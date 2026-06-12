import os

# Audio Configuration
SAMPLE_RATE = 16000
CHUNK_SIZE = 512
AUDIO_INPUT_DEVICE = None # Use system default microphone automatically
AUDIO_GAIN = 2.0 # Software amplifier

# VAD Configuration
VAD_THRESHOLD = 0.3
MIN_SPEECH_DURATION_MS = 250
MIN_SILENCE_DURATION_MS = 500

# Model Selection
OLLAMA_MODEL = "llama3.2:1b"  # Lightweight model for 8GB RAM
OLLAMA_HOST = "http://localhost:11434"
WHISPER_MODEL = "small"  # Much more accurate for Indian English accents
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# TTS Configuration (Piper)
# These will be downloaded automatically if not present
PIPER_MODEL_DIR = "models/piper"
PIPER_MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"
PIPER_CONFIG_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
PIPER_MODEL_FILE = os.path.join(PIPER_MODEL_DIR, "en_US-amy-medium.onnx")
PIPER_MODEL_CONFIG = os.path.join(PIPER_MODEL_DIR, "en_US-amy-medium.onnx.json")

# Memory Configuration
CHROMA_DB_DIR = "./chroma_db"
