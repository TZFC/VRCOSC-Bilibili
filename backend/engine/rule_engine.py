import logging
import math

from database import Rule, Session, engine, AppConfig
from engine.osc_manager import osc_manager
from sqlmodel import select

logger = logging.getLogger(__name__)


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
    
    right = [
        cy * cr + sy * sp * sr,
        cp * sr,
        -sy * cr + cy * sp * sr
    ]
    
    up = [
        -cy * sr + sy * sp * cr,
        cp * cr,
        sy * sr + cy * sp * cr
    ]
    
    forward = [
        sy * cp,
        -sp,
        cy * cp
    ]
    
    return right, up, forward


class RuleEngine:
    def __init__(self):
        self.rules = []
        self.current_camera_pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def reload_rules(self):
        with Session(engine) as session:
            self.rules = session.exec(select(Rule).where(Rule.enabled == True)).all()
        logger.info(f"Loaded {len(self.rules)} active rules")

    def process_bili_event(self, event_type: str, data: dict):
        if event_type == "Danmaku":
            msg = data.get("message", "").strip().lower()
            with Session(engine) as session:
                config = session.exec(select(AppConfig)).first()
            if config:
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

        for rule in self.rules:
            if rule.event_type != event_type:
                continue

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
                pass

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
        x, y, z, pitch, yaw, roll = self.current_camera_pose
        right, up, forward = get_camera_axes(pitch, yaw, roll)
        
        step_move_x = config.camera_move_x_step
        step_move_y = config.camera_move_y_step
        step_move_z = config.camera_move_z_step
        step_rot_x = config.camera_rotate_x_step
        step_rot_y = config.camera_rotate_y_step
        step_rot_z = config.camera_rotate_z_step
        
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
            
        pitch = max(-89.9, min(89.9, pitch))
        yaw = (yaw + 180) % 360 - 180
        roll = (roll + 180) % 360 - 180
        
        new_pose = [x, y, z, pitch, yaw, roll]
        self.current_camera_pose = new_pose
        
        osc_manager.send_message("/usercamera/Pose", new_pose)
        logger.info(f"Camera control applied: {cmd} -> new pose: {[round(v, 3) for v in new_pose]}")

    def on_osc_message_received(self, address: str, *args):
        if not args:
            return
            
        # Special handling for camera pose feedback to keep tracked coordinates synchronized
        # with manual changes in VRChat (respect manual overrides).
        if address == "/usercamera/Pose":
            if len(args) >= 6:
                self.current_camera_pose = [float(arg) for arg in args[:6]]
                logger.debug(f"Updated current camera pose from VRChat: {self.current_camera_pose}")
            return

        value = args[0]

        if osc_manager.is_echo(address, value):
            logger.debug(
                f"OSC echo ignored for {address} = {value}"
            )
            return

        governing_rules = [r for r in self.rules if r.osc_endpoint == address]

        if not governing_rules:
            osc_manager.intended_state[address] = value
            logger.debug(
                f"OSC received (ungoverned): {address} = {value}"
            )
            return

        sync_mode = governing_rules[0].sync_mode

        if sync_mode == "Respect":
            # Future Toggle/Add actions will continue from the user's manual change value.
            old_value = osc_manager.intended_state.get(address)
            osc_manager.intended_state[address] = value
            logger.info(
                f"[Respect] User changed {address}: {old_value} → {value}. "
                f"Automation will continue from new value."
            )
        else:
            intended = osc_manager.intended_state.get(address)
            if intended is not None and intended != value:
                logger.info(
                    f"[Overwrite] User changed {address} to {value}, "
                    f"but app intended {intended}. Restoring."
                )
                osc_manager.send_message(address, intended)
            else:
                osc_manager.intended_state[address] = value
                logger.debug(
                    f"[Overwrite] No conflict for {address} = {value}"
                )


rule_engine = RuleEngine()
