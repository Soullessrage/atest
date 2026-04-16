def process_economy(state, payload):
    town_id = payload.get("town_id")
    delta = payload.get("gold_delta", 0)

    if town_id in state["towns"]:
        state["towns"][town_id]["gold"] += delta


def process_population(state, payload):
    town_id = payload.get("town_id")
    delta = payload.get("pop_delta", 0)

    if town_id in state["towns"]:
        state["towns"][town_id]["population"] += delta


def process_weather(state, payload):
    region_id = payload.get("region_id")
    new_weather = payload.get("new_weather")

    if region_id in state["regions"]:
        state["regions"][region_id]["weather"] = new_weather

def process_economy(state, payload):
    town_id = payload.get("town_id")
    delta = payload.get("gold_delta", 0)

    if town_id in state["towns"]:
        state["towns"][town_id]["gold"] += delta


def process_population(state, payload):
    town_id = payload.get("town_id")
    delta = payload.get("pop_delta", 0)

    if town_id in state["towns"]:
        state["towns"][town_id]["population"] += delta


def process_weather(state, payload):
    region_id = payload.get("region_id")
    new_weather = payload.get("new_weather")

    if region_id in state["regions"]:
        state["regions"][region_id]["weather"] = new_weather
