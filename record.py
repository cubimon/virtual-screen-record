#!/usr/bin/python3

import psutil
import logging
from pulsectl import Pulse
from logging import error
from os import environ
from signal import signal, SIGINT
from time import sleep
from pathlib import Path
from configparser import ConfigParser
from selenium.webdriver import Firefox, FirefoxProfile
from pyvirtualdisplay import Display

from config import *
from obs import OBS


def shutdown():
  if driver:
    driver.close()
  display.stop()
  if pulse_module_id:
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
try:
  pulse_sink_info = next(filter(
    lambda sink: sink.name == virtual_sink_name, pulse.sink_list()))
except StopIteration as e:
  pulse_module_id = pulse.module_load('module-null-sink', f'sink_name={virtual_sink_name}')
  logging.info('loaded null sink')
pulse_sink_info = next(filter(
  lambda sink: sink.name == virtual_sink_name, pulse.sink_list()))
obs = OBS()
obs.prepare_recording(display.display, virtual_sink_name)

environ['PULSE_SINK'] = str(pulse_sink_info.index)

driver = Firefox(get_firefox_profile())
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
  obs.set_filename(name + '.mp4')
  obs.start_recording()
  print('started recording')
  sleep(2) # wait a little to stabilize recording
  plugin.play()
  duration = plugin.get_duration()
  sleep(duration)
  obs.stop_recording()
  print('stopped recording')
  import pdb; pdb.set_trace()
  # TODO: wait until stopped
  # remove cursor?

print('exited')
import pdb; pdb.set_trace()

shutdown()
