import pyaudio
import numpy as np
import matplotlib.pyplot as plt

DEVICE_INDEX = 0
CHUNK = 1024
RATE = 8000

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                input_device_index=DEVICE_INDEX,
                frames_per_buffer=CHUNK)

plt.ion()
fig, ax = plt.subplots()
rms_vals = []
line, = ax.plot(rms_vals)
ax.set_ylim(0, 5000)
ax.set_xlim(0, 100)

print("实时可视化音量，Ctrl+C退出。")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_data**2))
        rms_vals.append(rms)
        if len(rms_vals) > 100:
            rms_vals = rms_vals[-100:]
        line.set_ydata(rms_vals)
        line.set_xdata(np.arange(len(rms_vals)))
        ax.set_xlim(0, len(rms_vals))
        fig.canvas.draw()
        fig.canvas.flush_events()
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()
