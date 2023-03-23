import os
import sys
import json
from json import JSONDecodeError

SEVER_ABS_PATH = os.path.dirname(sys.argv[0]) + "/"
CONFIG_FILE_PATH = SEVER_ABS_PATH + "config.json"


class Configuration:
    def __init__(self, config_path, logger=None):
        self.__config_path = config_path
        self.__logger = logger

        self.__config = None
        self.__load_config()

    def __log(self, str_log):
        if self.__logger is not None:
            self.__logger.log(str(str_log))
        else:
            print(str_log)

    def __load_config(self):
        try:
            with open(self.__config_path, encoding="utf-8") as conf_file_handle:
                self.__config = json.load(conf_file_handle)
        except FileNotFoundError as e:
            self.__log("\nConfiguration file does not exist\n")
            self.__log(e)
        except JSONDecodeError as e:
            self.__log("\nConfiguration file is corrupted\n")
            self.__log(e)

    def _save_config(self):
        if self.__config is None:
            print("config is None")
            return None

        with open(self.__config_path, "w+", encoding="utf-8") as conf_file_handle:
            json.dump(self.__config, conf_file_handle, indent=4, ensure_ascii=False)

    def check(self):
        if self.__config is None:
            return False
        return True

    def get_key(self, key, prefix=None, default=None):
        if prefix is None:
            # print(self.__config)
            if key in self.__config:
                return self.__config.get(key)
            else:
                return default
        else:
            if prefix not in self.__config:
                return default
            if key not in self.__config.get(prefix):
                return default
            return self.__config.get(prefix).get(key)

    def alt_key(self, key, value, prefix=None):
        if self.__config is None:
            print("config is None")
            return None

        if prefix is not None:
            if prefix not in self.__config:
                self.__config[prefix] = {}
            self.__config[prefix][key] = value
        else:
            self.__config[key] = value
        self._save_config()
