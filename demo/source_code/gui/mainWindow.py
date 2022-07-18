import sys
from pyeumoniaWindow import *
from pyeumoniaWindowCn import *
from platform import system
import locale
import pickle
from platform import system
from getpass import getuser
from os import mkdir


def load_language():
    language_dir = ''
    if system() == 'Windows':
        language_dir = f'C:/Users/{getuser()}/AppData/Local/pyeumonia/'
    elif system() == 'Linux':
        language_dir = f'/home/{getuser()}/.local/share/pyeumonia/'
    elif system() == 'Darwin':
        language_dir = f'/Users/{getuser()}/Library/Application Support/pyeumonia/'
    try:
        mkdir(language_dir)
    except FileExistsError:
        pass
    language = locale.getdefaultlocale()[0]
    # 检测系统语言
    try:
        language = pickle.load(open(language_dir + 'language.pkl', 'rb'))
    except FileNotFoundError:
        pickle.dump(language, open(language_dir + 'language.pkl', 'wb'))
    return language


def create_window(language):
    if language != 'zh_CN':
        app = QApplication(sys.argv)
        window = PyeumoniaGui(None)
        window.show()
        sys.exit(app.exec_())
    else:
        app = QApplication(sys.argv)
        window = PyeumoniaGuiCn(None)
        window.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    language = load_language()
    create_window(language)
