from typing import NamedTuple
from data   import Data
from utils  import warning



class Static(NamedTuple):
    dir_path      : str
    lang_colors   : dict[str, str]
    default_color : str



class SVGBuilder:

    def __init__(self, data: Data):
        self.data: Data = data


    STATIC = Static(
        dir_path = './images',

        lang_colors = {
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
        },

        default_color='#8b949e'
    )


    def create_svg_cards(self):
        self._generate_languages_svg()
    
    
    
    def _generate_languages_svg(self):
        sorted_langs = sorted(self.data.lang_bytes.items(), key=lambda x: x[1], reverse=True)
        total_bytes  = sum(self.data.lang_bytes.values())

        if total_bytes == 0:
            warning("No language found for SVG generation")
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
                
            color         = self.STATIC.lang_colors.get(lang, self.STATIC.default_color)
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

        output_file = f'{self.STATIC.dir_path}/languages_stats.svg'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_parts))