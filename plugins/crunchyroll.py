from selenium.common.exceptions import NoSuchElementException

from .baseplugin import *

class Crunchyroll(BasePlugin):

  @staticmethod
  def supports(url):
    return 'crunchyroll.com' in url

  def prepare(self):
    print('prepare')
    # accept cookies if it exists
    try:
      accept = self.driver.find_element_by_xpath(
        '//button[contains(text(), "Accept")]')
      accept.click()
    except NoSuchElementException:
      pass
    super().prepare()

  def play(self):
    self.driver.switch_to.frame(self.iframe)
    self.driver.execute_script('arguments[0].play()', self.video)
    self.driver.switch_to.default_content()

  def get_time(self):
    self.driver.switch_to.frame(self.iframe)
    currentTime = self.video.get_property('currentTime')
    self.driver.switch_to.default_content()
    return currentTime

  def get_duration(self):
    self.driver.switch_to.frame(self.iframe)
    currentTime = self.video.get_property('duration')
    self.driver.switch_to.default_content()
    return currentTime
