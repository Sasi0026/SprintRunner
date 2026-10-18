import os
import sys

# On some Windows machines SDL's default audio driver (WASAPI) fails to open
# the speakers and every sound is silent; DirectSound works everywhere.
if sys.platform == 'win32':
    os.environ.setdefault('SDL_AUDIODRIVER', 'directsound')

from src.app import SprintRunnerApp

if __name__ == "__main__":
    SprintRunnerApp().run()
