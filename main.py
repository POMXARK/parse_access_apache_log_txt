import json
from datetime import datetime
import re
from file_read_backwards import FileReadBackwards
import threading
from rapidfuzz import  fuzz

lines = []


def parse_access_log(path_file: str):
    parse_logs = []
    try:
        with FileReadBackwards(path_file, encoding="utf-8") as frb:
            new_lines = []
            add_new = 0
            for idx, l in enumerate(frb):
                if len(lines) == 0:
                    new_lines.append(l)
                else:
                    try:
                        if fuzz.ratio(l, lines[0]) == 100:
                            break
                        else:
                            new_lines.append(l)
                    except IndexError:
                        break
            if len(new_lines) == 0:
                return
    except PermissionError or IndexError:
        return

    for el in new_lines:
        ip = re.findall(r"^\d+[.]\d+[.]\d+", el)
        if len(ip) == 0:
            ip = re.findall(r"^\d+[:]\d+[:]\d+", el)
            if len(ip) == 0:
                ip = re.findall(r"::\d+", el)
        date = str(datetime.strptime(re.findall(r"\d+[/]\D+[/]\d+[:]\d+[:]\d+[:]\d+", el)[-1], '%d/%b/%Y:%H:%M:%S'))
        data = re.split(r"] ", el)[-1]
        if len(ip) == 1:
            data = data.replace('\"', '')
            parse_logs.append({"ip": ip[-1], "date": date, "data": data})
    # else:
    for idx, el in enumerate(new_lines):
        lines.insert(idx, el)

    return json.dumps({"data": parse_logs})


def update_json():
    while True:
        json = parse_access_log(r"C:\xampp\apache\logs\access.log")
        if json is not None:
            print(json)



thr1 = threading.Thread(target=update_json, args=()).start()
print('основной поток')
