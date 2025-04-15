import unrealsdk
import random
import json
import os
import configparser

from Mods.ModMenu import SDKMod, RegisterMod
from . import hotfixer

class TeleportRandomizer(SDKMod):
    Name = "TeleportRandomizer"
    Version = "0.1.0"
    Author = "Sebb"
    Description = "Randomizes all door destinations and spawn tags on game load."
    Types = unrealsdk.ModTypes.Utility

    def __init__(self):
        self.TeleportMap = {}
        self.StationLinkMap = {}
        self.Processed = False
        self.LastTravel = {}
        self.spawn_tag_lookup = {}

        self.seed = None
        try:
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
            self.seed = config.getint("Randomizer", "Seed", fallback=None)
            if self.seed is not None:
                random.seed(self.seed)
                unrealsdk.Log(f"[TeleportRandomizer] Seed loaded: {self.seed}")
            else:
                unrealsdk.Log("[TeleportRandomizer] No seed found, using random shuffle.")
        except Exception as e:
            unrealsdk.Log(f"[TeleportRandomizer] Failed to read config.ini: {e}")
        
        try:
            path = os.path.join(os.path.dirname(__file__), "PlayerStartTags.json")
            with open(path, "r") as f:
                self.spawn_tag_lookup = json.load(f)
                unrealsdk.Log(f"[TeleportRandomizer] Loaded {len(self.spawn_tag_lookup)} maps from PlayerStartTags.json")
        except Exception as e:
            unrealsdk.Log(f"[TeleportRandomizer] Failed to load PlayerStartTags.json: {e}")

    def Enable(self):
        self.Processed = False
        unrealsdk.RegisterHook("WillowGame.WillowHUD.CreateWeaponScopeMovie", "TeleportRandomizer_Init", self.InitTeleportHooks)
        unrealsdk.RegisterHook("WillowGame.TravelStationComponent.TravelToLevel", "TeleportRandomizer_Travel", self.OnTravel)
        unrealsdk.RegisterHook("WillowGame.LevelTravelStationDefinition.PostBeginPlay", "TeleportRandomizer_ReturnHook", self.OnReturnInit)

    def Disable(self):
        self.TeleportMap.clear()
        self.StationLinkMap.clear()
        self.LastTravel.clear()
        self.Processed = False
        unrealsdk.RemoveHook("WillowGame.WillowHUD.CreateWeaponScopeMovie", "TeleportRandomizer_Init")
        unrealsdk.RemoveHook("WillowGame.TravelStationComponent.TravelToLevel", "TeleportRandomizer_Travel")
        unrealsdk.RemoveHook("WillowGame.LevelTravelStationDefinition.PostBeginPlay", "TeleportRandomizer_ReturnHook")

    def InitTeleportHooks(self, caller, function, params):
        if self.Processed:
            return True

        all_doors = [
            obj for obj in unrealsdk.FindAll("WillowGame.LevelTravelStationDefinition")
            if hasattr(obj, "StationLevelName") and "_P" in obj.StationLevelName
        ]

        unrealsdk.Log(f"[TeleportRandomizer] Found {len(all_doors)} doors.")

        # Map shuffle
        maps = [d.StationLevelName for d in all_doors]
        shuffled_maps = maps.copy()
        random.shuffle(shuffled_maps)
        self.TeleportMap = dict(zip(maps, shuffled_maps))

        # Door pairing (bidirectional)
        shuffled_doors = all_doors.copy()
        random.shuffle(shuffled_doors)

        self.StationLinkMap = {}
        used = set()

        for a, b in zip(all_doors, shuffled_doors):
            if a in used or b in used or a == b:
                continue
            self.StationLinkMap[a] = b
            self.StationLinkMap[b] = a
            used.update((a, b))

        # Apply hotfixes
        for obj, paired in self.StationLinkMap.items():
            original = obj.StationLevelName
            new_map = self.TeleportMap.get(original, original)
            entrypoints = self.spawn_tag_lookup.get(new_map, ["Entrance"])
            new_point = random.choice(entrypoints)

            hotfixer.set_station_destination(obj, new_map, new_point)
            obj.DestinationStationDefinition = paired
            unrealsdk.Log(f"[TeleportRandomizer] {obj.Name} now links to {paired.Name}")

        self.Processed = True
        return True

    def OnTravel(self, caller, function, params):
        try:
            obj = caller.Owner
            if obj and hasattr(obj, "StationLevelName"):
                self.LastTravel = {
                    "map": obj.StationLevelName,
                    "point": getattr(obj, "TravelToPointName", "Entrance")
                }
                unrealsdk.Log(f"[TeleportRandomizer] Stored travel from {self.LastTravel['map']} @ {self.LastTravel['point']}")
        except Exception as e:
            unrealsdk.Log(f"[TeleportRandomizer] Travel hook error: {e}")
        return True

    def SimulateReturn(self, obj):
        if self.LastTravel:
            original = obj.StationLevelName
            new_map = self.LastTravel["map"]
            point_name = self.LastTravel["point"]
            hotfixer.set_station_destination(obj, new_map, point_name)
            unrealsdk.Log(f"[TeleportRandomizer] Simulated return: {original} -> {new_map} @ {point_name}")

    def OnReturnInit(self, caller, function, params):
        try:
            self.SimulateReturn(caller)
        except Exception as e:
            unrealsdk.Log(f"[TeleportRandomizer] Return simulation error: {e}")
        return True

mod = TeleportRandomizer()
RegisterMod(mod)