import os


class MyLog:

    log_file = None

    def __init__(self, log_file):
        self.log_file = log_file
        self.flag = True
        try:
            os.remove(self.log_file)
        except:
            pass

    def log(self, beam):
        if self.flag and self.log_file is not None:
            with open(self.log_file, "a") as lf:
                lf.write(str(beam) + "\n")
