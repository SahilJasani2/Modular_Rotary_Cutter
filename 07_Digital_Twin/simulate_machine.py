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
    def warning(cls, msg):
        print(f"{cls._get_timestamp()} | {cls.WARNING}WARNING{cls.ENDC:<8} | {msg}")

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
        # Safety Bridge Path
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
        """Robust recovery from sensor/material jam with state verification"""
        IndustrialLogger.fault("State: ABORTED (80) - Sensor Jam. Initiating Auto-Recovery sequence...")
        
        try:
            # 1. Clear blockage with verification
            IndustrialLogger.hmi("Step 1: Clearing material blockage...")
            self.plc.write_by_name(self.PATH_SENSOR, False, pyads.PLCTYPE_BOOL)
            time.sleep(1.0)
            
            # Verify sensor is cleared
            sensor_state = self.plc.read_by_name(self.PATH_SENSOR, pyads.PLCTYPE_BOOL)
            if sensor_state:
                IndustrialLogger.warning("Sensor still shows blockage - retrying...")
                self.plc.write_by_name(self.PATH_SENSOR, False, pyads.PLCTYPE_BOOL)
                time.sleep(0.5)
            
            # 2. Reset system with state verification
            IndustrialLogger.hmi("Step 2: Resetting machine (CLEARING -> STOPPED)...")
            self.plc.write_by_name(self.PATH_RESET, True, pyads.PLCTYPE_BOOL)
            
            # Wait for state transition
            reset_wait = 0
            while reset_wait < 10:  # Max 5 seconds wait
                current_state = self.plc.read_by_name(self.PATH_STATE, pyads.PLCTYPE_INT)
                if current_state == 90:  # CLEARING state
                    break
                reset_wait += 1
                time.sleep(0.5)
            
            # Wait for STOPPED state
            stopped_wait = 0
            while stopped_wait < 8:  # Max 4 seconds wait
                current_state = self.plc.read_by_name(self.PATH_STATE, pyads.PLCTYPE_INT)
                if current_state in [10, 20]:  # STOPPED or STARTING
                    break
                stopped_wait += 1
                time.sleep(0.5)
            
            # 3. Restart with verification
            IndustrialLogger.hmi("Step 3: Restarting machine (STARTING -> EXECUTE)...")
            self.plc.write_by_name(self.PATH_START, True, pyads.PLCTYPE_BOOL)
            
            # Verify execution state
            exec_wait = 0
            while exec_wait < 6:  # Max 3 seconds wait
                current_state = self.plc.read_by_name(self.PATH_STATE, pyads.PLCTYPE_INT)
                if current_state == 30:  # EXECUTE
                    break
                exec_wait += 1
                time.sleep(0.5)
            
            IndustrialLogger.success("Jam Recovery complete. Resuming simulation.")
            
        except Exception as e:
            IndustrialLogger.fault(f"Jam Recovery FAILED: {e}")
            raise

    def _recover_from_safety_trip(self):
        """Robust recovery from safety/E-stop with proper sequence verification"""
        IndustrialLogger.fault("State: ABORTING/ABORTED (70/80) - Safety violation detected.")
        
        try:
            # Wait for system to stabilize
            time.sleep(2.0)
            
            # 1. Restore safety circuit with verification
            IndustrialLogger.hmi("Step 1: Restoring Safety Circuit (bSafetyOk -> TRUE)...")
            self.plc.write_by_name(self.PATH_SAFETY, True, pyads.PLCTYPE_BOOL)
            time.sleep(1.0)
            
            # Verify safety is restored
            safety_state = self.plc.read_by_name(self.PATH_SAFETY, pyads.PLCTYPE_BOOL)
            if not safety_state:
                IndustrialLogger.warning("Safety circuit not restored - retrying...")
                self.plc.write_by_name(self.PATH_SAFETY, True, pyads.PLCTYPE_BOOL)
                time.sleep(0.5)
            
            # 2. Manual reset with state verification
            IndustrialLogger.hmi("Step 2: Manual Reset Required (CLEARING -> STOPPED)...")
            self.plc.write_by_name(self.PATH_RESET, True, pyads.PLCTYPE_BOOL)
            
            # Wait for state transition
            reset_wait = 0
            while reset_wait < 10:  # Max 5 seconds wait
                current_state = self.plc.read_by_name(self.PATH_STATE, pyads.PLCTYPE_INT)
                if current_state == 90:  # CLEARING state
                    break
                reset_wait += 1
                time.sleep(0.5)
            
            # Wait for STOPPED state
            stopped_wait = 0
            while stopped_wait < 8:  # Max 4 seconds wait
                current_state = self.plc.read_by_name(self.PATH_STATE, pyads.PLCTYPE_INT)
                if current_state in [10, 20]:  # STOPPED or STARTING
                    break
                stopped_wait += 1
                time.sleep(0.5)
            
            # 3. Restart with verification
            IndustrialLogger.hmi("Step 3: Restarting machine (STARTING -> EXECUTE)...")
            self.plc.write_by_name(self.PATH_START, True, pyads.PLCTYPE_BOOL)
            
            # Verify execution state
            exec_wait = 0
            while exec_wait < 6:  # Max 3 seconds wait
                current_state = self.plc.read_by_name(self.PATH_STATE, pyads.PLCTYPE_INT)
                if current_state == 30:  # EXECUTE
                    break
                exec_wait += 1
                time.sleep(0.5)
            
            IndustrialLogger.success("Safety Recovery complete. Resuming simulation.")
            
        except Exception as e:
            IndustrialLogger.fault(f"Safety Recovery FAILED: {e}")
            raise

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
        """Enhanced simulation with true stochastic chaos engineering"""
        self.connect()
        self.press_start()
        
        cycle_count = 0
        IndustrialLogger.info("Simulation Loop Running. Use Ctrl+C to terminate.")
        IndustrialLogger.info("Chaos Engineering Mode: ACTIVE (Randomized Fault Injection)")
        
        while True:
            try:
                state = self.plc.read_by_name(self.PATH_STATE, pyads.PLCTYPE_INT)
                
                if state == 30:  # EXECUTE
                    cycle_count += 1
                    
                    # =========================================================
                    # CHAOS ENGINEERING: True Stochastic Fault Injection
                    # =========================================================
                    chaos_factor = random.random()
                    
                    if chaos_factor <= 0.02: 
                        # 2% chance per cycle of catastrophic E-Stop
                        IndustrialLogger.warning(f"CHAOS EVENT: Safety Trip (2% probability hit)")
                        self.trigger_panic_stop()
                        
                    elif chaos_factor <= 0.15: 
                        # 13% chance per cycle of material jam
                        IndustrialLogger.warning(f"CHAOS EVENT: Material Jam (13% probability hit)")
                        self.inject_jam()
                        
                    else:
                        # 85% chance of perfectly normal run
                        self.run_normal_cycle(cycle_count)
                
                elif state == 70 or state == 80:  # ABORTING or ABORTED
                    # Check what caused the abort to run the right recovery
                    if not self.plc.read_by_name(self.PATH_SAFETY, pyads.PLCTYPE_BOOL):
                        IndustrialLogger.info("Detected Emergency Stop - Running Recovery...")
                        self._recover_from_safety_trip()
                    else:
                        IndustrialLogger.info("Detected Jam State - Running Recovery...")
                        self._recover_from_jam()
                        
                elif state == 90:  # CLEARING
                    # Ensure proper state transition
                    IndustrialLogger.info("Machine in CLEARING state - waiting for STOPPED...")
                    time.sleep(1.0)
                    
                else:
                    IndustrialLogger.info(f"Waiting for State 30 (Current: {state})...")
                    time.sleep(2.0)
                    
            except pyads.ADSError as ads_err:
                IndustrialLogger.fault(f"ADS Communication Error: {ads_err}")
                time.sleep(1.0)  # Brief delay before retry
                
            except Exception as e:
                IndustrialLogger.fault(f"Unexpected Error in Simulation Loop: {e}")
                time.sleep(1.0)

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