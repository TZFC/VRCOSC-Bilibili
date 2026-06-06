import logging

from database import Rule, Session, engine
from engine.osc_manager import osc_manager
from sqlmodel import select

logger = logging.getLogger(__name__)


class RuleEngine:
    def __init__(self):
        # Cache rules in memory for fast evaluation
        self.rules = []
        self.reload_rules()

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
            elif event_type == "Guard" or event_type == "Enter":
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

        osc_manager.send_message(addr, val)

    def on_osc_message_received(self, address: str, *args):
        """Called when user manually changes a parameter in VRChat."""
        if not args:
            return
        value = args[0]

        # Find if this address is governed by any rule
        # If it is, check its sync_mode
        governing_rules = [r for r in self.rules if r.osc_endpoint == address]

        if governing_rules:
            # For simplicity, use the sync_mode of the first governing rule
            sync_mode = governing_rules[0].sync_mode

            if sync_mode == "Overwrite":
                intended = osc_manager.intended_state.get(address)
                if intended is not None and intended != value:
                    logger.info(
                        f"OSC state conflict for {address}: App({intended}) != VRChat({value}). Overwriting VRChat."
                    )
                    osc_manager.send_message(address, intended)
            else:  # Respect
                logger.debug(f"Respecting manual change for {address} -> {value}")
                osc_manager.intended_state[address] = value


rule_engine = RuleEngine()
