import json
from datetime import datetime
import re
from file_read_backwards import FileReadBackwards
from threading import Thread
from rapidfuzz import fuzz


class ParserAccessLog(Thread):

    def __init__(self, path_file):
        super().__init__()
        self.path_file = path_file
        self.new_lines = []
        self.parse_logs = []
        self.lines = []

    def _read_file(self):
        self.parse_logs = []
        try:
            with FileReadBackwards(self.path_file, encoding="utf-8") as frb:
                self.new_lines = []
                for idx, l in enumerate(frb):
                    if len(self.lines) == 0:
                        self.new_lines.append(l)
                    else:
                        try:
                            if fuzz.ratio(l, self.lines[0]) == 100:
                                break
                            else:
                                self.new_lines.append(l)
                        except IndexError:
                            break
                if len(self.new_lines) == 0:
                    return
                else:
                    return self._parse_file()

        except PermissionError or IndexError:
            return

    def _parse_file(self):
        for el in self.new_lines:
            ip = re.findall(r"^\d+[.]\d+[.]\d+", el)
            if len(ip) == 0:
                ip = re.findall(r"^\d+[:]\d+[:]\d+", el)
                if len(ip) == 0:
                    ip = re.findall(r"::\d+", el)
            date = str(datetime.strptime(re.findall(r"\d+[/]\D+[/]\d+[:]\d+[:]\d+[:]\d+", el)[-1], '%d/%b/%Y:%H:%M:%S'))
            data = re.split(r"] ", el)[-1]
            if len(ip) == 1:
                data = data.replace('\"', '')
                self.parse_logs.append({"ip": ip[-1], "date": date, "data": data})
        for idx, el in enumerate(self.new_lines):
            self.lines.insert(idx, el)

        return json.dumps({"data": self.parse_logs})

    def _update_json(self):
        while True:
            json = self._read_file()
            if json is not None:
                print(json)

    def run(self):
        self._update_json()


if __name__ == '__main__':
    thread1 = ParserAccessLog(r"access.log")
    thread1.start()

print('основной поток')
