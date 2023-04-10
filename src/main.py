from app.config import load_config
from app.generator import DefaultApiProvider

config = load_config()

output = config['output']
apis = config['api']

api_provider = DefaultApiProvider()

for api in apis:
	types = api['type'].split('+')
	del api['type'] # Don't need the type for the api anymore below 
	for type in types:
		api_type = api_provider.get(type)
		if api_type is None: continue
		api_type.generate(api, output)