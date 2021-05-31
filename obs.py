from obswebsocket import obsws, requests
from os import getcwd

def getSceneByName(name: str):
  for scene in ws.call(requests.GetSceneList()).getScenes():
    if scene['name'] == name:
      return scene

ws = obsws('localhost', 4444)
ws.connect()

scene_name = 'virtual-screen-record'
video_name = 'video'
audio_name = 'audio'


def prepare_recording():
  if not getSceneByName(scene_name):
    ws.call(requests.CreateScene(scene_name))
    ws.call(requests.CreateSource('video', 'xshm_input', scene_name))
    ws.call(requests.CreateSource('audio', 'pulse_output_capture', scene_name))
    ws.call(requests.SetSourceSettings('video', {'advanced': True, 'server': ':1', 'show_cursor': False}))
    ws.call(requests.SetSourceSettings('audio', {'device_id': 'virtual_sink.monitor'}))
  ws.call(requests.SetRecordingFolder(getcwd()))


def set_filename(filename):
  ws.call(requests.SetFilenameFormatting(filename))


def start_recording():
  ws.call(requests.StartRecording())


def start_recording():
  ws.call(requests.StopRecording())
