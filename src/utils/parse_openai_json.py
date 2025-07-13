import json


def parse_openai_json(json_str: str) -> dict:
    json_str = json_str.strip()
    json_str = json_str.replace("```json", "").replace("```", "")
    print(json_str)  # Debugging line to see the JSON string
    return json.loads(json_str)
