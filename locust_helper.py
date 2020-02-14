from os.path import dirname
from os import path
import json

CONFIG_FOLDER = path.join(dirname(__file__))

def get_json_config(file_name):
  """
  Load config by config file name.

  Args:
    file_name(str): The config file name to load

  Returns:
    dict: The content defined in the config file
  """
  file_path = path.join(CONFIG_FOLDER, file_name)

  with open(file_path, "r") as file_handle:
    config_data = json.load(file_handle)
  return config_data
