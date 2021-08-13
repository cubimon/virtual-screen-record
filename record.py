#!/usr/bin/python3

import logging
from pulsectl import Pulse
from logging import error
from os import environ
from signal import signal, SIGINT
from time import sleep, time
from pathlib import Path
from configparser import ConfigParser
from selenium.webdriver import Firefox, FirefoxProfile
from pyvirtualdisplay import Display

from config import *
from recorders.ffmpeg import FFMPEG


def shutdown():
  if recorder:
    logging.info('stopping recording')
    recorder.stop_recording()
  if display:
    logging.info('stopping display')
    display.stop()
  if driver:
    logging.info('stopping webdriver')
    driver.close()
  if pulse_module_id:
    logging.info('removing pulseaudio module')
    # TODO:
    pulse.module_unload(pulse_module_id)
    #Popen(['pactl', 'unload-module', str(pulse_module_id)])


def signal_handler(sig, frame):
  if sig == SIGINT:
    print('got sigint, shutting down')
    shutdown()


def get_firefox_profile():
  ini_file = ConfigParser()
  ini_file.read(str(Path.home()) + "/.mozilla/firefox/profiles.ini")
  for section in ini_file.sections():
    if "Default" in ini_file[section] \
        and ini_file[section]["Default"] == "1" \
        and "Path" in ini_file[section]:
      return FirefoxProfile(
        str(Path.home()) + "/.mozilla/firefox/" + ini_file[section]["Path"])


def get_plugin_class(url):
  for plugin in plugins:
    if plugin.supports(url):
      return plugin

logging.basicConfig(level=logging.INFO)
pulse = Pulse()
signal(SIGINT, signal_handler)
display = Display(backend=display_backend, size=(width, height), visible=display_visible)
display.start()
pulse_module_id = None
# TODO: unload if it exists, this should solve our obs device issue
try:
  pulse_sink_info = next(filter(
    lambda sink: sink.name == virtual_sink_name, pulse.sink_list()))
except StopIteration as e:
  pulse_module_id = pulse.module_load('module-null-sink', f'sink_name={virtual_sink_name}')
  logging.info('loaded null sink')
pulse_sink_info = next(filter(
  lambda sink: sink.name == virtual_sink_name, pulse.sink_list()))
recorder = FFMPEG()
recorder.prepare_recording(display.display, virtual_sink_name)

environ['PULSE_SINK'] = str(pulse_sink_info.index)

profile = get_firefox_profile()
profile.set_preference('full-screen-api.allow-trusted-requests-only', False)
profile.set_preference('media.autoplay.default', 0)
driver = Firefox(profile)
driver.set_window_position(0, 0)
driver.set_window_size(width, height)
driver.fullscreen_window()

for name, url in urls.items():
  plugin_class = get_plugin_class(url)
  plugin = plugin_class(driver)
  if not plugin:
    error(f'couldn\'t find plugin for url: {url}')
    continue
  print(f'going for {name} and {url}')
  driver.get(url)
  plugin.prepare()
  recorder.set_filename(name)
  recorder.start_recording()
  print('started recording')
  sleep(2) # wait a little to stabilize recording
  plugin.play()
  duration = plugin.get_duration()
  duration = int(duration * 1.01) # some offset to make sure we have everything
  start_time = time()
  remaining = duration - (time() - start_time)
  while remaining > 0:
    logging.info('remaining waiting time: ' + str(remaining))
    if remaining < 30:
      sleep(remaining)
    else:
      sleep(30)
    remaining = duration - (time() - start_time)
  recorder.stop_recording()
  print('stopped recording')

print('finished all videos')
shutdown()
