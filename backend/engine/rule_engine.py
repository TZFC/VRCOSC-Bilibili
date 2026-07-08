import logging

from database import Rule, Session, engine
from engine.osc_manager import osc_manager
from sqlmodel import select

logger = logging.getLogger(__name__)


class RuleEngine:
    def __init__(self):
        # Cache rules in memory for fast evaluation
        self.rules = []

    def reload_rules(self):
        with Session(engine) as session:
            self.rules = session.exec(select(Rule).where(Rule.enabled == True)).all()
        logger.info(f"Loaded {len(self.rules)} active rules")

    def process_bili_event(self, event_type: str, data: dict):
        """Evaluate a bilibili event against all rules."""
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

    def on_osc_message_received(self, address: str, *args):
        """Called when VRChat broadcasts a parameter value on port 9001.

        This fires for *every* parameter change, including echoes of values
        that we ourselves just sent.  We use osc_manager.is_echo() to
        distinguish genuine user-initiated changes (via the in-game radial
        menu or expressions menu) from echoes of our own automation.
        """
        if not args:
            return
        value = args[0]

        # Ignore echoes of our own sent messages
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
        # (All rules sharing the same address should ideally share the same
        # sync_mode, but we take the first as authoritative.)
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
