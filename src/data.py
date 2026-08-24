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

from dataclasses import dataclass, field



@dataclass(slots=True)
class Data:
    USERNAME            : str            = 'olivercalazans'
    TOTAL_LANGS         : int            = 10
    lang_bytes          : dict[str, int] = field(default_factory=dict)
    len_repos           : int            = 0
    repos               : list[dict]     = field(default_factory=list)
    total_stars         : int            = 0
    total_commits       : int            = 0
    total_contributions : int            = 0