import json

class ConfigReader:
    def __init__(self):
        with open("config.json", "r") as config_dict:
            self.__dict__ = json.load(config_dict)