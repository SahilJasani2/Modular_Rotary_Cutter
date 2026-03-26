# Modular Rotary Cutter (Flying Shear)

High-Performance Industrial Control Logic with Python Digital Twin

## 1. Overview

This project implements a modular, object-oriented control system for a Rotary Cutter (Flying Shear) using TwinCAT 3 (Structured Text). It bridges the gap between Industrial Automation (OT) and Software Engineering (IT) by utilizing a Python-based Digital Twin for real-time physics simulation and logic validation via ADS.

## 2. Technical Stack

- **Control System**: Beckhoff TwinCAT 3.1 (XAE)
- **Languages**: Structured Text (IEC 61131-3), Python 3.13
- **Architecture**: Object-Oriented Programming (OOP), Interface-based Dependency Injection
- **Communication**: ADS (Automation Device Specification), MQTT (TwinCAT IoT)
- **Standards**: PackML-inspired State Machine (E_MachineState)

## 3. System Architecture

The codebase is structured to ensure maximum modularity and hardware independence:

- **FB_MainMachine**: Orchestrates the top-level state machine and module coordination.
- **FB_InfeedConveyor**: Manages material transport. Utilizes I_Drive and I_DigitalSensor interfaces to decouple logic from physical I/O.
- **FB_RotaryKnife**: Implements electronic gearing (Master/Slave synchronization) to synchronize cutting speed with conveyor velocity.
- **FB_DigitalSensor**: Hardware wrapper for digital inputs with integrated edge detection (R_TRIG/F_TRIG).

## 4. Digital Twin & Simulation

To enable "Hardware-in-the-Loop" testing without physical components, a Python simulation is integrated directly into the PLC's real-time kernel:

- **Logic**: Python calculates deterministic workpiece flow based on simulated conveyor velocity.
- **Communication**: Uses pyads to write directly to concrete sensor instances (bRawInput) within the TwinCAT Router.
- **Abstraction**: The PLC logic interacts with interfaces (I_DigitalSensor), while Python interacts with concrete instances, allowing for seamless transition from simulation to physical commissioning.

## 5. IoT & Telemetry

A dedicated FB_Telemetry module utilizes the TwinCAT IoT library to publish machine states to an MQTT broker.

- **Broker**: broker.hivemq.com (Default)
- **Payload**: JSON-formatted machine state and performance metrics.

## 6. Setup and Deployment

### Prerequisites

- TwinCAT 3.1 (eXtendible Automation Engineering)
- Python 3.10+ with pyads library

### Execution

**TwinCAT**: Open the .sln, build, and Activate Configuration in Run Mode (UMRT supported).

**Digital Twin**:
```bash
python 07_Digital_Twin/simulate_machine.py
```

**Monitoring**: Observe state transitions (eState) and sensor triggers in the TwinCAT Live Watch or via an MQTT client.
