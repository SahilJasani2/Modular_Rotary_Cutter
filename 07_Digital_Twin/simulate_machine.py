import pyads
import time
import random

# ==============================================================================
# DIGITAL TWIN PHYSICS SIMULATION - CLOSED LOOP VERIFICATION
# ==============================================================================

AMS_NET_ID = '199.4.42.250.1.1'
PLC_PORT = pyads.PORT_TC3PLC1

def run_simulation():
    print("--- Starting Industrial Rotary Cutter Digital Twin ---")
    
    plc = pyads.Connection(AMS_NET_ID, PLC_PORT)
    try:
        plc.open()
        print(f"[SUCCESS] Connected to TwinCAT PLC. State: {plc.read_state()}")
        
        # 1. Trigger the Start Button
        # Path verified: MAIN -> RotaryCutter -> bCmdStart
        print("[HMI] Pressing 'Start' Button...")
        plc.write_by_name("MAIN.RotaryCutter.bCmdStart", True, pyads.PLCTYPE_BOOL)
        time.sleep(1.0) 
        
        # 2. Main Simulation Loop
        print("[SIMULATION] Conveyor physics loop running. Press Ctrl+C to stop.")
        while True:
            # Read current machine state (30 = EXECUTE)
            state = plc.read_by_name("MAIN.RotaryCutter.eState", pyads.PLCTYPE_INT)
            
            if state == 30: 
                print("\n[PHYSICS] Conveyor is moving. Material is feeding...")
                
                # Wait for material to reach the sensor
                time.sleep(random.uniform(2.0, 4.0)) 
                
                # TRIGGER THE SENSOR 
                # Updated Path: MAIN -> RotaryCutter -> fbProductSensor -> bRawInput
                sensor_path = "MAIN.RotaryCutter.fbProductSensor.bRawInput"
                cmd_path = "MAIN.RotaryCutter.RotaryKnife.bSyncCommand"
                
                print(f"[SENSOR] ---> Material Detected! (Path: {sensor_path})")
                plc.write_by_name(sensor_path, True, pyads.PLCTYPE_BOOL)
                
                # Give the PLC a fraction of a second to run its cycle and react
                time.sleep(0.1)
                
                # VERIFICATION 1: Read the chop command back from the PLC
                did_it_chop = plc.read_by_name(cmd_path, pyads.PLCTYPE_BOOL)
                if did_it_chop:
                    print("   ✅ VERIFIED: PLC responded with 'bSyncCommand = TRUE'. Cut initiated!")
                else:
                    print("   ❌ ERROR: No cut command received from PLC.")
                
                # Simulated width of the workpiece (the rest of the material passes)
                time.sleep(0.6) 
                
                print("[SENSOR] ---> Material Passed.")
                plc.write_by_name(sensor_path, False, pyads.PLCTYPE_BOOL)
                
                # Give the PLC a fraction of a second to run its cycle and react
                time.sleep(0.1)
                
                # VERIFICATION 2: Check if the PLC turned the chop command off
                is_chopping = plc.read_by_name(cmd_path, pyads.PLCTYPE_BOOL)
                if not is_chopping:
                    print("   ✅ VERIFIED: PLC responded with 'bSyncCommand = FALSE'. Ready for next cut.")
                else:
                    print("   ❌ ERROR: Knife is still locked!")
                
            else:
                print(f"[STATUS] Current State: {state} (Waiting for EXECUTE/30...)")
                time.sleep(2)

    except Exception as e:
        print(f"\n[ERROR] ADS Communication failed: {e}")
    finally:
        plc.close()
        print("\n--- Connection Closed ---")

if __name__ == '__main__':
    run_simulation()