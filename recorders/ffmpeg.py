from subprocess import Popen, PIPE
from signal import SIGINT

class FFMPEG:

  def __init__(self):
    self.filename = 'out.mp4'
    self.display = 0
    self.virtual_sink_name = ''
    self.process = None

  def prepare_recording(self, display, virtual_sink_name):
    self.display = display
    self.virtual_audio_source_name = virtual_sink_name + '.monitor'

  def set_filename(self, filename):
    self.filename = filename

  def start_recording(self):
    if self.process:
      return
    cmd = f'ffmpeg -draw_mouse 0 -hide_banner -y -thread_queue_size 512 ' \
          f'-f x11grab -framerate 60 -i :{self.display}.0 ' \
          f'-f pulse -i {self.virtual_audio_source_name} ' \
          f'-c:v mpeg4 -q:v 1 -f mp4 {self.filename}'
    self.process = Popen(cmd.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)

  def stop_recording(self):
    if not self.process:
      return
    self.process.communicate(b'q')
    self.process = None
