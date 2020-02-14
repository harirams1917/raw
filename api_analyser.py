import re
import pprint
import copy
import json
from api_filter import ApiFilter
import time


class ApiAnalyser(object):
  def __init__(self, filtered_api):
    self._api_list = filtered_api["filtered_api"]
    self._get_details = filtered_api["get_calls"]

  def analyse_api(self):
    def parse_non_dict(data):
      if not isinstance(data, list):
        if isinstance(data, unicode) or isinstance(data, str):
          if re.match(r'((\w+\-){4}(\w+)\:\:\d+)', str(data)):
            uuid_match = re.match(r'((\w+\-){4}(\w+)\:\:\d+)', str(data))
            uuid_path = self.get_uuid_path(uuid_match.group(1))
            print "+" * 100
            print uuid_path
            print "+" * 100
            if uuid_path:
              return "<get#{}>".format(uuid_path)
            else:
              return data
          elif re.match(r'((\w+\-)+(\w+))', str(data)):
            uuid_match = re.match(r'((\w+\-)+(\w+))', str(data))
            uuid_path = self.get_uuid_path(uuid_match.group(1))
            if uuid_path:
              return "<get#{}>".format(uuid_path)
            else:
              return data
          else:
            return data
        elif isinstance(data, bool):
          return "<bool>#{}".format(data)
        elif isinstance(data, int):
          return "<int>#{}".format(data)
        elif isinstance(data, str):
          return "<str>#{}".format(data)
      else:
        data_list = []
        for element in data:
          if isinstance(element, dict):
            data_list.append(parse_dict(element))
          else:
            data_list.append(parse_non_dict(element))
        return data_list

    def parse_dict(json_dict):
      for key, value in json_dict.iteritems():
        if isinstance(value, dict):
          json_dict[key] = parse_dict(value)
        elif key.lower() == "name":
          json_dict[key] = "<str>#{}".format(value)
        else:
          json_dict[key] = parse_non_dict(value)
      return json_dict

    analysed_api_list = []
    for api in self._api_list:
      temp_dict = copy.deepcopy(api)
      if api.get("payload"):
        pprint.pprint(api.get("payload"))
        temp_dict["payload"] = parse_dict(api.get("payload"))
      if api.get("response"):
        try:
          response_text = json.loads(api["response"]["content"]["text"])
          if response_text.get("task_uuid"):
            # temp_dict.pop("response")
            temp_dict["wait_for_task"] = True
          else:
            # temp_dict.pop("response")
            temp_dict["wait_for_task"] = False
        except:
          continue

      if api.get("url"):
        if re.search(r'((\w+\-)+(\w+))', str(api.get('url'))):
          value = re.search(r'((\w+\-)+(\w+))', str(api.get('url')))
          print value
          uuid = value.group(1)
          print uuid
          replace_data = self.get_uuid_path(uuid)
          print replace_data
          temp_dict["url"] = re.sub(r'((\w+\-)+(\w+))',
                                    "<get#{}>".format(replace_data),
                                    str(api.get('url')))
          print temp_dict["url"]
      pprint.pprint(temp_dict)
      analysed_api_list.append(temp_dict)
    file_name = "{}_{}.json".format("input_data", int(time.time()))
    har_file = open(file_name, 'w')
    har_file.write(json.dumps(
      {"api_data": analysed_api_list, "get_calls": self._get_details}))
    return file_name

  def get_uuid_path(self, uuid):
    # pprint.pprint(self._get_details)
    for entity, data in self._get_details.iteritems():
      for call in data:
        for entry in call["entities"]:
          if uuid in entry.values():
            for key, value in entry.iteritems():
              if value == uuid:
                name = entry.get("name")
                if not name:
                  name = entry.get("vmName")
                return "{}#{}#{}#{}".format(entity, data.index(call),
                                            key, name)
    return None


if __name__ == '__main__':
  api = ApiFilter(
    '/Users/hari.ramachandran/PycharmProjects/raw/sniffer/rar_har_1581430135.har',
    "10.46.208.36")
  api_list = api.api_filter()
  obj = ApiAnalyser(filtered_api=api_list)
  obj.analyse_api()
