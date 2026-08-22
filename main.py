import os
import sys
import requests
import time
from dotenv import load_dotenv



class MyGithubStats:

    USERNAME    : str = 'olivercalazans'
    TOTAL_LANGS : int = 10
    HEADERS     : str = ''

    def __init__(self):
        self._repos               : list[dict]     = []
        self._len_repos           : int            = 0
        self._stars               : int            = 0
        self._commits             : int            = 0
        self._lang_bytes          : dict[str, int] = {}
        self._total_contributions : int            = 0
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
            MyGithubStats._fatal('Unable to get token')
    
        return token



    @staticmethod
    def _fatal(err: str):
        print(f'[ ERROR ] {err}')
        sys.exit(1)



    def execute(self):
        try:
            self._get_data()
            self._process_data()
            self._display()
        except Exception as e:
            self._fatal(str(e))



    def _get_data(self):
        self._get_repo_basic_data()
        self._get_repo_langs_and_commits()
        self._get_total_contributions()



    def _get_repo_basic_data(self):
        PER_PAGE = 100
        page     = 1
        URL      = f'https://api.github.com/users/{self.USERNAME}/repos'

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

            self._repos.extend(repos)
            page += 1

            if len(repos) < PER_PAGE: break



    def _get_repo_langs_and_commits(self):
        for idx, repo in enumerate(self._repos, 1):
            repo_name = repo['name']
            print(f'  ({idx}/{len(self._repos)}) Processing {repo_name}...')

            self._get_repo_lang_bytes(repo_name)         
            self._get_repo_commits(repo_name)   



    def _get_repo_lang_bytes(self, repo_name: str):
        lang_url = f'https://api.github.com/repos/{self.USERNAME}/{repo_name}/languages'
        response = requests.get(lang_url, headers=self.HEADERS)

        if response.status_code != 200:
            print(f' Unable to get {repo_name} language: {response.status_code}')
            return

        langs: dict = response.json()
        for lang, bytes_count in langs.items():
            self._lang_bytes[lang] = self._lang_bytes.get(lang, 0) + bytes_count



    def _get_repo_commits(self, repo_name: str):
        RETRYS      = 3
        commits_url = f'https://api.github.com/repos/{self.USERNAME}/{repo_name}/stats/contributors'

        for _ in range(RETRYS):
            response = requests.get(commits_url, headers=self.HEADERS)

            if response.status_code == 202:
                time.sleep(2)
                continue

            if response.status_code == 200:
                contributors   = response.json()
                total_commits  = sum(c['total'] for c in contributors)
                self._commits += total_commits
                return

        print(f'Unable to get {repo_name} commits after {RETRYS} retrys: {response.status_code}')



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
        
        variables = {"username": self.USERNAME}
        response  = requests.post(
            GRAPHQL_URL, 
            json={'query': query, 'variables': variables}, 
            headers=self.HEADERS
        )
        
        if response.status_code != 200:
            print(f"Unable to get contributions via GraphQL: {response.status_code}")
            return

        try:
            data = response.json()
            self._total_contributions = int(data['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions'])
        except (Exception, KeyError, TypeError) as e:
            print(f'Unable to get total contributions: {e}')



    def _process_data(self):
        if len(self._repos) == 0:
            self._fatal('No repository found')

        self._len_repos = len(self._repos)
        self._get_stars()



    def _get_stars(self):
        for repo in self._repos:
            self._stars += repo.get('stargazers_count', 0)



    def _process_langs(self):
        sorted_langs = sorted(self._lang_bytes.items(), key=lambda x: x[1], reverse=True)
        total_bytes  = sum(self._lang_bytes.values())

        if total_bytes == 0:
            print('No language found')
            return

        for lang, bytes_count in sorted_langs[:self.TOTAL_LANGS]:
            pct = (bytes_count / total_bytes) * 100
            print(f'lang {lang}: {pct:.2f}%')
            


    def _display(self):
        print(f'repos: {self._len_repos}')
        print(f'stars: {self._stars}')
        print(f'commits: {self._commits}')
        print(f'contributions: {self._total_contributions}')
        self._process_langs()        




if __name__ == '__main__':
    x = MyGithubStats()
    x.execute()
    sys.exit(0)