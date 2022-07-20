
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
import re

float_num_re = re.compile(r"([0-9,]+\.*\d*)")

# FireFox binary path (Must be absolute path)
FIREFOX_BINARY = FirefoxBinary('/opt/firefox/firefox')
 
# FireFox PROFILE
PROFILE = webdriver.FirefoxProfile()
PROFILE.set_preference("browser.cache.disk.enable", False)
PROFILE.set_preference("browser.cache.memory.enable", False)
PROFILE.set_preference("browser.cache.offline.enable", False)
PROFILE.set_preference("network.http.use-cache", False)
PROFILE.set_preference("general.useragent.override","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:72.0) Gecko/20100101 Firefox/72.0")
 
# FireFox Options
FIREFOX_OPTS = Options()
FIREFOX_OPTS.log.level = "trace"    # Debug
FIREFOX_OPTS.headless = True
GECKODRIVER_LOG = '/geckodriver.log'

class Scraper:

	def __init__(self):
		ff_opt = {
			'firefox_binary': FIREFOX_BINARY,
			'firefox_profile': PROFILE,
			'options': FIREFOX_OPTS,
			'service_log_path': GECKODRIVER_LOG
		}
		self.DRIVER = webdriver.Firefox(**ff_opt)
		self.DRIVER.set_window_size(1370,2000)
		self.url = None
		self.selector = None

	def get_preview(self, link):
		"""Fetch a page and return a screenshot of it as png bytes"""
		if self.url != link:
			self.DRIVER.get(link)
			self.url = link
		time.sleep(6) # just in case
		return self.DRIVER.get_screenshot_as_png()

	def locate_element(self, link, x, y):
		"""Find an element at the coordinates, and return a css selector for it"""
		if self.url != link:
			self.DRIVER.get(link)
			self.url = link
		self.x_click = x
		self.y_click = y

		result = self.DRIVER.execute_script("""
// walk tree towards root, building selector, until selector selects only one thing.
const getCssSelectorShort = (elem) => {
  let el = elem;
  let path = [], parent;
  let selector = '';
  while (parent = el.parentNode) {
    let tag = el.tagName, siblings;
    path.unshift(
      el.id ? `#${el.id}` : (
        siblings = parent.children,
        [].filter.call(siblings, sibling => sibling.tagName === tag).length === 1 ? tag :
        `${tag}:nth-child(${1+[].indexOf.call(siblings, el)})`
      )
    );
    el = parent;

    // Test it
    selector = `${path.join(' > ')}`.toLowerCase();
    const matches = document.querySelectorAll(selector);
    if (matches.length === 1 && matches[0] === elem) {
    	break;
    }
  };
  return selector;
};
return getCssSelectorShort(document.elementFromPoint(%i, %i));
""" % (x, y))
		self.selector = result
		return result

	def get_text_with_selector(self, link, selector):
		if self.url != link:
			self.DRIVER.get(link)
			time.sleep(4)
			self.url = link
		return self.DRIVER.find_element(By.CSS_SELECTOR, selector).text

	def click_last_spot(self):
		ac = ActionChains(self.DRIVER)
		ac.move_by_offset(self.x_click, self.y_click).click().perform()
		time.sleep(1) # just in case
		return self.DRIVER.get_screenshot_as_png()

	def click_element_with_selector(self):
		self.DRIVER.find_element(By.CSS_SELECTOR, self.selector).click()
		time.sleep(1) # just in case
		return self.DRIVER.get_screenshot_as_png()