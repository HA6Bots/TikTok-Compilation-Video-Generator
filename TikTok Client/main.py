from PyQt5 import QtWidgets
from threading import Thread
import settings
import clientUI
import os
import client
import sys

current_path = os.path.dirname(os.path.realpath(__file__))
script = None
menu = None
class App():
    def __init__(self):
        global menu
        app = QtWidgets.QApplication(sys.argv)
        app.processEvents()

        login = clientUI.LoginWindow()
        login.show()


        Thread(target=client.VideoGeneratorRenderStatus).start()

        sys.exit(app.exec_())

def init():
    app = App()



sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook


def getFileNames(file_path):
    files = [os.path.splitext(filename)[0] for filename in os.listdir(file_path)]
    return files



def deleteAllFilesInPath(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_directory)
    settings.generateConfigFile()
    if not os.path.exists("TempClips"):
        os.mkdir("TempClips")
        os.mkdir("FirstClips")
        os.mkdir("Intros")
        os.mkdir("Outros")
        os.mkdir("Finished Videos")
        os.mkdir("Intervals")
        os.mkdir("Save Data")


    else:
        deleteAllFilesInPath("TempClips")

    client.requestGames()
    init()

    #requestGames()
    #requestClips("Warzone", 10)
    #connectFTP()

    pass
    #
    # while len(getFileNames(f'{current_path}/Assets/Music')) == 0:
    #     print(f"No music files in directory: '{current_path}/Assets/Music'. Please add some!")
    #     sleep(5)
    #
    # while len(getFileNames(f'{current_path}/Assets/Intros')) == 0:
    #     print(f"No intro videos in directory: '{current_path}/Assets/Intros'. Please add some!")
    #     sleep(5)
    #
    # while len(getFileNames(f'{current_path}/Assets/Intervals')) == 0:
    #     print(f"No intro videos in directory: '{current_path}/Assets/Intervals'. Please add some!")
    #     sleep(5)
    #
    #init()
