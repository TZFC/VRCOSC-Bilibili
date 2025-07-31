import json


def pretty_print_event(event: dict):
    return json.dumps(event, indent=4, ensure_ascii=False)
