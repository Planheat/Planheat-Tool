import os
import os.path
import json


class MyLog:

    def __init__(self, log_file, file_name=None, keep_file=False):
        self.log_file = log_file
        self.flag = True
        if file_name is not None:
            self.log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "log", file_name + ".txt")
        try:
            if not keep_file:
                os.remove(self.log_file)
        except:
            pass

    def log(self, beam, *args):
        if self.flag and self.log_file is not None:
            with open(self.log_file, "a") as lf:
                if isinstance(beam, dict):
                    beam = MyLog.format_json_object(beam)
                for string in args:
                    if isinstance(string, dict):
                        string = MyLog.format_json_object(string)
                    beam = beam + " " + str(string)
                lf.write(str(beam) + "\n")

    @staticmethod
    def format_json_object(content: dict):
        return json.dumps(content, indent=4)
