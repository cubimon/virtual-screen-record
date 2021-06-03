from obswebsocket import obsws, requests
from os import getcwd

scene_name = 'virtual-screen-record'
video_name = 'video'
audio_name = 'audio'

class OBS:

  def __init__(self, host='localhost', port=4444):
    self.ws = obsws(host, port)
    try:
      self.ws.connect()
    except:
      raise Exception('could not connect to obs websocket server')

  def getSceneByName(self, name: str):
    for scene in self.ws.call(requests.GetSceneList()).getScenes():
      if scene['name'] == name:
        return scene

  def prepare_recording(self, display, virtual_sink_name):
    if not self.getSceneByName(scene_name):
      self.ws.call(requests.CreateScene(scene_name))
      self.ws.call(requests.CreateSource('video', 'xshm_input', scene_name))
      self.ws.call(requests.CreateSource('audio', 'pulse_output_capture', scene_name))
    self.ws.call(requests.SetSourceSettings('video', {'advanced': True, 'server': f':{display}', 'show_cursor': False}))
    self.ws.call(requests.SetSourceSettings('audio', {'device_id': f'{virtual_sink_name}.monitor'}))
    self.ws.call(requests.SetRecordingFolder(getcwd()))


  def set_filename(self, filename):
    self.ws.call(requests.SetFilenameFormatting(filename))


  def start_recording(self):
    self.ws.call(requests.StartRecording())


  def stop_recording(self):
    self.ws.call(requests.StopRecording())
