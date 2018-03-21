# Audio Capture (Collection)

## Pre-conditions
1. Operating System - "Windows 10", would probably work on 7/8 but that wasn't tested.
1. Hardware - Sound device capable of input 
1. Software Installed - "Python 3.6", MME API (Native to Windows, doesn't require install)
1. Needed Packages - "PyAudio", included in 2 files (pyaudio.py, _portaudio.cp36-win32.pyd), or you can run "python -m pip install pyaudio"

## Post-Conditions
1. ADPCM output file exists and it's size indicates audio was captured for required amount of seconds

## Additional comments
1. recorder.py is the exploit script to run on the target machine
1. You can avoid installing the "PyAudio" package and just place pyaudio.py, _portaudio.cp36-win32.pyd and recorder.py in the same folder, then run recorder.py
1. If you want to hear for yourself that the exploit does in fact captures audio, you can run it on a physical machine with a physical, non-emulated microphone. After running recorder.py, place manualTester.py in the same folder and run it, you will get a wav file you can listen to.
