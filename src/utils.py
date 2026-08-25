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
from datetime import datetime, timezone, timedelta



def get_datetime() -> str:
    brazilian_time = timezone(timedelta(hours=-3))
    time_now       = datetime.now(timezone.utc).astimezone(brazilian_time)
    str_formated   = time_now.strftime('%Y-%m-%d %H:%M:%S')

    return f'[ {str_formated} ]'



def fatal(err: str):
    date = get_datetime()
    print(f'{date} [ ERROR ] {err}')
    sys.exit(1)



def info(msg: str):
    date = get_datetime()
    print(f'{date} {msg}')



def warning(msg: str):
    date = get_datetime()
    print(f'{date} {msg}')