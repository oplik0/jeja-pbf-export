import json
def parse_config(config_file_name):
    with open(config_file_name+".json") as config_file:
        config = json.load(config_file)
    return config

if __name__=="__main__":
    print(parse_config("config"))