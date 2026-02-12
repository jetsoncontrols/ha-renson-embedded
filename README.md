# Renson Embedded

Home Assistant custom integration for controlling a Renson Skye Pergola motorized roof.

## Installation

1. Install via [HACS](https://hacs.xyz/) as a custom repository
2. Add the repository URL: `https://github.com/jetsoncontrols/ha-renson-embedded`
3. Select category: **Integration**
4. Restart Home Assistant
5. Go to Settings > Devices & Services > Add Integration > Renson Embedded
6. Enter the IP address of your Renson device and credentials

## Features

Communicates with the Renson device over REST API and WebSocket for real-time state updates.

### Cover Entity

Controls the pergola slide (stack) position and slat (tilt) angle.

- **Slide position**: 0-100%
- **Tilt position**: 0-125 degrees mapped to 0-100%
- **Open/Close/Stop** for both slide and tilt
- **Set position** for both slide and tilt
- Real-time **opening/closing** state via WebSocket

### Buttons

- **Fully Open** - Opens the slide to 100%
- **Fully Close** - Closes the slats to 0 degrees
- **Open/Stop/Close/Stop** - Cycle button that alternates between open, stop, close, and stop on each press

### Binary Sensors

- **Fully Closed** - On when both slide and slats are at 0
- **Fully Opened** - On when slide is at 100% and slats are at 90 degrees

### Sensors

- **Roof State** - Current device state (ready, moving, homing, error, etc.)
- **Weather State** - Weather condition detected by the device

### Switch

- **Roof Lock** - Lock or unlock the roof

### Device

- **Visit** button links to the Renson device web UI

## Requirements

- Renson Skye Pergola with built-in web service
- Network access to the device from Home Assistant
- Device credentials (user type and password)
