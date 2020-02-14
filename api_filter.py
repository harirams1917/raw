import ast
import json
import iso8601
import time
import pprint
import re


class ApiFilter(object):
  VALID_METHODS = ["POST", "PUT", "DELETE"]
  SKIP_URL = ["PrismGateway/services/rest/v1/utils/filter_counts",
              "PrismGateway/services/rest/v1/groups", "/api/nutanix/v3/batch",
              "PrismGateway/j_spring_security_check",
              "PrismGateway/services/rest/v1/click_stream_logs",
              "http://update.googleapis.com/service/update2/json"]

  def __init__(self, har_file, ip=None):
    self.har_file = har_file
    self.ip = ip
    self.filtered_api = []
    self.get_calls = []

  def api_filter(self):
    with open(self.har_file, 'r') as har_json:
      har_parser = json.loads(har_json.read())
      if har_parser.get("log"):
        if har_parser["log"].get("entries"):
          for entry in har_parser["log"]["entries"]:
            d1 = iso8601.parse_date(entry.get('startedDateTime'))
            unix_utc_ts = time.mktime(d1.timetuple())
            if entry["request"]["method"] in self.VALID_METHODS:
              if ("/".join(
                  entry["request"]["url"].split("/")[3::]) in self.SKIP_URL) or \
                  entry["request"]["url"] in self.SKIP_URL or "google" in \
                  entry["request"]["url"]:
                continue
              parsed_api_data = {}
              parsed_api_data.update({'startedDateTime': unix_utc_ts})
              parsed_api_data.update({'method': entry["request"]["method"]})
              parsed_api_data.update({'url': entry["request"]["url"]})
              if 'postData' in entry.get('request'):
                if 'text' in entry.get('request').get('postData'):
                  try:
                    parsed_api_data.update({'payload': ast.literal_eval(
                      entry["request"]["postData"].get("text"))})
                  except:
                    try:
                      parsed_api_data.update({'payload': json.loads(
                        entry["request"]["postData"].get(
                          "text"))})
                    except:
                      pass
              parsed_api_data.update({'response': entry.get('response')})
              self.filtered_api.append(parsed_api_data)
    return ({"filtered_api": self.filtered_api,
             "get_calls": self.segregate_get_methods()})

  def segregate_get_methods(self):
    segregatted_get_calls = {}
    with open(self.har_file, 'r') as har_json:
      har_parser = json.loads(har_json.read())
      if har_parser.get("log"):
        if har_parser["log"].get("entries"):
          for entry in har_parser["log"]["entries"]:
            if entry["request"]["method"] == "GET":
              if self.ip in str(entry["request"]["url"]):
                str_url = str(entry["request"]["url"])
                actual_url = str_url.split("?")[0]
                uuid_search = re.search(r'((\w+\-){4}(\w+))', actual_url)
                if uuid_search:
                  # print actual_url
                  key = uuid_search.group(1)
                else:
                  key = actual_url.split("/")[-1]
                  # if key == "vms":
                  #   print actual_url
                  #   print json.loads(
                  #     entry.get('response').get("content").get("text"))
                parsed_api_data = {}
                parsed_api_data.update({'method': entry["request"]["method"]})
                parsed_api_data.update({'url': entry["request"]["url"]})
                if entry.get('response'):
                  if entry["response"].get("content"):
                    if entry["response"]["content"].get("text"):
                      try:
                        parsed_data = ast.literal_eval(
                          entry["response"]["content"].get("text"))
                        for entity in parsed_data.get("entities"):
                          if entity.get("name") or entity.get("vmName"):
                            parsed_api_data.update(
                              {"entities": parsed_data.get("entities")})
                            continue
                      except:
                        try:
                          parsed_data = json.loads(
                            entry["response"]["content"].get("text"))
                          if parsed_data.get("entities"):
                            for entity in parsed_data.get("entities"):
                              if entity.get("name") or entity.get("vmName"):
                                parsed_api_data.update(
                                  {"entities": parsed_data.get("entities")})
                                continue
                        except:
                          continue
                if segregatted_get_calls.get(key) and parsed_api_data.get(
                    "entities"):
                  segregatted_get_calls[key].append(parsed_api_data)
                elif parsed_api_data.get("entities"):
                  segregatted_get_calls[key] = [parsed_api_data]

          return segregatted_get_calls
          # pprint.pprint(segregatted_get_calls)


if __name__ == '__main__':
  api = ApiFilter(
    '/Users/hari.ramachandran/PycharmProjects/raw/sniffer/rar_har_1581430135.har',
    "10.46.208.36")
  api_list = api.segregate_get_methods()
