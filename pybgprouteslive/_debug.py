import sys
from colorama import Fore, Style
import datetime

# Load environment variables.
DEBUG_NOTHING = 0
DEBUG_ESSENTIAL = 1
DEBUG_EXHAUSTIVE = 2
DEBUG_TOO_MUCH   = 3

class Debug:
    def __init__(self, outfile=None, mode="w", debug_level=DEBUG_NOTHING):
        self.outfile = None
        self.outfile = outfile
        self.mode = mode

        self.f = None
        self._open_file()

        self.debug_level = debug_level



    def _open_file(self):
        if self.outfile and self.outfile != "none":
            try:
                self.f = open(self.outfile, self.mode)
            except:
                print("Unable to open debug file '{}', using STDERR instead".format(self.outfile))
                self.f = sys.stderr
        else:
            self.f = sys.stderr



    def err_msg(self, msg, debug_level, end="\n"):
        if debug_level >= self.debug_level:
            currentTime = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            s = Fore.RED+Style.BRIGHT+"[ERROR - {}]: ".format(currentTime) +Style.NORMAL + msg + Fore.WHITE + end

            try:
                self.f.write(s)
                self.f.flush()
            except OSError:
                self._open_file()


    def wrn_msg(self, msg, debug_level, end="\n"):
        if debug_level >= self.debug_level:
            currentTime = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            s = Fore.YELLOW+Style.BRIGHT+"[WARNING - {}]: ".format(currentTime) +Style.NORMAL + msg + Fore.WHITE + end

            try:
                self.f.write(s)
                self.f.flush()
            except OSError:
                self._open_file()
            

    def debug(self, msg, debug_level, end="\n"):
        if debug_level >= self.debug_level:
            currentTime = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            s = Fore.BLUE+Style.BRIGHT+"[DEBUG {}]: ".format(currentTime) +Style.NORMAL + msg + Fore.WHITE + end

            try:
                self.f.write(s)
                self.f.flush()
            except OSError:
                self._open_file()


    def close(self):
        if self.outfile:
            self.f.close()


    def set_debug_level(self, debug_level):
        self.debug_level = debug_level

    
    def set_debug_file(self, debug_file):
        self.outfile = debug_file
        self._open_file()

