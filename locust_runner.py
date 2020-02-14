from locust import TaskSet, task
import time
from locust_helper import get_json_config
import json
import re
import requests
import pprint


class RawTest(TaskSet):
  """
    Perform operations on the task page in PC
  """
  FUNCTION_MAP = {"<str>": str,
                  "<int>": int,
                  "<bool>": bool}

  def __init__(self, file_name=None):
    self.file_name = file_name
    if not self.file_name:
      self.file_name = "input_data_1.json"

  def on_start(self):
    """
    on_start is called when a Locust start before any task is scheduled
    Args:
       None
    """
    self.client.auth = ('admin', 'Nutanix.123')
    self.client.verify = False
    self.client.headers = {'content-type': 'application/json'}
    self._witness_uuid = ""

  @task(1)
  def taskpage(self):
    """
      Perform operations on the task page in PC
    """
    self.tasks_ro_ops()

  def tasks_ro_ops(self):
    """
      Perform operations on the task page in PC
    """
    config = get_json_config(self.file_name)
    self.get_data = {}
    self.get_calls = []
    self.get_call_name = {}
    self.delete_dict = {}
    self.execute_locust(config)

  def execute_locust(self, locust_config):
    """
      Make rest calls from default config in the config file

      Args:
        config(str): The config file name to load
        entity(str): Entity type

      Returns:
        None
    """
    self.get_calls_list = locust_config.get("get_calls")
    api_to_run = locust_config.get("api_data")
    for api in api_to_run:
      self.generate_calls(api)

  def generate_calls(self, api):
    payload = api.get("payload")
    # print payload
    if payload:
      json = self.parse_dict(payload)
      call_url = ""
      if re.search((r'<get#'), api.get("url")):
        url_split = api.get("url").split("/")
        for split_data in url_split:
          if "<get#" in split_data:
            new_uuid = self.get_value(
              self.get_calls[self.get_get_calls(split_data)])
            index = url_split.index(split_data)
            url_split[index] = new_uuid
            call_url = "/".join(url_split[3::])
            del_url = "/".join(url_split[3:index + 1:])
            self.delete_dict[new_uuid] = del_url
      else:
        call_url = "/".join(api.get("url").split("/")[3::])

      response = self.client.get(url=call_url, verify=False)
      if response.status_code == 200:
        resp = response.json()
        for entity in resp["entities"]:
          if payload["name"] in entity.values():
            return

      print "+" * 100
      print json
      print "+" * 100

      if json.get("vm_disks"):
        json.pop("vm_disks")

      if api.get("wait_for_task"):
        response = self.client.post(url=call_url, json=json, verify=False)
        if response:
          task_details = response.json()
          if task_details.get("task_uuid"):
            self.wait_for_task(task_details.get("task_uuid"))
      else:
        self.client.post(url=call_url, json=json, verify=False)

      if self.delete_dict:
        for uuid, url in self.delete_dict.iteritems():
          self.client.delete(url=url)
          self.delete_dict.pop(uuid)

  def get_get_calls(self, map_string):
    if "None" in map_string:
      return
    temp_dict = {}
    splitted_value = [str(val) for val in map_string.split("#")]
    url = \
      self.get_calls_list[splitted_value[1]][int(splitted_value[2])][
        "url"].split(
        "?")[
        0]
    val = url.split("/")
    temp_dict["url"] = "/".join(val[3::])
    # print url
    # response = requests.get(url.split("?")[0], auth=('admin', 'Nutanix.123'),
    #                         headers={'Content-Type': 'application/json'},
    #                         verify=False)
    # print response.json()
    if "default-storage-pool" in splitted_value[-1].replace(">", ""):
      temp_dict["name"] = "default-storage-pool"
      temp_dict["find"] = True
    else:
      temp_dict["name"] = splitted_value[-1].replace(">", "")
    temp_dict["key"] = splitted_value[-2]
    if temp_dict:
      self.get_calls.append(temp_dict)
      return self.get_calls.index(temp_dict)

  def get_formatted_value(self, value):
    splitted_list = value.split('#')
    func = self.FUNCTION_MAP[str(splitted_list[0])]
    return func(splitted_list[1])

  def parse_non_dict(self, data):
    if not isinstance(data, list):
      if isinstance(data, unicode):
        if "<get#" in str(data):
          try:
            return self.get_value(self.get_calls[self.get_get_calls(data)])
          except:
            return None
        else:
          return data
      elif re.match(r'<\w+>\#\w+', str(data)):
        return self.get_formatted_value(data)
    else:
      data_list = []
      for element in data:
        if isinstance(element, dict):
          data_list.append(self.parse_dict(element))
        else:
          data_list.append(self.parse_non_dict(element))
      return data_list

  def parse_dict(self, json_dict):
    for key, value in json_dict.iteritems():
      if isinstance(value, dict):
        json_dict[key] = self.parse_dict(value)
      elif re.match(r'<\w+>\#\w+', str(value)):
        json_dict[key] = self.get_formatted_value(value)
      else:
        json_dict[key] = self.parse_non_dict(value)
    return json_dict

  def get_value(self, data):
    # return "eeb31974-a5b2-44f5-8c3d-b97b69ce696a"
    response = self.client.get(url=data["url"], verify=False)
    if response.status_code == 200:
      resp = response.json()

      for entity in resp["entities"]:
        if data.get("find"):
          if data["name"] in entity["name"]:
            print "Entity in get_value:{}".format(entity[data["key"]])
            return entity[data["key"]]
        else:
          if entity.get("name") == data["name"] or entity.get("vmName") == data[
            "name"]:
            print "Entity in get_value:{}".format(entity[data["key"]])
            return entity[data["key"]]

  def wait_for_task(self, uuid):
    url = "PrismGateway/services/rest/v1/progress_monitors?filterCriteria=(status==kRunning)"

    def check_status():
      response = self.client.get(url=url)
      if response.status_code == 200:
        resp = response.json()
        for entity in resp["entities"]:
          if entity.get('id') == uuid:
            time.sleep(5)
            check_status()
      else:
        return

    check_status()

# obj = RawTest()
# obj.tasks_ro_ops()
