# Modular Rotary Cutter (Flying Shear)

High-Performance Industrial Control Logic with Python Digital Twin

## 1. Overview

This project implements a modular, object-oriented control system for a Rotary Cutter (Flying Shear) using TwinCAT 3 (Structured Text). It bridges the gap between Industrial Automation (OT) and Software Engineering (IT) by utilizing a Python-based Digital Twin for real-time physics simulation and closed-loop logic validation via ADS.

## 2. Technical Stack

- **Control System**: Beckhoff TwinCAT 3.1 (XAE)
- **Languages**: Structured Text (IEC 61131-3), Python 3.13
- **Architecture**: Object-Oriented Programming (OOP), Interface-based Dependency Injection
- **Communication**: ADS (Automation Device Specification), MQTT (TwinCAT IoT)
- [cite_start]**Standards**: PackML-inspired State Machine (`E_MachineState`) [cite: 112, 113]

## 3. System Architecture

The codebase is structured to ensure maximum modularity and hardware independence. [cite_start]Physical hardware is decoupled from the control logic using IEC 61131-3 Interfaces (`I_Drive`, `I_DigitalSensor`) [cite: 8-16, 48, 49].

```mermaid
classDiagram
    direction TB
    
    class MAIN {
        +RotaryCutter : FB_MainMachine
    }
    
    class FB_MainMachine {
        +InfeedConveyor : FB_InfeedConveyor
        +RotaryKnife : FB_RotaryKnife
        +ConveyorMotor : FB_Drive
        +KnifeMotor : FB_Drive
        +fbProductSensor : FB_DigitalSensor
    }

    class FB_InfeedConveyor {
        +iMotor : I_Drive
        +iProductCam : I_DigitalSensor
    }

    class FB_RotaryKnife {
        +iMotor : I_Drive
        +bSyncCommand : BOOL
        +fbGearIn : MC_GearIn
    }

    class I_DigitalSensor {
        <<Interface>>
        +P_RisingEdge : BOOL
        +P_RawInput : BOOL
    }

    class I_Drive {
        <<Interface>>
        +M_MoveAbs()
        +M_MoveVel()
        +M_Stop()
    }

    class FB_DigitalSensor {
        +bRawInput : BOOL
        +fbRisingEdge : R_TRIG
    }
    
    class FB_Drive {
        +Axis : AXIS_REF
        +fbMoveVel : MC_MoveVelocity
    }

    MAIN --> FB_MainMachine : Executes
    FB_MainMachine *-- FB_InfeedConveyor : Orchestrates
    FB_MainMachine *-- FB_RotaryKnife : Orchestrates
    
    %% Interface Connections
    FB_InfeedConveyor --> I_DigitalSensor : Requires
    FB_InfeedConveyor --> I_Drive : Requires
    FB_RotaryKnife --> I_Drive : Requires
    
    %% Hardware Implementations
    FB_DigitalSensor ..|> I_DigitalSensor : Implements
    FB_Drive ..|> I_Drive : Implements
```

**FB_MainMachine**: Orchestrates the top-level state machine and module coordination.

**FB_InfeedConveyor**: Manages material transport. Utilizes I_Drive and I_DigitalSensor interfaces to decouple logic from physical I/O.

**FB_RotaryKnife**: Implements electronic gearing (Master/Slave synchronization) to synchronize cutting speed with conveyor velocity.

**FB_DigitalSensor**: Hardware wrapper for digital inputs with integrated edge detection (R_TRIG/F_TRIG).

## 4. Digital Twin & Simulation

To enable "Hardware-in-the-Loop" testing without physical components, a Python simulation is integrated directly into the PLC's real-time kernel:

- **Physics Simulation**: Python calculates deterministic workpiece flow and triggers concrete sensor instances (bRawInput) within the TwinCAT Router via pyads.
- **Closed-Loop Verification**: Python synchronously reads the PLC's response (bSyncCommand) immediately after sensor triggering to mathematically verify deterministic motion execution and state transitions.
- **Abstraction**: The PLC logic interacts strictly with interfaces (I_DigitalSensor), allowing for a seamless transition from the Python simulation directly to physical fieldbus commissioning without code changes.

## 5. IoT & Telemetry

A dedicated FB_Telemetry module utilizes the TwinCAT IoT library to publish machine states to an MQTT broker.

- **Broker**: broker.hivemq.com (Default)
- **Payload**: JSON-formatted machine state and performance metrics sent at 2-second intervals.

## 6. Setup and Deployment

### Prerequisites

- TwinCAT 3.1 (eXtendible Automation Engineering)
- Python 3.10+ with pyads library

### Execution

**TwinCAT**: Open the .sln, build, and Activate Configuration. Ensure the PLC is in Run Mode (State 5 in ADS).

**Digital Twin**:
```bash
python 07_Digital_Twin/simulate_machine.py
```

**Monitoring**: Observe state transitions (eState) and closed-loop validation outputs directly in the Python CLI or via an MQTT client subscribing to the telemetry topic.
