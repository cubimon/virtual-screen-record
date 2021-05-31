
# Xnest

```python
xserver = Popen(['Xnest', display, '-geometry', f'{width}x{height}+0+0'])
```

# gstreamer
```bash
gst-launch-1.0 ximagesrc display-name=:1 use-damage=0 ! video/x-raw,framerate=30/1 ! videoconvert ! x264enc ! avimux ! filesink location=tmp.avi
gst-launch-1.0 ximagesrc display-name=:1 use-damage=0 ! video/x-raw,framerate=30/1 ! videoconvert ! x264enc ! avimux name = mux ! filesink location=tmp.avi pulsesrc device=virtual_sink.monitor ! audioconvert ! mux.
gst-launch-1.0 pulsesrc device=virtual_sink.monitor ! audioconvert ! vorbisenc ! oggmux ! filesink location=tmp.ogg
gst-launch-1.0 pulsesrc device=virtual_sink.monitor ! queue ! audioconvert ! 'audio/x-raw,rate=44100,channels=2' ! lamemp3enc ! queue ! avimux ! filesink location=tmp.avi

# together
gst-launch-1.0 ximagesrc display-name=:1 ! video/x-raw,framerate=30/1 ! queue ! videoconvert ! videorate ! queue ! x264enc ! queue ! avimux name=mux ! queue ! filesink location=tmp.avi pulsesrc device=virtual_sink.monitor ! queue ! audioconvert ! 'audio/x-raw,rate=44100,channels=2' ! lamemp3enc ! queue ! mux.
gst-launch-1.0 ximagesrc display-name=:1 ! video/x-raw,framerate=30/1 ! queue ! videoconvert ! queue ! x264enc key-int-max=5 ! queue ! mp4mux name=mux reserved-bytes-per-sec=100 reserved-max-duration=20184000000000 reserved-moov-update-period=100000000 ! queue ! filesink location=out.mp4 pulsesrc device=virtual_sink.monitor ! queue ! audioconvert ! queue ! lamemp3enc bitrate=192 ! queue ! mux.

# old
gst-launch-1.0 ximagesrc display-name=:1 ! video/x-raw,framerate=60/1 ! videoconvert ! theoraenc ! oggmux ! filesink location=tmp.ogg
gst-launch-1.0 ximagesrc display-name=:1 ! video/x-raw,framerate=60/1 ! videoconvert ! theoraenc ! oggmux name = mux ! filesink location=tmp.ogg pulsesrc device=virtual_sink.monitor !  audioconvert ! vorbisenc ! mux.
ffmpeg -f x11grab -i :1.0 -f pulse -ac 2 -i virtual_sink.monitor output.mkv
```


```py
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)
gst_pipeline = Gst.parse_launch('ximagesrc display-name={display} ! filesink location=tmp.ogg')
```

# ffmpeg

```bash
ffmpeg -f x11grab -i :1.0 -f pulse -ac 2 -i virtual_sink.monitor output.mkv
# nvenc, super slow, more like 10 fps
ffmpeg -f x11grab -i :1.0 -f pulse -ac 2 -i virtual_sink.monitor -c:v h264_nvenc -qp 0 output.mkv
# ultrafast, also super slow ~ 10fps
ffmpeg -f x11grab -i :1.0 -f pulse -ac 2 -i virtual_sink.monitor -c:v libx264rgb -crf 0 -preset ultrafast output.mkv
```