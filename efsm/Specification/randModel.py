import json
import random

def generate_json(states, transitions):
    data = []

    # MLS-BASED
    input_event_options = ["?U.input(qos);", ""]
    guard_options = ["uid <> ID1;", "uid = ID1;", "uid <> ID2;", "uid = ID2;", "uid = ID1 && pwd = PW1;",
                     "uid <> ID2 || pwd <> PW2;", ""]
    action_options = [
        f"uid := {random.randint(0, 1)}; ID1 := {random.randint(0, 5)}; ID2 := {random.randint(0, 4)}; pwd := {random.randint(0, 4)}; PW1 := {random.randint(0, 5)}; out := {random.randint(0, 5)};",
        f"out := {random.randint(0, 5)};", f"PW1 := {random.randint(0, 5)};", "PW1 := out;",
        "PW1 := qos;", "qos := qos - 1;", "", "", "", ""]
    output_event_options = ["!U.output(qos);", "!U.output(PW1);", "!U.output(out);", "", ""]

    for i in range(1, transitions + 1):
        trans_name = f"t{i}"
        h_state = f"id{random.randint(1, states)}"
        t_state = f"id{random.randint(1, states)}"
        input_event = random.choice(input_event_options)
        guard = random.choice(guard_options)
        action = random.choice(action_options)
        output_event = random.choice(output_event_options)

        transition_info = {
            "trans_name": trans_name,
            "h_state": h_state,
            "t_state": t_state,
            "input_event": input_event,
            "guard": guard,
            "action": action,
            "output_event": output_event
        }

        data.append(transition_info)

    return data


if __name__ == "__main__":
    num_states = 50             # !!!
    num_transitions = 100         # !!!

    json_data = generate_json(num_states, num_transitions)

    with open('RM1.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=2)
