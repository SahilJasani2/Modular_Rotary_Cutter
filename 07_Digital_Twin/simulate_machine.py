import pyads
import time
import random

# ==============================================================================
# DIGITAL TWIN PHYSICS SIMULATION - RESTORED ENDLESS LOOP WITH AUTO-RECOVERY
# ==============================================================================

AMS_NET_ID = '199.4.42.250.1.1'
PLC_PORT = pyads.PORT_TC3PLC1

def run_simulation():
    print("--- Starting Industrial Rotary Cutter Digital Twin ---")
    
    plc = pyads.Connection(AMS_NET_ID, PLC_PORT)
    try:
        plc.open()
        print(f"[SUCCESS] Connected to TwinCAT PLC. State: {plc.read_state()}")
        
        # 1. Trigger the Start Button (Your original logic)
        print("[HMI] Pressing 'Start' Button...")
        plc.write_by_name("MAIN.RotaryCutter.bCmdStart", True, pyads.PLCTYPE_BOOL)
        time.sleep(1.0) 
        
        # 2. Main Simulation Loop (Restored to run endlessly)
        cycle_count = 0
        print("[SIMULATION] Conveyor physics loop running. Press Ctrl+C to stop.")
        
        while True:
            # Read current machine state (30 = EXECUTE, 99 = ERROR)
            state = plc.read_by_name("MAIN.RotaryCutter.eState", pyads.PLCTYPE_INT)
            
            if state == 30: # EXECUTE
                cycle_count += 1
                print(f"\n[PHYSICS] CYCLE {cycle_count}: Material feeding...")
                
                sensor_path = "MAIN.RotaryCutter.fbProductSensor.bRawInput"
                cmd_path = "MAIN.RotaryCutter.RotaryKnife.bSyncCommand"
                
                # --- NEW: Every 5th cycle, simulate a JAM ---
                if cycle_count % 5 == 0:
                    print(f"[FAULT] !!! MATERIAL JAM DETECTED !!! Holding sensor TRUE...")
                    plc.write_by_name(sensor_path, True, pyads.PLCTYPE_BOOL)
                    # Wait for PLC to detect it (PLC timer is 5s)
                    time.sleep(6.0) 
                    continue # Skip the rest of the loop to let the ERROR block handle it
                
                # --- YOUR ORIGINAL SENSOR LOGIC ---
                time.sleep(random.uniform(2.0, 4.0)) 
                print(f"[SENSOR] ---> Material Detected! (Path: {sensor_path})")
                plc.write_by_name(sensor_path, True, pyads.PLCTYPE_BOOL)
                time.sleep(0.1)
                
                # VERIFICATION 1 (Restored)
                if plc.read_by_name(cmd_path, pyads.PLCTYPE_BOOL):
                    print("   ✅ VERIFIED: Cut initiated!")
                
                time.sleep(0.6) 
                print("[SENSOR] ---> Material Passed.")
                plc.write_by_name(sensor_path, False, pyads.PLCTYPE_BOOL)
                time.sleep(0.1)
                
                # VERIFICATION 2 (Restored)
                if not plc.read_by_name(cmd_path, pyads.PLCTYPE_BOOL):
                    print("   ✅ VERIFIED: Ready for next cut.")

            elif state == 99: # ERROR
                print(f"\n[ALARM] Machine in ERROR state. Initiating Auto-Reset...")
                time.sleep(2.0)
                
                # Release the sensor first
                plc.write_by_name("MAIN.RotaryCutter.fbProductSensor.bRawInput", False, pyads.PLCTYPE_BOOL)
                
                # Trigger Reset and Restart (Your PLC logic handles the rest)
                plc.write_by_name("MAIN.RotaryCutter.bCmdReset", True, pyads.PLCTYPE_BOOL)
                time.sleep(1.0)
                plc.write_by_name("MAIN.RotaryCutter.bCmdStart", True, pyads.PLCTYPE_BOOL)
                print("[RECOVERY] Reset sent. Restarting machine...")
                
            else:
                # If machine is STOPPED or STARTING, just wait
                time.sleep(1)

    except Exception as e:
        print(f"\n[ERROR] ADS Communication failed: {e}")
    finally:
        plc.close()
        print("\n--- Connection Closed ---")

if __name__ == '__main__':
    run_simulation()