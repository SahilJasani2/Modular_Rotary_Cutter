import pyads
import time
import random
from datetime import datetime

# ==============================================================================
# INDUSTRIAL LOGGING ENGINE (Tech Lead Level)
# ==============================================================================
class IndustrialLogger:
    """Handles professional CLI output with timestamps and colors."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    @staticmethod
    def _get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    @classmethod
    def info(cls, msg):
        print(f"{cls._get_timestamp()} | {cls.OKBLUE}INFO{cls.ENDC:<8} | {msg}")

    @classmethod
    def success(cls, msg):
        print(f"{cls._get_timestamp()} | {cls.OKGREEN}SUCCESS{cls.ENDC:<8} | {msg}")

    @classmethod
    def fault(cls, msg):
        print(f"{cls._get_timestamp()} | {cls.FAIL}FAULT{cls.ENDC:<8} | {msg}")

    @classmethod
    def hmi(cls, msg):
        print(f"{cls._get_timestamp()} | {cls.HEADER}HMI{cls.ENDC:<8} | {msg}")

# ==============================================================================
# DIGITAL TWIN PHYSICS SIMULATION - MODULAR & PROFESSIONAL
# ==============================================================================

class RotaryCutterTwin:
    def __init__(self, ams_id, port):
        self.ams_id = ams_id
        self.port = port
        self.plc = pyads.Connection(ams_id, port)
        
        # Paths preserved 100% from your project
        self.PATH_START   = "MAIN.RotaryCutter.bCmdStart"
        self.PATH_RESET   = "MAIN.RotaryCutter.bCmdReset"
        self.PATH_STATE   = "MAIN.RotaryCutter.eState"
        self.PATH_SENSOR  = "MAIN.RotaryCutter.fbProductSensor.bRawInput"
        self.PATH_CHOP    = "MAIN.RotaryCutter.RotaryKnife.bSyncCommand"
        # NEW: Safety Bridge Path
        self.PATH_SAFETY  = "GVL_Safety.bSafetyOk"

    def connect(self):
        self.plc.open()
        # Initialize Safety to TRUE so the machine can start
        self.plc.write_by_name(self.PATH_SAFETY, True, pyads.PLCTYPE_BOOL)
        IndustrialLogger.success(f"ADS Connection Established & Safety OK. NetID: {self.ams_id}")

    def press_start(self):
        IndustrialLogger.hmi("Operator pressed 'Start'. Syncing with PLC...")
        self.plc.write_by_name(self.PATH_START, True, pyads.PLCTYPE_BOOL)
        time.sleep(1.0)

    def _recover_from_jam(self):
        IndustrialLogger.fault("State: ERROR (99). Initiating Auto-Recovery sequence...")
        # 1. Clear blockage
        self.plc.write_by_name(self.PATH_SENSOR, False, pyads.PLCTYPE_BOOL)
        time.sleep(1.0)
        # 2. Reset
        self.plc.write_by_name(self.PATH_RESET, True, pyads.PLCTYPE_BOOL)
        time.sleep(1.0)
        # 3. Restart
        self.plc.write_by_name(self.PATH_START, True, pyads.PLCTYPE_BOOL)
        IndustrialLogger.success("Jam Recovery complete. Resuming simulation.")

    def _recover_from_safety_trip(self):
        IndustrialLogger.fault("State: EMERGENCY_STOP (100). Safety violation detected.")
        time.sleep(2.0)
        # 1. Simulate "Pulling out the E-Stop button"
        IndustrialLogger.hmi("Restoring Safety Circuit (bSafetyOk -> TRUE)...")
        self.plc.write_by_name(self.PATH_SAFETY, True, pyads.PLCTYPE_BOOL)
        time.sleep(1.0)
        # 2. Manual Reset Required
        self.plc.write_by_name(self.PATH_RESET, True, pyads.PLCTYPE_BOOL)
        time.sleep(1.0)
        # 3. Restart
        self.plc.write_by_name(self.PATH_START, True, pyads.PLCTYPE_BOOL)
        IndustrialLogger.success("Safety Recovery complete. Resuming simulation.")

    def run_normal_cycle(self, cycle_num):
        IndustrialLogger.info(f"CYCLE {cycle_num}: Conveyor active. Material in transit...")
        time.sleep(random.uniform(2.0, 4.0)) 
        
        IndustrialLogger.info(f"---> Material Detected! (Path: {self.PATH_SENSOR})")
        self.plc.write_by_name(self.PATH_SENSOR, True, pyads.PLCTYPE_BOOL)
        time.sleep(0.1)
        
        if self.plc.read_by_name(self.PATH_CHOP, pyads.PLCTYPE_BOOL):
            IndustrialLogger.success("VERIFIED: PLC responded with 'bSyncCommand = TRUE'.")
        else:
            IndustrialLogger.fault("VERIFICATION FAILED: No Sync Command detected.")
        
        time.sleep(0.6) 
        IndustrialLogger.info("---> Material Passed.")
        self.plc.write_by_name(self.PATH_SENSOR, False, pyads.PLCTYPE_BOOL)
        time.sleep(0.1)
        
        if not self.plc.read_by_name(self.PATH_CHOP, pyads.PLCTYPE_BOOL):
            IndustrialLogger.success("VERIFIED: PLC released Sync Command.")

    def inject_jam(self):
        IndustrialLogger.fault("INJECTING PROCESS FAULT: Material Jam.")
        self.plc.write_by_name(self.PATH_SENSOR, True, pyads.PLCTYPE_BOOL)
        IndustrialLogger.info("Waiting for PLC Alarm detection (5.0s logic)...")
        time.sleep(6.0)

    def trigger_panic_stop(self):
        IndustrialLogger.fault("!!! TRIGGERING PANIC TEST: E-STOP PRESSED !!!")
        self.plc.write_by_name(self.PATH_SAFETY, False, pyads.PLCTYPE_BOOL)
        time.sleep(3.0)

    def start_simulation(self):
        self.connect()
        self.press_start()
        
        cycle_count = 0
        IndustrialLogger.info("Simulation Loop Running. Use Ctrl+C to terminate.")
        
        while True:
            state = self.plc.read_by_name(self.PATH_STATE, pyads.PLCTYPE_INT)
            
            if state == 30: # EXECUTE
                cycle_count += 1
                # Panic test every 7 cycles, Jam test every 5
                if cycle_count % 7 == 0:
                    self.trigger_panic_stop()
                elif cycle_count % 5 == 0:
                    self.inject_jam()
                else:
                    self.run_normal_cycle(cycle_count)
            
            elif state == 99: # ERROR (Jam)
                self._recover_from_jam()
                
            elif state == 100: # EMERGENCY_STOP
                self._recover_from_safety_trip()
            
            else:
                IndustrialLogger.info(f"Waiting for State 30 (Current: {state})...")
                time.sleep(2)

# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == '__main__':
    twin = RotaryCutterTwin('199.4.42.250.1.1', pyads.PORT_TC3PLC1)
    try:
        twin.start_simulation()
    except KeyboardInterrupt:
        print("\n")
        IndustrialLogger.hmi("User requested shutdown.")
    except Exception as e:
        IndustrialLogger.fault(f"ADS Communication Breakdown: {e}")
    finally:
        twin.plc.close()
        print("--- Digital Twin Disconnected ---")