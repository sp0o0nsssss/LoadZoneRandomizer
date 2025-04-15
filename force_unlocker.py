import unrealsdk

def discover_all_doors():
    for obj in unrealsdk.FindAll("LevelTravelStationDefinition"):
        try:
            obj.bIsDiscovered = True
            unrealsdk.Log(f"[Discovery] Unlocked {obj.PathName(obj)}")
        except:
            pass

unrealsdk.RegisterHook("WillowGame.WillowHUD.PostBeginPlay", "UnlockLevelTravelDoors", lambda caller, function, params: discover_all_doors() or True)