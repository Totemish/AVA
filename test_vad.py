import onnxruntime as ort
import numpy as np

sess = ort.InferenceSession('models/silero_vad.onnx')
state = np.zeros((2, 1, 128), dtype=np.float32)
audio = np.zeros((1, 512), dtype=np.float32)

# Case 1: sr as array shape (1,)
try:
    sr = np.array([16000], dtype=np.int64)
    out = sess.run(None, {'input': audio, 'state': state, 'sr': sr})
    print("Array sr success")
except Exception as e:
    print("Array sr error:", e)

# Case 2: sr as scalar shape ()
try:
    sr = np.array(16000, dtype=np.int64)
    out = sess.run(None, {'input': audio, 'state': state, 'sr': sr})
    print("Scalar sr success")
except Exception as e:
    print("Scalar sr error:", e)
