import sounddevice as sd
import numpy as np
import config

print(f"Testing microphone input on device {config.AUDIO_INPUT_DEVICE}...")
try:
    recording = sd.rec(int(16000 * 2), samplerate=16000, channels=1, dtype='float32', device=config.AUDIO_INPUT_DEVICE)
    sd.wait()
    max_amp = np.max(np.abs(recording))
    print(f"Max amplitude: {max_amp:.6f}")
    if max_amp == 0.0:
        print("Microphone is completely silent (returning all zeros). This usually means Windows Privacy Settings are blocking microphone access for Desktop Apps.")
    else:
        print("Microphone successfully captured audio.")
except Exception as e:
    print(f"Error: {e}")
