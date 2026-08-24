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

import sys
from data           import Data
from request_github import Fetcher
from svg_builder    import SVGBuilder


def main():
    data = Data()

    fetcher = Fetcher(data)
    fetcher.fetch_data()

    builder = SVGBuilder(data)
    builder.create_svg_cards()



if __name__ == '__main__':
    main()
    sys.exit(0)