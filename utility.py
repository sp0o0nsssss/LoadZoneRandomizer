import sys
import types

def run_console_command(command: str, bWriteToLog: bool = False) -> None:
    try:
        sdk = sys.modules.get("unrealsdk")
        if isinstance(sdk, types.ModuleType) and hasattr(sdk, "RunCommand"):
            sdk.RunCommand(command)
            if bWriteToLog:
                sdk.Log(f"[ConsoleRunner] Ran: {command}")
        else:
            print(f"[ConsoleRunner] unrealsdk.RunCommand not available — SDK not initialized?")
    except Exception as e:
        try:
            sdk = sys.modules.get("unrealsdk")
            if sdk and hasattr(sdk, "Log"):
                sdk.Log(f"[ConsoleRunner] Failed: {command} → {e}")
            else:
                print(f"[ConsoleRunner] Failed: {command} → {e}")
        except:
            pass  # Failsafe fallback
