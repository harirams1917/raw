import json
from selenium import webdriver
import time
from browsermobproxy import Server
import threading
from api_filter import ApiFilter
import time


class ProxyManager():
  __BMP = "/Users/hari.ramachandran/PycharmProjects/raw/utils/bin/browsermob-proxy.bat"
  STOP = False

  def __init__(self):
    self.__server = Server(ProxyManager.__BMP)
    self.__client = None
    self._thread = None
    self.stop = False
    self.har_file_name = None

  def start_server(self):
    self.__server.start()
    return self.__server

  def start_client(self):
    self.__client = self.__server.create_proxy(
      params={"trustAllServers": "true"})
    return self.__client

  @property
  def client(self):
    return self.__client

  @property
  def server(self):
    return self.__client

  def sniff_api(self, host=None, port=9440):
    server = self.start_server()
    client = self.start_client()
    client.new_har("https://{}:{}".format(host, port),
                   options={"captureHeaders": "true", "captureContent": "true"})
    options = webdriver.ChromeOptions()
    options.add_argument("--proxy-server={}".format(client.proxy))
    driver = webdriver.Chrome(chrome_options=options)
    driver.get("https://{}:{}".format(host, port))
    while self.stop == False:
      time.sleep(1)
    self.har_file_name = "raw_har_{}".format(int(time.time()))
    har_data = json.dumps(client.har, indent=4)
    har_file = open("{}.har".format(self.har_file_name), 'w')
    # print type(client.har)
    # print client.har
    har_file.write(har_data)
    har_file.close()
    server.stop()
    driver.quit()
    # valid_apis = self.get_valid_api()


  def stop_sniffing(self):
    self.stop = True

  def get_valid_api(self):
    filterer = ApiFilter(har_file="{}.har".format(self.har_file_name),
                         mouse_listener=None)
    return filterer.api_filter()

  def segregate_api(self,valid_apis):
    pass


if __name__ == '__main__':
  obj = ProxyManager()
  val = threading.Thread(target=obj.sniff_api, args=("10.46.241.64", "9440",))
  val.start()
  time.sleep(30)
  obj.stop_sniffing()
  val.join()
