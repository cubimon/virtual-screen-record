from plugins import *

urls = {
  #'tower of god 1': 'https://www.crunchyroll.com/tower-of-god/episode-1-ball-795456'
  'tower of god 2': 'https://www.crunchyroll.com/tower-of-god/episode-2-3400-three-four-hundredths-795592'
}
plugins = [
  CrunchyrollPlugin
]
#display_backend = "xephyr"
display_backend = "xvfb"
display_visible = False
width = 1920
height = 1080
virtual_sink_name = 'virtual_sink'