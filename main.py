import os
import sys
import requests
import time
from dotenv   import load_dotenv
from datetime import datetime, timezone, timedelta



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
        date = MyGithubStats._get_datetime()
        print(f'{date} [ ERROR ] {err}')
        sys.exit(1)



    @staticmethod
    def _warning(msg: str):
        date = MyGithubStats._get_datetime()
        print(f'{date} {msg}')



    @staticmethod
    def _get_datetime() -> str:
        brazilian_time = timezone(timedelta(hours=-3))
        time_now       = datetime.now(timezone.utc).astimezone(brazilian_time)
        str_formated   = time_now.strftime('%Y-%m-%d %H:%M:%S')

        return f'[ {str_formated} ]'



    def execute(self):
        try:
            self._get_data()
            self._process_data()
            #self._display()
            self._generate_languages_svg()
        except Exception as e:
            self._fatal(str(e))



    def _get_data(self):
        self._get_repo_basic_data()
        self._get_repo_langs_and_commits()
        #self._get_total_contributions()



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
            self._warning(f' Unable to get {repo_name} language: {response.status_code}')
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

        self._warning(f'Unable to get {repo_name} commits after {RETRYS} retrys: {response.status_code}')



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
            self._warning(f"Unable to get contributions via GraphQL: {response.status_code}")
            return

        try:
            data = response.json()
            self._total_contributions = int(data['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions'])
        except (Exception, KeyError, TypeError) as e:
            self._warning(f'Unable to get total contributions: {e}')



    def _process_data(self):
        if len(self._repos) == 0:
            self._fatal('No repository found')

        self._len_repos = len(self._repos)
        self._get_stars()



    def _get_stars(self):
        for repo in self._repos:
            self._stars += repo.get('stargazers_count', 0)
            


    def _display(self):
        print(f'repos: {self._len_repos}')
        print(f'stars: {self._stars}')
        print(f'commits: {self._commits}')
        print(f'contributions: {self._total_contributions}')



    LANG_COLORS = {
        'Python'     : '#3572A5',
        'JavaScript' : '#f1e05a',
        'TypeScript' : '#3178c6',
        'HTML'       : '#e34c26',
        'CSS'        : '#563d7c',
        'Shell'      : '#89e051',
        'Java'       : '#b07219',
        'C++'        : '#f34b7d',
        'C#'         : '#178600',
        'PHP'        : '#4F5D95',
        'Go'         : '#00ADD8',
        'TeX'        : '#3D6117',
        'PowerShell' : '#012456'
    }

    DEFAULT_COLOR = '#8b949e'



    def _generate_languages_svg(self):
        sorted_langs = sorted(self._lang_bytes.items(), key=lambda x: x[1], reverse=True)
        total_bytes  = sum(self._lang_bytes.values())

        if total_bytes == 0:
            self._warning("No language found for SVG generation")
            return

        width      = 300
        height     = 160
        bar_height = 10
        x_offset   = 20
        y_offset   = 50

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
            '  <style>',
            '    text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 12px; fill: #c9d1d9; }',
            '    .title { font-weight: 600; font-size: 14px; fill: #58a6ff; }',
            '  </style>',
            '  <!-- Fundo do GitHub Dark (sem bordas) -->',
            '  <rect width="100%" height="100%" rx="6" fill="#0d1117"/>',
            '  <!-- Título -->',
            f'  <text x="{x_offset}" y="30" class="title">Most Used Languages</text>',
            '  <!-- Barra de Progresso Segmentada -->',
            f'  <svg x="{x_offset}" y="{y_offset}" width="{width - (x_offset * 2)}" height="{bar_height}">',
        ]

        # 1. Construir a barra segmentada
        current_x = 0
        top_langs = sorted_langs[:self.TOTAL_LANGS]
        
        bar_parts    = []
        legend_parts = []
        
        legend_y      = y_offset + bar_height + 25
        max_bar_width = width - (x_offset * 2)

        for idx, (lang, bytes_count) in enumerate(top_langs):
            pct = (bytes_count / total_bytes) * 100

            if pct < 0.1:
                continue
                
            color         = self.LANG_COLORS.get(lang, self.DEFAULT_COLOR)
            segment_width = (pct / 100) * max_bar_width

            bar_parts.append(
                f'    <rect x="{current_x}" y="0" width="{segment_width}" height="{bar_height}" fill="{color}" rx="2" ry="2"/>'
            )
            current_x += segment_width

            col = idx % 2
            row = idx // 2
            lx = x_offset + (col * 130)
            ly = legend_y + (row * 20)

            legend_parts.append(
                f'  <g transform="translate({lx}, {ly})">'
                f'    <circle cx="4" cy="4" r="4" fill="{color}"/>'
                f'    <text x="14" y="8">{lang} ({pct:.1f}%)</text>'
                '  </g>'
            )

        svg_parts.append(f'    <mask id="bar-mask"><rect width="{max_bar_width}" height="{bar_height}" rx="5" fill="#fff"/></mask>')
        svg_parts.append(f'    <g mask="url(#bar-mask)">')
        svg_parts.extend(bar_parts)
        svg_parts.append('    </g>')
        svg_parts.append('  </svg>')
        svg_parts.extend(legend_parts)
        svg_parts.append('</svg>')

        output_file = 'languages_stats.svg'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_parts))



if __name__ == '__main__':
    x = MyGithubStats()
    x.execute()
    sys.exit(0)