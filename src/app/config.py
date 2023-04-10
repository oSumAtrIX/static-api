import json

def load_config() -> dict:
	with open('config.json', 'r') as config_file:
		return json.load(config_file)
