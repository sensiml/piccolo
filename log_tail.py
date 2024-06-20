import io
import json
import sys
import time

import colorama

colorama.init()


def follow(file, sleep_sec=0.1):
    """Yield each line from a file as they are written.
    `sleep_sec` is the time to sleep after empty reads."""
    line = ""
    while True:
        tmp = file.readline()
        if tmp is not None:
            line += tmp
            if line.endswith("\n"):
                yield line
                line = ""
        elif sleep_sec:
            time.sleep(sleep_sec)


if __name__ == "__main__":
    with open(sys.argv[1], "r") as file:
        file.seek(0, io.SEEK_END)
        for line in follow(file):
            if len(line) < 10:
                continue
            try:
                if "/MainProcess]" in line or "ForkPoolWorker" in line:
                    message = line[line.index("] ") + 2 :]
                else:
                    # print(line.index("] {"))
                    message = line[line.index("] {") + 2 :]
            except Exception as e:
                # print(colorama.Fore.RED+str(e), end='\n')
                message = line

            try:
                if " ERROR " in line:
                    message = json.dumps(json.loads(message), indent=4, sort_keys=True)
                    print(colorama.Fore.RED + message, end="\n")
                elif " INFO " in line:
                    message = json.dumps(json.loads(message), indent=4, sort_keys=True)
                    print(colorama.Fore.BLUE + message, end="\n")
                elif " DEBUG " in line:
                    message = json.dumps(json.loads(message), indent=4, sort_keys=True)
                    print(colorama.Fore.GREEN + message, end="\n")
                else:
                    print(line, end="")

            except:
                print(line, end="\n")
