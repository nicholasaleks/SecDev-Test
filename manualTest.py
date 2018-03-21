import audioop
import wave

data = []
with open('output.adpcm', 'rb') as f:
    state = (None, None)
    byte = f.read(1)
    while byte != b'':
        state = audioop.adpcm2lin(byte, 4, state[1])
        data.append(state[0])
        byte = f.read(1)
wf = wave.open('output.wav', 'wb')
wf.setnchannels(2)
wf.setsampwidth(4)
wf.setframerate(44100)
wf.writeframes(b''.join(data))
wf.close()
