# HortiVault 🌱

## Overview
HortiVault is a smart greenhouse monitoring and automation system. It continuously captures, processes, and analyzes environmental data to maintain optimal growing conditions.

## Architecture
The system is built with a modular, decoupled architecture:
* **Firmware:** A microcontroller handles the physical sensor data acquisition.
* **Backend:** A Python-based server processes raw data, evaluates system states, and stores metrics persistently in a SQL database. The backend is designed to run in an isolated Docker environment.
* **Frontend:** A web dashboard for remote data visualization and configuration.

## Hardware & Sensors
* ESP32 Microcontroller
* Environmental Sensors: Temperature, Humidity, Soil Moisture, Light Intensity, and Water Level
* Webcam (planned for visual analysis)

## Repository Structure
* `/firmware/`: Contains the microcontroller codebase.
* `/backend/`: Contains the backend logic, data management, and event processing.
* `/frontend/`: Contains the web dashboard.

## Roadmap
* **Phase 1-3:** Hardware setup, sensor calibration, and SQL database data modeling.
* **Phase 4-7:** Backend data pipeline via USB, event processing, REST API development, and frontend dashboard implementation.
* **Phase 8-12:** Advanced analytics, network integration, computer vision, and fully automated climate control.
