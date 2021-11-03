#!/usr/bin/python3
import unittest
from selenium import webdriver
from selenium.webdriver import firefox
from selenium.webdriver.firefox import service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from prettytable import from_html_one
import time
import os

class InfraSmokeTests(unittest.TestCase):

    def setUp(self):
        self.openvidu_url = os.getenv('OV_URL')
        self.openvidu_password = os.getenv('OV_SECRET')
        self.driver = None

    def test_inspector(self):
        self.inspector_check(browser="chrome")
        self.inspector_check(browser="firefox")
        self.inspector_check(browser="firefox", turn=True)

    def inspector_check(self, browser="chrome", turn=False):
        print('\n\n======================================================================')
        print('|')
        print('|')
        print('|   Testing OpenVidu with ' + browser + ' and force relay: ' + str(turn))
        print('|')
        print('|')
        print('======================================================================')
        if self.openvidu_url == None or self.openvidu_password == None:
            raise(Exception("You must specify OV_URL and OV_SECRET environment variables"))
        if browser == "chrome":
            self.runChrome()
        else:
            self.runFirefox(turn)

        url_test = self.openvidu_url + '/inspector'
        self.driver.get(url_test)

        elem = self.driver.find_element(By.ID, 'secret-input')
        elem.send_keys(self.openvidu_password)

        elem = self.driver.find_element(By.ID, 'login-btn')
        elem.send_keys(Keys.RETURN)

        # print('data:image/png;base64,' + self.driver.get_screenshot_as_base64())
        elem = self.driver.find_element(By.ID,'menu-test-btn')
        elem.send_keys(Keys.RETURN)

        elem = self.driver.find_element(By.ID,'test-btn')
        elem.send_keys(Keys.RETURN)

        video_error = False
        try:
            self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Stream playing')]")
        except:
            video_error = True
        finally:
            # print('data:image/png;base64,' + self.driver.get_screenshot_as_base64())
            if browser == "firefox":
                self.print_candidates()

        if video_error == True:
            raise Exception('Error. No video detected')

        print('Video detected.\n')
        elem = self.driver.find_element(By.ID,'test-btn')
        elem.send_keys(Keys.RETURN)

        self.closeBrowser()
        print('Sucess with ' + browser + ' and Force Turn: ' + str(turn) + '\n')
        print('----------------------------------------------------------------------\n')

    def runChrome(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--use-fake-ui-for-media-stream")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--use-fake-device-for-media-stream")
        self.options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options = self.options)
        self.driver.implicitly_wait(15)

    def runFirefox(self, turn=False):
        print("Running firefox with Turn: ", turn)
        self.options = webdriver.FirefoxOptions()
        self.options.set_preference('media.navigator.permission.disabled', False)
        self.options.set_preference('media.navigator.streams.fake', True)
        self.options.set_preference('media.peerconnection.enabled', True)
        self.options.set_preference('media.peerconnection.ice.obfuscate_host_addresses', False)
        self.options.set_preference('media.peerconnection.identity.enabled', True)
        self.options.set_preference('media.peerconnection.mtransport_process', True)
        self.options.set_preference('media.peerconnection.ice.no_host', False)
        self.options.set_preference('network.process.enabled', True)
        self.options.set_preference('media.peerconnection.ice.relay_only', turn)
        self.options.set_preference('media.peerconnection.turn.disable', not turn)

        self.driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options = self.options)
        self.driver.implicitly_wait(5)
        self.driver.maximize_window()

    def print_candidates(self):
        try:
            # New tab
            self.driver.execute_script("window.open('');")
            # Switch to the new window
            self.driver.switch_to.window(self.driver.window_handles[1])
                    # Open about:webrtc
            self.driver.get('about:webrtc')
            peer_conn_elems = self.driver.find_elements(By.CLASS_NAME, "peer-connection")
            for peer_conn in peer_conn_elems:
                show_details_elems = peer_conn.find_elements(By.XPATH, "//*[contains(text(), 'show details')]")
                for show_details in show_details_elems:
                    show_details.click()

            print("Waiting for candidates to be checked...")
                    # Get ice stats
            time.sleep(15)
            ice_stats_div_elems = self.driver.find_elements(By.XPATH, "//div[contains(@id, 'ice-stats')]")
            for ice_stats_div in ice_stats_div_elems:
                table_elems = ice_stats_div.find_elements(By.TAG_NAME, 'table')
                ice_candidates_table = table_elems[0]
                html_ice_table = '<table>' + ice_candidates_table.get_attribute('innerHTML') + '</table>'
                print(from_html_one(html_ice_table))
            # Go to main window
            self.driver.switch_to.window(self.driver.window_handles[0])
        except:
            print('Error getting candidates')

    def closeBrowser(self):
        # close the browser window
        self.driver.close()
        self.driver.quit()

if __name__ == '__main__':
    unittest.main()
