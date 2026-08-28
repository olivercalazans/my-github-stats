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
# along with this program.  If not, see <https://gnu.org>.

from typing  import NamedTuple
from data    import Data
from display import info



class Static(NamedTuple):
    DIR_PATH      : str
    LANG_COLORS   : dict[str, str]
    DEFAULT_COLOR : str



class SVGBuilder:

    def __init__(self, data: Data):
        self.data: Data = data


    STATIC = Static(
        DIR_PATH = './images',

        LANG_COLORS = {
            'Python'          : '#3572A5',
            'JavaScript'      : '#f1e05a',
            'TypeScript'      : '#3178c6',
            'HTML'            : '#e34c26',
            'CSS'             : '#563d7c',
            'Shell'           : '#89e051',
            'Java'            : '#b07219',
            'C++'             : '#f34b7d',
            'C#'              : "#670086",
            'PHP'             : '#4F5D95',
            'Go'              : '#00ADD8',
            'TeX'             : '#3D6117',
            'PowerShell'      : '#012456',
            'Jupyter Notebook': '#DA5B0B',
            'R'               : '#198ce7',
            'Matlab'          : '#bb92ac',
            'Julia'           : '#a270ba',
            'C'               : '#555555',
            'Rust'            : '#dea584',
            'Swift'           : '#ffac45',
            'Kotlin'          : '#F18E33',
            'Ruby'            : '#701516',
            'Scala'           : '#DC322F',
            'Clojure'         : '#db5855',
            'Elixir'          : '#6e4a7e',
            'Haskell'         : '#29b544',
            'Dart'            : '#00B4AB',
            'Lua'             : '#000080',
            'Assembly'        : '#6E4C13',
            'Objective-C'     : '#438eff',
            'Perl'            : '#0298c3',
            'Groovy'          : '#e69f56',
            'Vue'             : '#41b883',
            'Svelte'          : '#ff3e00',
            'Dockerfile'      : '#384d54',
            'Makefile'        : '#427819',
            'Smarty'          : '#f1c40f',
            'SCSS'            : '#c6538c',
            'Less'            : '#1d365d',
            'AST'             : '#15aabf'
        },

        DEFAULT_COLOR='#8b949e'
    )



    def create_svg_cards(self):
        self._generate_languages_svg()
        self._generate_stats_svg()

    
    
    def _generate_languages_svg(self):
        sorted_langs = sorted(self.data.lang_bytes.items(), key=lambda x: x[1], reverse=True)
        total_bytes  = sum(self.data.lang_bytes.values())

        if total_bytes == 0:
            info("No language found for SVG generation")
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

        current_x = 0
        top_langs = sorted_langs[:self.data.TOTAL_LANGS]
        
        bar_parts    = []
        legend_parts = []
        
        legend_y      = y_offset + bar_height + 25
        max_bar_width = width - (x_offset * 2)

        for idx, (lang, bytes_count) in enumerate(top_langs):
            pct = (bytes_count / total_bytes) * 100

            if pct < 0.1:
                continue
                
            color         = self.STATIC.LANG_COLORS.get(lang, self.STATIC.DEFAULT_COLOR)
            segment_width = (pct / 100) * max_bar_width

            bar_parts.append(
                f'    <rect x="{current_x}" y="0" width="{segment_width}" height="{bar_height}" fill="{color}" rx="2" ry="2"/>'
            )
            current_x += segment_width

            col = idx % 2
            row = idx // 2
            lx  = x_offset + (col * 130)
            ly  = legend_y + (row * 20)

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

        output_file = f'{self.STATIC.DIR_PATH}/languages_stats.svg'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_parts))



    def _generate_stats_svg(self):
        width    = 300
        height   = 195
        x_offset = 25

        stats = [
            ("Total Stars", self.data.total_stars),
            ("Total Commits", self.data.total_commits),
            ("Total Issues", self.data.total_issues),
            ("Total Pull Requests", self.data.total_prs),
            ("Total Contributions", self.data.total_contributions)
        ]

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
            '  <style>',
            '    text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 14px; fill: #c9d1d9; }',
            '    .title { font-weight: 600; font-size: 16px; fill: #58a6ff; }',
            '    .bold { font-weight: 600; fill: #58a6ff; }',
            '  </style>',
            '  <!-- Fundo do GitHub Dark com borda sutil padrão -->',
            '  <rect width="100%" height="100%" rx="4.5" fill="#0d1117" stroke="#30363d" stroke-width="1"/>',
            '  <!-- Título -->',
            f'  <text x="{x_offset}" y="35" class="title">{self.data.USERNAME}\'s GitHub Stats</text>',
        ]

        start_y      = 65
        line_spacing = 25        
        value_x_pos  = width - (x_offset * 2)

        for idx, (label, val) in enumerate(stats):
            y_pos = start_y + (idx * line_spacing)
            svg_parts.append(
                f'  <g transform="translate({x_offset}, {y_pos})">'
                f'    <text x="0" y="0">{label}:</text>'
                f'    <text x="{value_x_pos}" y="0" class="bold" text-anchor="end">{val}</text>'
                '  </g>'
            )

        svg_parts.append('</svg>')

        output_file = f'{self.STATIC.DIR_PATH}/github_stats.svg'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_parts))