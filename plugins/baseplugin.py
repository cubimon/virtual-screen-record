from retrying import retry

class BasePlugin:

  def __init__(self, driver):
    self.driver = driver

  def find_videos(self):
    """
    returns list of (element, iframe)
    """
    todo = self.driver.find_elements_by_xpath('//iframe')
    videos = []
    for video in self.driver.find_elements_by_xpath('//video'):
      if video.is_displayed():
        videos.append((video, None))
    while len(todo) > 0:
      iframe = todo.pop()
      self.driver.switch_to.frame(iframe)
      for video in self.driver.find_elements_by_xpath('//video'):
        if video.is_displayed():
          videos.append((video, iframe))
      todo.extend(self.driver.find_elements_by_xpath('//iframe'))
      self.driver.switch_to.default_content()
    return videos

  @retry(stop_max_delay=10000)
  def get_video(self):
    videos = self.find_videos()
    if len(videos) != 1:
      raise Exception('could not find video')
    return videos[0]

  def prepare(self):
    self.video, self.iframe = self.get_video()
    self.pause()
    self.set_time(0)
    self.remove_controls()
    self.fullscreen()

  def pause(self):
    if self.iframe:
      self.driver.switch_to.frame(self.iframe)
    self.driver.execute_script('arguments[0].pause()', self.video)
    if self.iframe:
      self.driver.switch_to.default_content()

  def play(self):
    if self.iframe:
      self.driver.switch_to.frame(self.iframe)
    self.driver.execute_script('arguments[0].play()', self.video)
    if self.iframe:
      self.driver.switch_to.default_content()

  def get_time(self):
    if self.iframe:
      self.driver.switch_to.frame(self.iframe)
    currentTime = self.video.get_property('currentTime')
    if self.iframe:
      self.driver.switch_to.default_content()
    return currentTime

  def set_time(self, time: int):
    if self.iframe:
      self.driver.switch_to.frame(self.iframe)
    self.driver.execute_script(f'arguments[0].currentTime = {time}', self.video)
    if self.iframe:
      self.driver.switch_to.default_content()

  def get_duration(self):
    if self.iframe:
      self.driver.switch_to.frame(self.iframe)
    currentTime = self.video.get_property('duration')
    if self.iframe:
      self.driver.switch_to.default_content()
    return currentTime

  def remove_controls(self):
    if self.iframe:
      self.driver.switch_to.frame(self.iframe)
    self.driver.execute_script('arguments[0].controls = false', self.video)
    if self.iframe:
      self.driver.switch_to.default_content()

  def fullscreen(self):
    if self.iframe:
      self.driver.switch_to.frame(self.iframe)
    self.driver.execute_script('arguments[0].requestFullscreen()', self.video)
    if self.iframe:
      self.driver.switch_to.default_content()
