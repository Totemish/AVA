import os
import urllib.request
import tarfile
import config

def download_file(url, filepath):
    if not os.path.exists(filepath):
        print(f"Downloading {url} to {filepath}...")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        urllib.request.urlretrieve(url, filepath)
        print("Done.")
    else:
        print(f"File {filepath} already exists.")

def setup_models():
    # Piper TTS model
    os.makedirs(config.PIPER_MODEL_DIR, exist_ok=True)
    
    if not os.path.exists(config.PIPER_MODEL_FILE):
        download_file(config.PIPER_MODEL_URL, config.PIPER_MODEL_FILE)
    if not os.path.exists(config.PIPER_MODEL_CONFIG):
        download_file(config.PIPER_CONFIG_URL, config.PIPER_MODEL_CONFIG)
    
    print("Piper TTS setup complete.")
        
    # Silero VAD ONNX model
    vad_url = "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx"
    vad_path = "models/silero_vad.onnx"
    download_file(vad_url, vad_path)
    print("Silero VAD setup complete.")

if __name__ == "__main__":
    setup_models()
