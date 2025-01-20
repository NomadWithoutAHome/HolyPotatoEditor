import clr
from System import Int32, Double, Convert

clr.AddReference('System')


def serialize_json(obj, in_game_data=False):
    """Serialize JSON in the same format as LitJson.JsonMapper"""
    if isinstance(obj, dict):
        items = sorted(obj.items())
        parts = []
        for key, value in items:
            key_str = f'"{key}"'
            value_str = serialize_json(
                value,
                in_game_data=(in_game_data or key == "value")
            )
            parts.append(f"{key_str}:{value_str}")
        return "{" + ",".join(parts) + "}"
    elif isinstance(obj, (list, tuple)):
        return "[" + ",".join(
            serialize_json(x, in_game_data) for x in obj
        ) + "]"
    elif isinstance(obj, bool):
        if in_game_data:
            return f'"{Convert.ToString(obj)}"'
        else:
            return "true" if obj else "false"
    elif isinstance(obj, int):
        if in_game_data:
            return f'"{Int32(obj).ToString()}"'
        else:
            return str(obj)
    elif isinstance(obj, float):
        if in_game_data:
            return f'"{Double(obj).ToString()}"'
        else:
            return str(obj)
    elif obj is None:
        return "null"
    else:
        return f'"{str(obj).replace('"', '\\"')}"' 