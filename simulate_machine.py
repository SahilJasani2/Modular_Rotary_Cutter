import pyads
import time
import random

# ==============================================================================
# DIGITAL TWIN PHYSICS SIMULATION
# This script bridges the gap between the IT environment and the Real-Time PLC.
# It uses the Beckhoff ADS protocol to simulate physical workpieces moving 
# down the Infeed Conveyor and triggering the Digital Photo-Eye.
# ==============================================================================

# TwinCAT 3 Local AMS NetID and standard PLC Port (851)
AMS_NET_ID = '127.0.0.1.1.1'
PLC_PORT = pyads.PORT_TC3PLC1

def run_simulation():
    print("--- Starting Flying Shear / Rotary Cutter Digital Twin ---")
    
    # 1. Open Connection to the PLC
    plc = pyads.Connection(AMS_NET_ID, PLC_PORT)
    try:
        plc.open()
        print(f"[SUCCESS] Connected to TwinCAT PLC. State: {plc.read_state()}")
        
        # 2. Command the Machine to Start
        print("[HMI] Pressing 'Start' Button...")
        plc.write_by_name("MAIN.RotaryCutter.bCmdStart", True, pyads.PLCTYPE_BOOL)
        time.sleep(1) # Let the PLC state machine process the command
        
        # 3. Main Physics Loop
        print("[SIMULATION] Conveyor physics loop running. Press Ctrl+C to stop.")
        while True:
            # Read the current state of the machine from the PLC
            state = plc.read_by_name("MAIN.RotaryCutter.eState", pyads.PLCTYPE_INT)
            
            # PackML State 30 = EXECUTE (Running)
            if state == 30: 
                print("\n[PHYSICS] Conveyor is moving. Material is feeding...")
                
                # Wait a random amount of time to simulate distance between products
                time.sleep(random.uniform(2.0, 4.0)) 
                
                # TRIGGER THE SENSOR (Workpiece leading edge blocks the laser)
                print("[SENSOR] ---> Workpiece Leading Edge Detected! (Rising Edge)")
                plc.write_by_name("MAIN.RotaryCutter.InfeedConveyor.ProductSensor.bRawInput", True, pyads.PLCTYPE_BOOL)
                
                # Wait 0.5 seconds (the time it takes the physical workpiece to pass the laser)
                time.sleep(0.5)
                
                # CLEAR THE SENSOR (Workpiece trailing edge has passed)
                print("[SENSOR] ---> Workpiece Trailing Edge Passed. (Falling Edge)")
                plc.write_by_name("MAIN.RotaryCutter.InfeedConveyor.ProductSensor.bRawInput", False, pyads.PLCTYPE_BOOL)
                
            else:
                print(f"[STATUS] Machine is not in EXECUTE state (Current State: {state}). Waiting...")
                time.sleep(2)

    except Exception as e:
        print(f"\n[ERROR] ADS Communication failed: {e}")
        print("Make sure your TwinCAT PLC is in RUN mode (Green Gear icon).")
    finally:
        plc.close()
        print("\n--- Connection Closed ---")

if __name__ == '__main__':
    run_simulation()