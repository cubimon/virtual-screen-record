#!/usr/bin/python3

import psutil
import logging
from pulsectl import Pulse
from logging import error
from os import environ
from subprocess import Popen, PIPE
from signal import signal, SIGINT
from time import sleep
from pathlib import Path
from configparser import ConfigParser
from selenium.webdriver import Firefox, FirefoxProfile

from config import *


def shutdown():
  if driver:
    driver.close()
  if xserver:
    xserver.send_signal(SIGINT)
    xserver.wait()
  if pulse_module_id:
    # TODO:
    pulse.module_unload(pulse_module_id)
    #Popen(['pactl', 'unload-module', str(pulse_module_id)])
  if record_process:
    record_process.send_signal(SIGINT)
    record_process.wait()


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


def start_record(filename):
  global record_process
  # ffmpeg -f x11grab -i :1.0+nomouse -f pulse -ac 2 -i virtual_sink.monitor output.mkv
  record_process = Popen(['ffmpeg', 
    '-framerate', '25',
    '-f', 'x11grab', '-i', f'{display}.0+nomouse',
    '-f', 'pulse', '-ac', '2', '-i', f'{virtual_sink_name}.monitor',
    f'{filename}.mkv'], stdout=PIPE)

def stop_record():
  record_process.send_signal(SIGINT)
  record_process.wait()

urls = [
  'https://www.crunchyroll.com/tower-of-god/episode-1-ball-795456'
]
plugins = [
  CrunchyrollPlugin
]
width = 1920
height = 1080
display = ':1'
virtual_sink_name = 'virtual_sink'


logging.basicConfig(level=logging.INFO)
pulse = Pulse()
signal(SIGINT, signal_handler)
try:
  xserver = next(filter(lambda x: x.name() == 'Xephyr' and x.cmdline()[1] == display, list(psutil.process_iter())))
  if xserver:
    xserver.terminate()
except StopIteration as e:
  logging.info('could not find existing xephyr')
xserver = Popen(['Xephyr', display, '-screen', f'{width}x{height}'], stdout=PIPE)
try:
  pulse_sink_info = next(filter(
    lambda sink: sink.name == virtual_sink_name, pulse.sink_list()))
except StopIteration as e:
  pulse_module_id = pulse.module_load('module-null-sink', f'sink_name={virtual_sink_name}')
  logging.info('loaded null sink')
pulse_sink_info = next(filter(
  lambda sink: sink.name == virtual_sink_name, pulse.sink_list()))
pulse_source_info = next(filter(
  lambda sink: sink.name == virtual_sink_name + '.monitor', pulse.source_list()))
record_process = None

environ['DISPLAY'] = display
environ['PULSE_SINK'] = str(pulse_sink_info.index)

driver = Firefox(get_firefox_profile())
driver.set_window_position(0, 0)
driver.set_window_size(width, height)
driver.fullscreen_window()

for url in urls:
  plugin_class = get_plugin_class(url)
  plugin = plugin_class(driver)
  if not plugin:
    error(f'couldn\'t find plugin for url: {url}')
    continue
  driver.get(url)
  plugin.prepare()
  start_record('output')
  sleep(2) # wait a little to stabilize recording
  plugin.play()
  duration = plugin.get_duration()
  sleep(duration)
  stop_record()
  import pdb; pdb.set_trace()
  # TODO: wait until stopped
  # remove cursor?

print('exited')
import pdb; pdb.set_trace()

shutdown()
