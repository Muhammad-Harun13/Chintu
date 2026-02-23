# Chintu – Smart Autonomous Robotic AI System

Emotion-first robot software stack for Raspberry Pi 4 with expressive animated eyes.

## Project Structure

```text
Chintu/
  core/
  display/
  motion/
  vision/
  voice/
  ai/
  utils/
  main.py
```

## Installation

1. Install system dependencies on Raspberry Pi OS:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-pygame portaudio19-dev
   ```
2. Install Python packages:
   ```bash
   pip install pygame requests pyttsx3 pvporcupine vosk sounddevice picamera2 RPi.GPIO
   ```
3. Install and start Ollama, then pull a small model:
   ```bash
   ollama pull phi3:mini
   ```
4. Set environment variables:
   ```bash
   export GEMINI_API_KEY="your_key_here"
   export OLLAMA_MODEL="phi3:mini"
   export PORCUPINE_ACCESS_KEY="your_porcupine_access_key"
   export PORCUPINE_KEYWORD_PATH="/home/pi/hey-chintu.ppn"  # optional custom wake phrase
   export WAKE_WORD="porcupine"  # built-in Porcupine keyword when custom keyword path is not set
   export VOSK_MODEL_PATH="/home/pi/models/vosk-model-small-en-us-0.15"
   export CHINTU_LOG_LEVEL="DEBUG"  # optional: DEBUG, INFO, WARNING
   ```
5. Run:
   ```bash
   cd Chintu
   python main.py
   ```

## GPIO Pin Mapping (L298N)

| L298N Pin | Raspberry Pi GPIO | Purpose |
|---|---:|---|
| ENA | GPIO 12 (PWM) | Left motor speed |
| IN1 | GPIO 5 | Left motor direction 1 |
| IN2 | GPIO 6 | Left motor direction 2 |
| ENB | GPIO 13 (PWM) | Right motor speed |
| IN3 | GPIO 20 | Right motor direction 1 |
| IN4 | GPIO 21 | Right motor direction 2 |

## Example Usage Flow

1. Wake word detector triggers interaction (`WAKE_WORD`/Porcupine keyword).
2. Emotion changes to `LISTENING` and speech is captured.
3. Router classifies text:
   - direct commands -> motor/scanner actions,
   - short prompts -> local LLaMA,
   - long prompts -> Gemini with fallback to local.
4. Eyes react in real-time to emotion transitions.
5. Response is spoken via TTS.
6. System idles and becomes `SLEEPY` after inactivity.

## Notes

- Eye animations are fully procedural (no static PNG assets).
- All hardware modules include fallback behavior for non-Pi development.
- If the camera is disconnected, Chintu logs and speaks a clear "Camera not connected" message while other modules continue running.
