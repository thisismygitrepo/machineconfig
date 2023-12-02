
"""Pomodoro
"""

from crocodile.toolbox import Log, install_n_import, Scheduler, P
import time
from datetime import datetime


def pomodoro(work: int = 25, rest: int = 5, repeats: int = 4):
    logger = Log(name="pomodoro", file=False, stream=True)
    def loop(sched: Scheduler):
        speak("Alright, time to start working..."); start = datetime.now(); _ = sched
        while (diff := work - ((datetime.now() - start).seconds / 60)) > 0: logger.debug(f"Keep working. Time Left: {round(diff)} minutes"); time.sleep(60 * 1)
        speak("Now, its time to take a break."); start = datetime.now()
        while (diff := rest - ((datetime.now() - start).seconds / 60)) > 0: logger.critical(f"Keep Resting. Time Left: {round(diff)} minutes"); time.sleep(60 * 1)
    def speak(txt: str):
        install_n_import("gtts").gTTS(txt, lang='en', tld='com.au').save(tmp := P.tmpfile(suffix=".mp3")); time.sleep(0.5)
        pyglet = install_n_import("pyglet"); pyglet.resource.path = [tmp.parent.str]; pyglet.resource.reindex(); pyglet.resource.media(tmp.name).play()
    def beep(duration: int = 1, frequency: int = 3000):
        try: import winsound
        except ImportError: __import__("os").system(f'beep -f {frequency} -l {1000 * duration}')
        else: winsound.Beep(frequency, 1000 * duration)  # type: ignore
    _ = beep
    return Scheduler(routine=loop, max_cycles=repeats, logger=logger, wait="0.1m").run()


# def main():
#     parser = argparse.ArgumentParser(description='FTP client')
#
#     parser.add_argument("machine", help=f"machine ssh address", default="")
#     parser.add_argument("file", help="file/folder path.", default="")
#     # FLAGS
#     parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
#     parser.add_argument("--zipFirst", "-z", help="Zip before sending.", action="store_true")  # default is False
#
#     args = parser.parse_args()


if __name__ == '__main__':
    pomodoro()
