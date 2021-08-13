from plugins import *

urls = {
  '1': '',
  '2': '',
  '3': '',
  '4': '',
  '5': '',
  '6': '',
  '7': '',
  '8': '',
  '9': '',
  '10': '',
}
plugins = [
  Crunchyroll,
  Netflix
]
#display_backend = "xephyr"
#display_visible = True
display_backend = "xvfb"
display_visible = False
width = 1920
height = 1080
virtual_sink_name = 'virtual_sink'
