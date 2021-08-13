from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep

from .baseplugin import *

class Netflix(BasePlugin):

  @staticmethod
  def supports(url):
    return 'netflix.com' in url

  def prepare(self):
    video = WebDriverWait(self.driver, 30) \
        .until(EC.presence_of_element_located((By.XPATH, '//video')))
    if not video:
      raise Exception('could not find video')
    script = """
    window.videoPlayer = window.netflix.appContext.state.playerApp.getAPI().videoPlayer;
    console.log(window.videoPlayer);
    window.id = videoPlayer.getAllPlayerSessionIds()[0];
    console.log(window.id);
    window.player = videoPlayer.getVideoPlayerBySessionId(id);
    console.log(window.player);
    """
    self.driver.execute_script(script)
    super().prepare()

  def pause(self):
    self.driver.execute_script('window.player.pause()')

  def play(self):
    self.driver.execute_script('window.player.play()')

  def set_time(self, time: int):
    self.driver.execute_script(f'window.player.seek({time} * 1000)')

  def remove_controls(self):
    selectors = [
      'PlayerControlsNeo__core-controls',
      'PlayerControlsNeo__bottom-control'
    ]
    # TODO: use better apis if possible
    for selector in selectors:
      #for element in self.driver.find_elements_by_class_name('selector'):
      for element in self.driver.find_elements_by_xpath(f'//div[contains(@class, \'{selector}\')]'):
        self.driver.execute_script('arguments[0].style = "visibility: hidden"', element)
