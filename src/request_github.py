# Copyright (C) 2026 Oliver Calazans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import requests
import time
from data   import Data
from dotenv import load_dotenv
from utils  import fatal, warning



class Fetcher:

    RETRY = 3

    __slots__ = ('data', 'HEADERS')

    def __init__(self, data: Data):
        self.data    : Data = data
        self.HEADERS : dict = None
        self._set_headers()



    def _set_headers(self): 
        token = self._get_token()
        self.HEADERS = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
        }



    @staticmethod
    def _get_token() -> str:
        load_dotenv()
        token = os.getenv('GITHUB_TOKEN')
    
        if not token:
            fatal('Unable to get token')
    
        return token



    def fetch_data(self):
        try:
            self._get_data()
            self._valid_len_repos()
            self._process_data()
            #self._display()
        except Exception as e:
            fatal(str(e))



    def _get_data(self):
        self._get_repo_basic_data()
        self._get_repo_langs_and_commits()
        #self._get_total_contributions()



    def _get_repo_basic_data(self):
        PER_PAGE = 100
        page     = 1
        URL      = f'https://api.github.com/users/{self.data.USERNAME}/repos'

        while True:
            params = {
                'type': 'public',
                'sort': 'updated',
                'per_page': PER_PAGE,
                'page': page,
            }

            response = requests.get(URL, headers=self.HEADERS, params=params)
            response.raise_for_status()
            repos = response.json()

            if not repos: break

            self.data.repos.extend(repos)
            page += 1

            if len(repos) < PER_PAGE: break



    def _valid_len_repos(self):
        len_repos = len(self.data.repos)
        
        if len_repos == 0:
            fatal('No repository found')
        
        self.data.len_repos = len_repos



    def _get_repo_langs_and_commits(self):
        for idx, repo in enumerate(self.data.repos, 1):
            repo_name = repo['name']
            print(f'({idx}/{self.data.len_repos}) Processing {repo_name}...')

            self._get_repo_lang_bytes(repo_name)         
            self._get_repo_commits(repo_name)   



    def _get_repo_lang_bytes(self, repo_name: str):
        lang_url = f'https://api.github.com/repos/{self.data.USERNAME}/{repo_name}/languages'

        for i in range(1, self.RETRY + 1):
            response = requests.get(lang_url, headers=self.HEADERS)

            if response.status_code != 200:
                warning(f"  - {i}/{self.RETRY} attempt failed. Response code: {response.status_code}")
                time.sleep(2)
                continue

            langs: dict = response.json()
            for lang, bytes_count in langs.items():
                self.data.lang_bytes[lang] = self.data.lang_bytes.get(lang, 0) + bytes_count
                return

        fatal(f'Unable to get {repo_name} language')



    def _get_repo_commits(self, repo_name: str):
        commits_url   = f'https://api.github.com/repos/{self.data.USERNAME}/{repo_name}/stats/contributors'

        for i in range(1, self.RETRY + 1):
            response = requests.get(commits_url, headers=self.HEADERS)

            if response.status_code != 200:
                warning(f"  {i}/{self.RETRY} attempt failed. Response code: {response.status_code}")
                time.sleep(2)
                continue

            contributors  = response.json()
            total_commits = sum(c['total'] for c in contributors)

            self.data.total_commits += total_commits
            return

        fatal(f'Unable to get {repo_name} commits')



    def _get_total_contributions(self):
        GRAPHQL_URL = "https://api.github.com/graphql"
        
        query = """
            query($username: String!) {
              user(login: $username) {
                contributionsCollection {
                  contributionCalendar {
                    totalContributions
                  }
                }
              }
            }
            """
        
        variables = {"username": self.data.USERNAME}
        response  = requests.post(
            GRAPHQL_URL, 
            json={'query': query, 'variables': variables}, 
            headers=self.HEADERS
        )
        
        if response.status_code != 200:
            warning(f"Unable to get contributions via GraphQL: {response.status_code}")
            return

        try:
            data = response.json()
            self.data.total_contributions = int(data['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions'])
        except (Exception, KeyError, TypeError) as e:
            warning(f'Unable to get total contributions: {e}')



    def _process_data(self):
        self._get_stars()



    def _get_stars(self):
        for repo in self.data.repos:
            self.data.total_stars += repo.get('stargazers_count', 0)
            


    def _display(self):
        print(f'repos: {self.data.len_repos}')
        print(f'stars: {self.data.total_stars}')
        print(f'commits: {self.data.total_commits}')
        print(f'contributions: {self.data.total_contributions}')

