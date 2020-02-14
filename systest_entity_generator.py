import json
import re
from os import path


class SystestEntityGenerator(object):
  """
  Class to generate entities_ops from api calls
  """

  def __init__(self, file_location):
    self.complete_json = json.loads(open(file_location, "r").read())
    self.get_calls = self.complete_json["get_calls"]
    self.api_data = self.complete_json["api_data"]

  def generate_entity_api_call_op(self, **kwargs):
    entity = kwargs.get("entity")
    call_type = kwargs.get("call_type")
    version = kwargs.get("version")
    url = kwargs.get("url")
    payload = kwargs.get("payload")
    # if entity file already exists, then append, else create new
    if path.exists("generate_" + entity + "_op.py"):
      outF = open("generate_" + entity + "_op.py", "a")
    else:
      outF = open("generate_" + entity + "_op.py", "w")
      outF.write(
        "from workflows.systest.entities.entity_op import EntityOp, ApiVersion\n\n")
      outF.write("class Generate" + entity.capitalize() + "Op(EntityOp):\n\n")
      outF.write("  def __init__(self):\n")
      outF.write("    pass\n\n")
    with open("generate_" + entity + "_op.py") as myfile:
      process = url.split('/')[-2]
      if "/" + process + "/" != url and call_type + "_" + entity + "_" + process + "(self)" not in myfile.read():
        self.getvalueofkeys(payload=payload)
        outF.write(
          "  def " + call_type + "_" + entity + "_" + process + "(self):\n\n")
        outF.write('    url ="' + url + '"\n')
        outF.write('    json = ' + str(payload) + '\n')
        outF.write(
          '    self._client.' + call_type + '(url=url, json=json, version=' + version + ')\n\n')
      elif call_type + "_" + entity + "(self)" not in myfile.read():
        self.getvalueofkeys(payload=payload)
        outF.write("  def " + call_type + "_" + entity + "(self):\n\n")
        outF.write('    url ="' + url + '"\n')
        outF.write('    json = ' + str(payload) + '\n')
        outF.write(
          '    self._client.' + call_type + '(url=url, json=json, version=' + version + ')\n\n')

  def get_data(self):
    # with open('/Users/rakesh.eshwar/PycharmProjects/har/10.53.54.227.har','r') as f:
    for each_dict in self.api_data:
      if each_dict["method"] == "GET":
        # self.outF.write("\n----------------------\nmethod for GET\n")
        self.data_for_get_call(each_dict)
      elif each_dict["method"] == "PUT":
        # self.outF.write("\n-----------------------\nmethod for PUT\n")
        self.data_for_put_call(each_dict)
      else:
        # self.outF.write("\n------------------------\nmethod for POST\n")
        self.data_for_post_call(each_dict)

  def data_for_get_call(self, each_dict):
    api_version, entity, url = self.get_api_version(each_dict['url'])
    entity = re.split('/|\\?', entity)[0]
    self.generate_entity_api_call_op(entity=entity, call_type="get",
                                     version=api_version, url=url,
                                     payload=each_dict["payload"])

  def data_for_put_call(self, each_dict):
    api_version, entity, url = self.get_api_version(each_dict['url'])
    entity = re.split('/|\\?', entity)[0]
    self.generate_entity_api_call_op(entity=entity, call_type="update",
                                     version=api_version, url=url,
                                     payload=each_dict["payload"])

  def data_for_post_call(self, each_dict):
    api_version, entity, url = self.get_api_version(each_dict['url'])
    entity = re.split('/|\\?', entity)[0]
    self.generate_entity_api_call_op(entity=entity, call_type="create",
                                     version=api_version, url=url,
                                     payload=each_dict["payload"])

  def get_api_version(self, api_call):
    url = "/"
    api_data_list = api_call.split("/")
    api_version_list = ['v0.8', 'v1', 'v2.0', 'v2', 'v3', 'v1_groups',
                        'v3_groups']
    api_data_set = set(api_data_list)
    api_version_set = set(api_version_list)
    version = list(api_data_set & api_version_set)[0]
    d_index = api_data_list.index(version)
    entity = api_data_list[d_index + 1]
    for i in range(d_index + 1, len(api_data_list)):
      url = url + api_data_list[i] + "/"
    return "ApiVersion." + version.replace(".", "_").upper(), entity, url

  def getvalueofkeys(self, **kwargs):
    list_of_get_vals = self.get_calls
    payload = kwargs.get("payload")
    listOfItems = payload.items()
    for tup_item in listOfItems:
      item = list(tup_item)
      if type(item[1]) is list:
        for i in item[1]:
          self.getvalueofkeys(payload=i)
      if str(item[1]).startswith("<get"):
        print item[0]
        get_full_list = str(item[1])[1:-1].split("#")
        get_check_element = get_full_list[-1]
        get_value = get_full_list[-2]
        get_full_list = get_full_list[1:-2]
        count = 0
        for i in get_full_list:
          if i.isdigit():
            list_of_get_vals = list_of_get_vals[count]
          else:
            list_of_get_vals = list_of_get_vals[i]
        list_of_get_vals = list_of_get_vals["entities"][0]
        if list_of_get_vals["name"] == get_check_element:
          payload[item[0]] = list_of_get_vals[get_value]
        else:
          count += 1

# a = ApiCallRecorder()
# a.get_data()
