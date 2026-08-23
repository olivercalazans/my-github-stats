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



def warning(msg: str):
    date = get_datetime()
    print(f'{date} {msg}')