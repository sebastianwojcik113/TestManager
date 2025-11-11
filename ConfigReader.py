import json


class ConfigReader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.resources = {} #empty resources list

    def read_config(self):
        try:
            with open(self.config_file, 'r') as f:
                print(f"[INFO] Loading config file: {self.config_file}")
                data = json.load(f)
                if not data:
                    print(f"[ERROR] Config file is empty!")
                    return
                # Json file is a list with only one dict on position [0]
                self.resources = data[0]
                print(f"[INFO] Loaded resources: {list(self.resources.keys())}")
        except FileNotFoundError:
            print(f"[ERROR] Config file {self.config_file} not found!")
        except json.JSONDecodeError:
            print(f"[ERROR] Config file {self.config_file} is not valid JSON!")

    def get(self, resource):
        res = self.resources.get(resource)
        if res is None:
            print(f"[ERROR] Resource '{resource}' not found in config!")
        return res