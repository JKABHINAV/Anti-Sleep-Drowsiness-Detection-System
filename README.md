# Anti-Sleep Drowsiness Detection System
An IoT prototype using a laptop camera for vision processing and an ESP32 for real-time alerting.

## Tech Stack
- **Language:** Python (Laptop), C (ESP32)
- **Framework:** OpenCV, Dlib, ESP-IDF
- **Hardware:** ESP32, Buzzer, Laptop Camera

## How it works
1. The Python script captures video and calculates the **Eye Aspect Ratio (EAR)**.
2. If EAR falls below a threshold for a set time, an 'A' signal is sent via UART.
3. The ESP32 receives the signal and activates the hardware alarm.
