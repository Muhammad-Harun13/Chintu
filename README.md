# Chintu Robot 🤖

Chintu is an advanced, AI-powered personal robot built with Python. It features a dynamic personality, voice interaction, computer vision, and autonomous motion capabilities.

## 🚀 Key Features

- **🧠 Dual AI Brain**: Powered by Google Gemini API for complex reasoning and Local Llama for offline capabilities.
- **👁️ Dynamic Eyes**: A custom-built expression engine that visualizes emotions like Happy, Curious, Thinking, and Scanning.
- **🎤 Voice Command System**: Responds to wake words and executes complex voice commands.
- **📷 Computer Vision**: Real-time scene scanning and object description using integrated camera systems.
- **⚙️ Precise Motion**: Controlled movement with dedicated motor drivers and patrol routines.
- **📡 Event-Driven Architecture**: Built on a robust `EventBus` for seamless communication between hardware and AI modules.

## 📁 Project Structure

- `Chintu/main.py`: The central application entry point.
- `Chintu/ai/`: Integration with Gemini and Local Llama AI models.
- `Chintu/vision/`: Camera controls and scene scanning logic.
- `Chintu/voice/`: Speech-to-text, text-to-speech, and wake word detection.
- `Chintu/display/`: The "Eyes" engine and UI dashboard.
- `Chintu/motion/`: Motor drivers and movement routines.

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Pygame (for the display engine)
- Required API keys (Gemini)

### Installation
1. Clone the repository:
   ```bash
   git clone git@github.com:Muhammad-Harun13/Chintu.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Chintu:
   ```bash
   python Chintu/main.py
   ```

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License.
