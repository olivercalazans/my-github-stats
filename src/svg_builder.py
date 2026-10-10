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

import os
import re
import html
import math
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
        os.makedirs(self.STATIC.DIR_PATH, exist_ok=True)
        self._generate_languages_svg()
        self._generate_stats_svg()
        self._generate_contributions_svg()



    def _generate_contributions_svg(self):
        template_file = 'templates/profile-night-green.svg'
        if not os.path.exists(template_file):
            info(f'Missing SVG template: {template_file}')
            return

        with open(template_file, encoding='utf-8') as f:
            svg = f.read()

        language_items = sorted(
            self.data.lang_bytes.items(), key=lambda item: item[1], reverse=True
        )

        top_languages   = language_items[:3]
        language_counts = [count for _, count in top_languages] + [
            sum(count for _, count in language_items[3:])
        ]
        
        while len(language_counts) < 4:
            language_counts.insert(-1 if language_counts else 0, 0)
            top_languages = top_languages + [('other', 0)]
        
        language_labels = [name for name, _ in top_languages] + ['other']
        language_labels = language_labels[:4]
        language_total  = sum(language_counts)
        
        language_percentages = [
            (count / language_total * 100) if language_total else 0
            for count in language_counts
        ]
        
        template_language_names = ('JavaScript', 'TypeScript', 'CSS', 'other')
        language_segments = list(zip(language_labels, language_counts, language_percentages))
        
        language_colors = [
            self.STATIC.LANG_COLORS.get(name, self.STATIC.DEFAULT_COLOR)
            for name, _, _ in language_segments
        ]

        for old_name, (new_name, byte_count, percentage) in zip(
            template_language_names, language_segments
        ):
            escaped_name = html.escape(new_name or 'other')
            legend = f'{escaped_name} ({percentage:.1f}%)'
            svg = re.sub(
                rf'(?<=>){re.escape(old_name)}(?=<animate attributeName="fill-opacity")',
                legend,
                svg,
                count=1,
            )
            svg = re.sub(
                rf'<title>{re.escape(old_name)} \d+</title>',
                f'<title>{escaped_name}: {byte_count} bytes, {percentage:.1f}%</title>',
                svg,
                count=1,
            )

        legend_start = svg.find('<g transform="translate(40, 520)">')
        legend_end   = svg.find('<g transform="translate(130, 130)">', legend_start)
        
        if legend_start >= 0 and legend_end > legend_start:
            legend       = svg[legend_start:legend_end]
            swatch_index = 0

            def replace_swatch(match):
                nonlocal swatch_index
                color = language_colors[swatch_index]
                swatch_index += 1
                return f'{match.group(1)}{color}'

            legend, _ = re.subn(
                r'(<rect x="0" y="[\d.]+" width="21\.666666666666668" '
                r'height="21\.666666666666668" fill=")[^"]+',
                replace_swatch,
                legend,
                count=4,
            )
            svg = svg[:legend_start] + legend + svg[legend_end:]


        def point(radius: float, angle: float) -> tuple[float, float]:
            radians = math.radians(angle)
            return radius * math.cos(radians), radius * math.sin(radians)


        def donut_path(start: float, sweep: float) -> str:
            if sweep >= 359.999:
                outer_start = point(117, start)
                outer_mid   = point(117, start + 180)
                inner_mid   = point(65, start + 180)
                inner_start = point(65, start)
                return (
                    f'M{outer_start[0]:.3f},{outer_start[1]:.3f}'
                    f'A117,117 0,1,1 {outer_mid[0]:.3f},{outer_mid[1]:.3f}'
                    f'A117,117 0,1,1 {outer_start[0]:.3f},{outer_start[1]:.3f}'
                    f'L{inner_start[0]:.3f},{inner_start[1]:.3f}'
                    f'A65,65 0,1,0 {inner_mid[0]:.3f},{inner_mid[1]:.3f}'
                    f'A65,65 0,1,0 {inner_start[0]:.3f},{inner_start[1]:.3f}Z'
                )
            outer_start = point(117, start)
            outer_end   = point(117, start + sweep)
            inner_end   = point(65, start + sweep)
            inner_start = point(65, start)
            large_arc   = 1 if sweep > 180 else 0
            
            return (
                f'M{outer_start[0]:.3f},{outer_start[1]:.3f}'
                f'A117,117 0,{large_arc},1 {outer_end[0]:.3f},{outer_end[1]:.3f}'
                f'L{inner_end[0]:.3f},{inner_end[1]:.3f}'
                f'A65,65 0,{large_arc},0 {inner_start[0]:.3f},{inner_start[1]:.3f}Z'
            )

        angle         = -90.0
        segment_index = 0
        path_pattern  = re.compile(
            r'<path d="[^"]*" style="fill: [^"]+;" stroke="#00000f" '
            r'stroke-width="2px"><title>[^<]*</title>.*?</path>'
        )


        def replace_language_path(match):
            nonlocal angle, segment_index
            name, byte_count, percentage = language_segments[segment_index]
            segment_index += 1
            sweep = percentage * 3.6
            path  = donut_path(angle, sweep)
            angle += sweep
            color = self.STATIC.LANG_COLORS.get(name, self.STATIC.DEFAULT_COLOR)
            title = f'{html.escape(name or "other")}: {byte_count} bytes, {percentage:.1f}%'
            block = re.sub(r'(<path d=")[^"]*', rf'\g<1>{path}', match.group(0), count=1)
            block = re.sub(r'(style="fill: )[^"]*', rf'\g<1>{color};', block, count=1)
            block = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', block, count=1)
            return block


        svg  = path_pattern.sub(replace_language_path, svg, count=4)
        days = self.data.contribution_days[-365:]
        
        cell_colors = [
            (68, 68, 68, 57, 57, 57, 48, 48, 48),
            (27, 125, 40, 23, 105, 33, 19, 88, 28),
            (36, 167, 54, 30, 140, 45, 25, 117, 38),
            (45, 209, 67, 38, 175, 56, 31, 146, 47),
            (87, 218, 105, 73, 182, 88, 61, 153, 74),
        ]

        def contribution_level(count: int) -> int:
            if count == 0: return 0
            if count <= 2: return 1
            if count <= 5: return 2
            if count <= 10: return 3
            return 4


        cell_pattern = re.compile(
            r'<g transform="translate\(([^)]*)\)">(?:(?!</g>).)*?'
            r'<rect stroke="none" x="0" y="0" width="18" height="18".*?</g>'
        )
        cell_index = 0

        def replace_cell(match):
            nonlocal cell_index
            if cell_index >= len(days):
                cell_index += 1
                return match.group(0)

            day         = days[cell_index]
            cell_index += 1
            count       = day['contributionCount']
            level       = contribution_level(count)
            height      = min(42.0, 2.6 + count * 2.2)
            colors      = cell_colors[level]
            
            fills = [
                f'rgb({colors[0]}, {colors[1]}, {colors[2]})',
                f'rgb({colors[3]}, {colors[4]}, {colors[5]})',
                f'rgb({colors[6]}, {colors[7]}, {colors[8]})',
            ]
            
            block           = match.group(0)
            transform_match = re.search(r'translate\(([-\d.]+) ([-\d.]+)\)', block)
            x, current_y    = float(transform_match.group(1)), float(transform_match.group(2))
            animation = re.search(
                r'<animateTransform attributeName="transform"[^>]*values="([-\d.]+) ([-\d.]+);([-\d.]+) ([-\d.]+)"[^>]*>.*?</animateTransform>',
                block,
            )

            baseline_y = float(animation.group(2)) if animation else current_y
            final_y    = baseline_y - (height - 2.6) * 1.15
            block = re.sub(
                r'translate\(([-\d.]+) ([-\d.]+)\)',
                f'translate({x:g} {final_y:.2f})',
                block,
                count=1,
            )
            block = re.sub(
                r'<animateTransform attributeName="transform"[^>]*/>|'
                r'<animateTransform attributeName="transform"[^>]*>.*?</animateTransform>',
                '',
                block,
            )

            if count:
                anim = (
                    f'<animateTransform attributeName="transform" type="translate" '
                    f'values="{x:g} {baseline_y:.2f};{x:g} {final_y:.2f}" dur="3s" repeatCount="1"/>'
                )
                block = block.replace('>', f'>{anim}', 1)

            rects = list(re.finditer(r'<rect stroke="none".*?</rect>', block))
            for rect_index, rect_match in reversed(list(enumerate(rects))):
                rect = rect_match.group(0)
                fill = fills[min(rect_index, 2)]
                rect = re.sub(r'fill="[^"]+"', f'fill="{fill}"', rect, count=1)
            
                if rect_index:
                    rect = re.sub(r'height="[\d.]+"', f'height="{height:.2f}"', rect, count=1)
                    rect = re.sub(
                        r'<animate attributeName="height"[^>]*/>|'
                        r'<animate attributeName="height"[^>]*>.*?</animate>',
                        '',
                        rect,
                    )
            
                    if count:
                        rect = rect.replace(
                            '>',
                            f'><animate attributeName="height" values="2.6;{height:.2f}" dur="3s"/>',
                            1,
                        )
                block = block[:rect_match.start()] + rect + block[rect_match.end():]
            
            first_rect = block.find('<rect stroke="none"')
            title      = f'<title>{day["date"]}: {count} contributions</title>'
            block      = block[:first_rect] + title + block[first_rect:]
            
            return block

        if days:
            svg = cell_pattern.sub(replace_cell, svg, count=365)

        metric_values = {
            'Commit': f'{self.data.total_commits} commits in the last 12 months',
            'Issue': self.data.total_issue_contributions,
            'PullReq': self.data.total_pr_contributions,
            'Review': self.data.total_pr_reviews,
            'Repo': self.data.total_contributed_repos,
        }
        for label, value in metric_values.items():
            svg = re.sub(
                rf'(<text\b[^>]*>{label})<title>[^<]*</title>(</text>)',
                lambda match: f'{match.group(1)}<title>{html.escape(str(value))}</title>{match.group(2)}',
                svg,
                count=1,
            )

        radar_values = [
            self.data.total_commits,
            self.data.total_issue_contributions,
            self.data.total_pr_contributions,
            self.data.total_pr_reviews,
            self.data.total_contributed_repos,
        ]

        radar_angles = (-90, -18, 54, 126, 198)
        radar_start_points = []
        radar_points = []

        for value, angle in zip(radar_values, radar_angles):
            radians = math.radians(angle)
            radar_start_points.append(
                f'{24.96 * math.cos(radians):.2f},{24.96 * math.sin(radians):.2f}'
            )
            radius  = 24.96 if value <= 0 else min(156, 31.2 * (1 + math.log10(value)))
            radar_points.append(f'{radius * math.cos(radians):.2f},{radius * math.sin(radians):.2f}')

        radar_start = ' '.join(radar_start_points)
        radar_end = ' '.join(radar_points)
        svg = re.sub(
            r'(<polygon style="stroke-width: 4px; stroke: #47a042; fill: #47a042; fill-opacity: 0.5;" points=")[^"]+',
            lambda match: match.group(1) + radar_end,
            svg,
            count=1,
        )
        svg = re.sub(
            r'(<animate attributeName="points" values=")[^"]+',
            lambda match: match.group(1) + f'{radar_start};{radar_end}',
            svg,
            count=1,
        )

        svg = re.sub(
            r'(<text style="font-size: 32px; font-weight: bold;" x="384"[^>]*>)(\d+)(</text>)',
            rf'\g<1>{self.data.total_contributions}\g<3>',
            svg,
            count=1,
        )

        for x_pos, value in ((650, self.data.total_stars), (772, self.data.total_forks)):
            svg = re.sub(
                rf'(<text style="font-size: 32px; font-weight: bold;" x="{x_pos}"[^>]*>)\d+<title>\d+</title>(</text>)',
                rf'\g<1>{value}<title>{value}</title>\g<2>',
                svg,
                count=1,
            )

        svg = svg.replace(
            'font-size: 16px;" x="1260"',
            'font-size: 19px;" x="1260"',
            1,
        )

        if days:
            date_range = f'{days[0]["date"]} / {days[-1]["date"]}'
            svg = re.sub(
                r'(<text style="font-size: 19px;" x="1260"[^>]*>)[^<]*(</text>)',
                rf'\g<1>{date_range}\g<2>',
                svg,
                count=1,
            )

        output_file = f'{self.STATIC.DIR_PATH}/profile-night-green.svg'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg)

    
    
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
        width    = 260
        height   = 195
        x_offset = 20

        stats = [
            ("Total Stars", self.data.total_stars),
            ("Commits (12 months)", self.data.total_commits),
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
            '  <!-- Fundo do GitHub Dark (sem bordas) -->',
            '  <rect width="100%" height="100%" rx="6" fill="#0d1117"/>',
            '  <!-- Título -->',
            f'  <text x="{x_offset}" y="35" class="title">{self.data.USERNAME}\'s GitHub Stats</text>',
        ]

        start_y      = 65
        line_spacing = 25        
        value_x_pos  = 222

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
