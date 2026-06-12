# Ava: Real-Time Voice Assistant

Ava is a highly capable, real-time voice assistant built with a multi-threaded, node-based architecture. It uses local, on-device AI models for speech-to-text, text generation, text-to-speech, and conversational memory, ensuring privacy and low-latency responses.

## Core Features
* **Speech-to-Text (STT):** High-speed, accurate local transcription using `faster-whisper`.
* **Conversational Memory:** Persistent vector database (`ChromaDB`) to remember past conversations and context.
* **Large Language Model (LLM):** Fast on-device inference via local `Ollama` models.
* **Text-to-Speech (TTS):** Natural sounding voices with `Piper TTS`.
* **Low Latency Pipeline:** Asynchronous threaded queues allowing Ava to listen, think, and speak concurrently.

---

## Prerequisites

Before running Ava, ensure you have the following installed on your system:
1. **Python 3.10+**
2. **[Ollama](https://ollama.com/)** running locally (for the LLM).
   * After installing Ollama, download the model used by the assistant:
     ```bash
     ollama run llama3.2:1b
     ```

## Installation & Setup

It is highly recommended to run this project inside a Python Virtual Environment (`venv`) to keep the dependencies isolated from your main system.

### 1. Create a Virtual Environment
Open your terminal in the project directory and create a virtual environment:
```powershell
# On Windows
python -m venv venv
```

### 2. Activate the Virtual Environment
You must activate the virtual environment every time you want to run or install packages for Ava.
```powershell
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt)
.\venv\Scripts\activate.bat
```
*(When activated, your terminal prompt will show `(venv)` at the beginning of the line.)*

### 3. Install Requirements
With your virtual environment activated, install all the required Python libraries using the included `requirements.txt` file:
```powershell
pip install -r requirements.txt
```

---

## How to Run

1. Make sure **Ollama** is open and running in the background.
2. Activate your virtual environment (if not already activated):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. Run the main pipeline script:
   ```powershell
   python main.py
   ```
4. Ava will initialize and let you know when she is listening. Start speaking into your microphone! To stop the assistant, press `Ctrl+C`.

---

## Architecture

* `main.py` - Initializes threads and queues.
* `audio.py` - Handles microphone input and VAD (Voice Activity Detection).
* `stt.py` - Transcribes audio into text.
* `memory.py` - Saves and retrieves context from the ChromaDB vector database.
* `llm.py` - Prompts the local language model.
* `tts.py` - Synthesizes the generated text back into speech.
* `config.py` - Central configuration variables (thresholds, model names, etc.).

## License
MIT License
