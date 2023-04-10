from abc import abstractmethod

import requests

class Api():
	_api_key: str
	
	@abstractmethod
	def __init__(self, api_key: str = None) -> None:
		self._api_key: str = api_key
	
	@abstractmethod
	def get_release(self, repository: str, all: bool = False, prerelease: bool = False) -> dict | list:
		'''Gets the release(s) for a repository.

		Args:
			repository (str): The repository to get releases for.
			all (bool, optional): Whether to get all releases or not. Defaults to False.
			prerelease (bool, optional): Whether to get prereleases or not. Defaults to False.
		Returns:
			dict | list: The release(s) for the repository.
		'''
		raise NotImplementedError
	
	@abstractmethod
	def get_contributor(self, repository):
		'''Gets the contributors for a repository.

		Args:
			repository (str): The repository to get contributors for.
		'''
		raise NotImplementedError

class GitHubApi(Api):
	def __init__(self) -> None:
		pass

	def get_contributor(self, repository):
		def transform_contributor(contributor: dict) -> dict:
			'''Transforms a contributor into a dict.

			Args:
				contributor (dict): The contributor to transform.

			Returns:
				dict: The transformed contributor.
			'''

			return {
				'username': contributor['login'],
				'avatar': contributor['avatar_url'], # TODO: Proxy via a CDN.
				'link': contributor['html_url'],
				'contributions': contributor['contributions']
			}

		def sort_and_delete_key(contributor: dict) -> int:
			contributions = contributor['contributions']
			del contributor['contributions']
			return contributions

		contributors = requests.get(f'https://api.github.com/repos/{repository}/contributors').json()
		contributors = list(map(transform_contributor, contributors)) # List might not be needed.
		contributors.sort(key=sort_and_delete_key, reverse=True)

		return contributors

	def get_release(self, repository: str, all: bool = False, prerelease: bool = False) -> dict | list:
		def transform_release(release: dict) -> dict:
			'''Transforms a release dict into a dict.

			Args:
				release (dict): The release dict to transform.

			Returns:
				dict: The transformed release dict.
			'''

			return {
				# TODO: Check if theres any need for this: 'id': release['id'].
				'tag': release['tag_name'],
				'prerelease': release['prerelease'],
				'published_at': release['published_at'],
				'assets': [
					{
						'name': asset['name'],
						'download_url': asset['browser_download_url'] # TODO: Proxy via a CDN.
					} for asset in release['assets']
				]
			}

		# A little bit of code duplication but more readable than a ternary operation.
		if all:
			releases: list = requests.get(f'https://api.github.com/repos/{repository}/releases').json()
			return list(map(transform_release, releases)) # List might not be needed.
		else:
			latest_release: object = requests.get(f'https://api.github.com/repos/{repository}/releases/latest?prerelease={prerelease}').json()
			return transform_release(latest_release)
