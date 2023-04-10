import json
from os.path import join
from app import api
from app.utils import get_repository_name, write_json, read_json, create_if_not_exists
from abc import abstractmethod

class Api():
	_api: api.Api

	def __init__(self, name: str, api: api.Api = api.GitHubApi()) -> None:
		self.name = name
		self._api = api
		pass

	@abstractmethod
	def generate(self, config, path):
		'''
			Generates the api based on the config to the path.

			Args:
				config (dict): The config for the api
				path (str): The path where the api should be generated
		'''
		raise NotImplementedError

class ReleaseApi(Api):
	def __init__(self, api) -> None:
		super().__init__("release", api)
		pass
	
	def generate(self, config, path):
		path = join(path, 'release')

		repositories = config["repositories"]

		for repository in repositories:
			release = self._api.get_release(repository)
			repository_name = get_repository_name(repository)
			
			tag = release['tag']
			
			release_path = join(path, repository_name)
			release_json = json.dumps(release)
			
			create_if_not_exists(release_path)
			
			write_json(release_json, join(release_path, f'{tag}.json'), overwrite=False)
			write_json(release_json, join(release_path, 'latest.json'))  # Overwrite the latest release
				
			# At last join the current tag to an index file
			index_path = join(path, f'{repository_name}.json')
			
			index = read_json(index_path, [])
			if tag not in index: # TODO: Check if there a better way to do this
				index.append(tag) # Add the current tag to the index

			write_json(index, index_path)
		pass

class ContributorApi(Api):
	def __init__(self, api) -> None:
		super().__init__("contributor", api)
		pass

	def generate(self, config, path):
		path = join(path, 'contributor')

		create_if_not_exists(path)
		repositories = config["repositories"]

		for repository in repositories:
			repository_name = get_repository_name(repository)

			contributors = self._api.get_contributor(repository)
			contributors_path = join(path, f'{repository_name}.json')

			write_json(contributors, contributors_path)
		pass

class SocialApi(Api):
	def __init__(self, api) -> None:
		super().__init__("social", api)
		pass
	
	def generate(self, config, path):
		new_social = config
		
		social_path = join(path, f"social.json")
		social = read_json(social_path, new_social)

		write_json(social, social_path)
		pass

class ApiProvider():
	_apis: list[Api]

	def __init__(self, apis: list[Api]) -> None:
		self._apis = apis
		pass

	def get(self, name: str) -> Api:
		for api in self._apis:
			if api.name == name:
				return api

		return None

class DefaultApiProvider(ApiProvider):
	def __init__(self):
		self._api = api.GitHubApi() # Use GitHub as default api
		
		super().__init__([
			ReleaseApi(self._api), 
			ContributorApi(self._api), 
			SocialApi(self._api)]
		)
		pass