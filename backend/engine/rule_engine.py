import logging
import math

from database import Rule, Session, engine, AppConfig
from engine.osc_manager import osc_manager
from sqlmodel import select

logger = logging.getLogger(__name__)


# Dictionary mapping camera commands to English/Chinese danmaku keywords
CAMERA_COMMANDS = {
    "rotate_left": ["rotate left", "向左旋转", "左旋"],
    "rotate_right": ["rotate right", "向右旋转", "右旋"],
    "tilt_up": ["tilt up", "向上倾斜", "仰角", "抬头"],
    "tilt_down": ["tilt down", "向下倾斜", "俯角", "低头"],
    "pivot_left": ["pivot left", "向左偏转", "左偏", "左转"],
    "pivot_right": ["pivot right", "向右偏转", "右偏", "右转"],
    "move_left": ["move left", "向左移动", "左移"],
    "move_right": ["move right", "向右移动", "右移"],
    "move_up": ["move up", "向上移动", "上移"],
    "move_down": ["move down", "向下移动", "下移"],
    "move_forward": ["move forward", "向前移动", "前移", "前进"],
    "move_backward": ["move backward", "向后移动", "后移", "后退"],
}


def get_camera_axes(pitch_deg: float, yaw_deg: float, roll_deg: float):
    """Calculate local coordinate axis vectors (Right, Up, Forward) in world space
    based on Unity's left-handed coordinate system and ZXY Euler rotation order.
    
    Coordinate System:
      - Position (X, Y, Z in meters): +X = Right, +Y = Up, +Z = Forward.
      - Rotation (Pitch, Yaw, Roll in degrees): ZXY order.
        +X = Pitch down, +Y = Yaw right, +Z = Roll left.
    """
    p = math.radians(pitch_deg)
    y = math.radians(yaw_deg)
    r = math.radians(roll_deg)
    
    cy = math.cos(y)
    sy = math.sin(y)
    cp = math.cos(p)
    sp = math.sin(p)
    cr = math.cos(r)
    sr = math.sin(r)
    
    # Right vector (local X axis direction in world coordinates)
    right = [
        cy * cr + sy * sp * sr,
        cp * sr,
        -sy * cr + cy * sp * sr
    ]
    
    # Up vector (local Y axis direction in world coordinates)
    up = [
        -cy * sr + sy * sp * cr,
        cp * cr,
        sy * sr + cy * sp * cr
    ]
    
    # Forward vector (local Z axis direction in world coordinates)
    forward = [
        sy * cp,
        -sp,
        cy * cp
    ]
    
    return right, up, forward


class RuleEngine:
    def __init__(self):
        # Cache rules in memory for fast evaluation
        self.rules = []
        
        # Track current camera pose: [x, y, z, pitch, yaw, roll]
        # Updated via VRChat OSC broadcasts on port 9001
        self.current_camera_pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def reload_rules(self):
        with Session(engine) as session:
            self.rules = session.exec(select(Rule).where(Rule.enabled == True)).all()
        logger.info(f"Loaded {len(self.rules)} active rules")

    def process_bili_event(self, event_type: str, data: dict):
        """Evaluate a bilibili event against all rules and check for camera commands."""
        # 1. Parse danmaku messages for camera control keywords
        if event_type == "Danmaku":
            msg = data.get("message", "").strip().lower()
            with Session(engine) as session:
                config = session.exec(select(AppConfig)).first()
            if config:
                # Dynamically construct command keywords from config
                dynamic_commands = {
                    "rotate_left": [k.strip().lower() for k in getattr(config, "camera_kw_rotate_left", "").split(",") if k.strip()],
                    "rotate_right": [k.strip().lower() for k in getattr(config, "camera_kw_rotate_right", "").split(",") if k.strip()],
                    "tilt_up": [k.strip().lower() for k in getattr(config, "camera_kw_tilt_up", "").split(",") if k.strip()],
                    "tilt_down": [k.strip().lower() for k in getattr(config, "camera_kw_tilt_down", "").split(",") if k.strip()],
                    "pivot_left": [k.strip().lower() for k in getattr(config, "camera_kw_pivot_left", "").split(",") if k.strip()],
                    "pivot_right": [k.strip().lower() for k in getattr(config, "camera_kw_pivot_right", "").split(",") if k.strip()],
                    "move_left": [k.strip().lower() for k in getattr(config, "camera_kw_move_left", "").split(",") if k.strip()],
                    "move_right": [k.strip().lower() for k in getattr(config, "camera_kw_move_right", "").split(",") if k.strip()],
                    "move_up": [k.strip().lower() for k in getattr(config, "camera_kw_move_up", "").split(",") if k.strip()],
                    "move_down": [k.strip().lower() for k in getattr(config, "camera_kw_move_down", "").split(",") if k.strip()],
                    "move_forward": [k.strip().lower() for k in getattr(config, "camera_kw_move_forward", "").split(",") if k.strip()],
                    "move_backward": [k.strip().lower() for k in getattr(config, "camera_kw_move_backward", "").split(",") if k.strip()],
                }
                
                matched_cmd = None
                for cmd, keywords in dynamic_commands.items():
                    for kw in keywords:
                        if kw in msg:
                            matched_cmd = cmd
                            break
                    if matched_cmd:
                        break
                        
                if matched_cmd:
                    self.handle_camera_command(matched_cmd, config)

        # 2. Continue with standard rule evaluation
        for rule in self.rules:
            if rule.event_type != event_type:
                continue

            # Evaluate conditions
            matched = False
            if event_type == "Danmaku":
                msg = data.get("message", "")
                if rule.condition_keyword and rule.condition_keyword in msg:
                    matched = True
            elif event_type == "Gift":
                price = data.get("price", 0.0)
                if price >= rule.condition_min_value:
                    matched = True
            elif event_type == "SC":
                price = data.get("price", 0.0)
                if price >= rule.condition_min_value:
                    matched = True
            elif event_type in ("Guard", "Enter"):
                matched = True

            if matched:
                self.execute_action(rule)

    def execute_action(self, rule: Rule):
        addr = rule.osc_endpoint
        val = rule.action_value

        # Convert string value to proper type
        if val.lower() == "true":
            val = True
        elif val.lower() == "false":
            val = False
        else:
            try:
                if "." in val:
                    val = float(val)
                else:
                    val = int(val)
            except ValueError:
                pass  # keep as string

        # Handle action type (Set, Toggle, Add)
        if rule.action_type == "Toggle":
            current_val = osc_manager.intended_state.get(addr, False)
            val = not bool(current_val)
        elif rule.action_type == "Add":
            current_val = osc_manager.intended_state.get(addr, 0)
            val = float(current_val) + float(val)

        # Conform /chatbox/input to VRChat OSC guidelines: https://wiki.vrchat.com/wiki/OSC#Chatbox
        # It requires: /chatbox/input s b b (text: string, send: bool, playSFX: bool)
        if addr == "/chatbox/input":
            osc_manager.send_message(addr, [str(val), True, True])
        else:
            osc_manager.send_message(addr, val)

    def handle_camera_command(self, cmd: str, config: AppConfig):
        """Execute a relative camera transformation based on the matched command
        and the step configurations. Re-projects local translation steps to world coordinates.
        """
        x, y, z, pitch, yaw, roll = self.current_camera_pose
        
        # Calculate coordinate axes (in world space) relative to current camera angles
        right, up, forward = get_camera_axes(pitch, yaw, roll)
        
        # Load configuration step sizes (6 DOF)
        step_move_x = config.camera_move_x_step
        step_move_y = config.camera_move_y_step
        step_move_z = config.camera_move_z_step
        step_rot_x = config.camera_rotate_x_step
        step_rot_y = config.camera_rotate_y_step
        step_rot_z = config.camera_rotate_z_step
        
        # Apply translation/rotation updates
        if cmd == "move_left":
            x -= step_move_x * right[0]
            y -= step_move_x * right[1]
            z -= step_move_x * right[2]
        elif cmd == "move_right":
            x += step_move_x * right[0]
            y += step_move_x * right[1]
            z += step_move_x * right[2]
        elif cmd == "move_up":
            x += step_move_y * up[0]
            y += step_move_y * up[1]
            z += step_move_y * up[2]
        elif cmd == "move_down":
            x -= step_move_y * up[0]
            y -= step_move_y * up[1]
            z -= step_move_y * up[2]
        elif cmd == "move_forward":
            x += step_move_z * forward[0]
            y += step_move_z * forward[1]
            z += step_move_z * forward[2]
        elif cmd == "move_backward":
            x -= step_move_z * forward[0]
            y -= step_move_z * forward[1]
            z -= step_move_z * forward[2]
        elif cmd == "tilt_up":
            pitch -= step_rot_x
        elif cmd == "tilt_down":
            pitch += step_rot_x
        elif cmd == "pivot_left":
            yaw -= step_rot_y
        elif cmd == "pivot_right":
            yaw += step_rot_y
        elif cmd == "rotate_left":
            roll += step_rot_z
        elif cmd == "rotate_right":
            roll -= step_rot_z
            
        # Normalize pitch to prevent gimbal lock / flip over
        pitch = max(-89.9, min(89.9, pitch))
        # Normalize yaw and roll to [-180, 180] range
        yaw = (yaw + 180) % 360 - 180
        roll = (roll + 180) % 360 - 180
        
        new_pose = [x, y, z, pitch, yaw, roll]
        self.current_camera_pose = new_pose
        
        # Send new pose to VRChat via port 9000
        osc_manager.send_message("/usercamera/Pose", new_pose)
        logger.info(f"Camera control applied: {cmd} -> new pose: {[round(v, 3) for v in new_pose]}")

    def on_osc_message_received(self, address: str, *args):
        """Called when VRChat broadcasts a parameter value on port 9001."""
        if not args:
            return
            
        # Special handling for VRChat Camera Pose update (read-write pose feedback)
        # Keeps our local tracked pose directly in sync with VRChat, making sure
        # manual overrides (e.g. user moving camera in game) are immediately respected.
        if address == "/usercamera/Pose":
            if len(args) >= 6:
                self.current_camera_pose = [float(arg) for arg in args[:6]]
                logger.debug(f"Updated current camera pose from VRChat: {self.current_camera_pose}")
            return

        value = args[0]

        # Ignore echoes of our own sent messages for standard parameter rules
        if osc_manager.is_echo(address, value):
            logger.debug(
                f"OSC echo ignored for {address} = {value}"
            )
            return

        # --- Genuine user-initiated change detected ---

        # Find if this address is governed by any rule
        governing_rules = [r for r in self.rules if r.osc_endpoint == address]

        if not governing_rules:
            # No rules govern this address; just track the value for reference
            osc_manager.intended_state[address] = value
            logger.debug(
                f"OSC received (ungoverned): {address} = {value}"
            )
            return

        # Use the sync_mode of the first governing rule for this address.
        sync_mode = governing_rules[0].sync_mode

        if sync_mode == "Respect":
            # Accept the user's manual change. Future Toggle/Add actions will
            # use this new value as their base because they read from
            # intended_state.
            old_value = osc_manager.intended_state.get(address)
            osc_manager.intended_state[address] = value
            logger.info(
                f"[Respect] User changed {address}: {old_value} → {value}. "
                f"Automation will continue from new value."
            )
        else:  # Overwrite
            intended = osc_manager.intended_state.get(address)
            if intended is not None and intended != value:
                logger.info(
                    f"[Overwrite] User changed {address} to {value}, "
                    f"but app intended {intended}. Restoring."
                )
                osc_manager.send_message(address, intended)
            else:
                # No conflict (we haven't set this address yet, or values match)
                osc_manager.intended_state[address] = value
                logger.debug(
                    f"[Overwrite] No conflict for {address} = {value}"
                )


rule_engine = RuleEngine()
