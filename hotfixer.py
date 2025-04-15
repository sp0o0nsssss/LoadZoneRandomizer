import unrealsdk

def console_command(cmd: str) -> None:
    try:
        # Avoid SDK errors if it's not fully available
        if not hasattr(unrealsdk, "RunCommand"):
            return  # Just silently skip the command

        unrealsdk.RunCommand(cmd)
    except Exception as e:
        unrealsdk.Log(f"[TeleportRandomizer] Console error: {e}")

def set_station_destination(obj, new_map, point_name):
    try:
        path = obj.PathName(obj)
        console_command(f"set {path} StationLevelName {new_map}")
        console_command(f"set {path} TravelToPointName {point_name}")
        console_command(f"set {path} PlayerStartTag {point_name}")
        unrealsdk.Log(f"[TeleportRandomizer] HOTFIX: {path} → {new_map} @ {point_name}")
    except Exception as e:
        unrealsdk.Log(f"[TeleportRandomizer] Failed to hotfix: {e}")

def set_destination_station(obj, new_destination_path):
    try:
        path = obj.PathName(obj)
        console_command(f"set {path} DestinationStationDefinition {new_destination_path}")
        unrealsdk.Log(f"[TeleportRandomizer] DESTINATION PATCHED: {path} → {new_destination_path}")
    except Exception as e:
        unrealsdk.Log(f"[TeleportRandomizer] Failed to set destination: {e}")