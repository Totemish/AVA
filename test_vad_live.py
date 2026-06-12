import sounddevice as sd
import numpy as np
import onnxruntime as ort
import config

print(f"Testing VAD and Mic locally on device {config.AUDIO_INPUT_DEVICE}...")

sess_options = ort.SessionOptions()
sess_options.inter_op_num_threads = 1
sess_options.intra_op_num_threads = 1
vad_session = ort.InferenceSession("models/silero_vad.onnx", sess_options=sess_options)
state = np.zeros((2, 1, 128), dtype=np.float32)

def audio_callback(indata, frames, time_info, status):
    global state
    audio_chunk = indata[:, 0].astype(np.float32)
    max_amp = np.max(np.abs(audio_chunk))
    
    ort_inputs = {
        'input': audio_chunk.reshape(1, -1),
        'sr': np.array(config.SAMPLE_RATE, dtype=np.int64),
        'state': state
    }
    ort_outs = vad_session.run(None, ort_inputs)
    speech_prob, state = ort_outs[0], ort_outs[1]
    
    print(f"Amp: {max_amp:.4f} | VAD: {speech_prob[0][0]:.4f}", flush=True)

try:
    stream = sd.InputStream(
        device=config.AUDIO_INPUT_DEVICE,
        samplerate=config.SAMPLE_RATE,
        channels=1,
        blocksize=config.CHUNK_SIZE,
        callback=audio_callback
    )
    with stream:
        print("Listening for 5 seconds. Please speak loudly!")
        sd.sleep(5000)
except Exception as e:
    print(f"Error: {e}")
