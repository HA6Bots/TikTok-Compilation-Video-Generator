from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5 import QtWidgets
from filtercreator import FilterCreationWindow
from PyQt5.QtCore import *
from PyQt5 import QtGui
import scriptwrapper
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSignal, QPoint, QRect, QObject
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QVideoFrame, QAbstractVideoSurface, QAbstractVideoBuffer, QVideoSurfaceFormat
from PyQt5.QtWidgets import *
import autodownloader
import server
import database
import pickle
import tiktok
import os
from time import sleep
from threading import Thread
import settings
import sys
from PyQt5.QtGui import QIcon

current_path = os.path.dirname(os.path.realpath(__file__))


def cleanDatabase():
    clips = database.getClipsByStatus("DOWNLOADED")

    print("Checking %s clips for MP4s" % len(clips))

    for i, clip in enumerate(clips):
        filePath = f"{settings.vid_filepath}/%s.mp4" % clip.mp4
        print(f"Checking if clip ({i + 1}/{len(clips)}) exists")
        if not os.path.exists(f"{settings.vid_filepath}/%s.mp4" % clip.mp4):
            print(f"Clip does not exist {filePath}")
            database.updateStatus(clip.id, "MISSING")

def deleteClipsForFilter(filter):
    clips = database.getFilterClipsByStatus(filter, "DOWNLOADED")

    print("Attemping to delete all clips for %s (%s downloaded found)" % (filter, len(clips)))
    for i, clip in enumerate(clips):
        filePath = f"{settings.vid_filepath}/%s.mp4" % clip.mp4
        print(f"Checking if clip ({i + 1}/{len(clips)}) exists")
        if not os.path.exists(f"{settings.vid_filepath}/%s.mp4" % clip.mp4):
            print(f"Clip does not exist {filePath}")
            database.updateStatus(clip.id, "FOUND")
        else:
            os.remove(f"{settings.vid_filepath}/%s.mp4" % clip.mp4)
            print(f"Clip exists, deleting it {filePath}")
            database.updateStatus(clip.id, "FOUND")




class PassiveDownloaderWindow(QMainWindow):
    update_log_found_clips = pyqtSignal(str, int, str)
    update_log_found_total_clips = pyqtSignal(str, int)
    update_log_start_downloading_game = pyqtSignal(str, int)
    update_log_downloaded_clip = pyqtSignal(int)
    update_done_downloading_game = pyqtSignal(str, int)

    start_clip_search = pyqtSignal()
    start_download_search = pyqtSignal()
    update_combo_box_filter = pyqtSignal()

    end_find_search = pyqtSignal()
    end_download_search = pyqtSignal()


    def __init__(self, clipEditorWindow = None):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi(f"{current_path}/UI/clipPassiveDownload.ui", self)
        try:
            self.setWindowIcon(QIcon('Assets/tiktoklogo.png'))
        except Exception as e:
            pass
        self.autoDownloadQueue = []
        self.autoWrapper = autodownloader.AutoDownloader(self, self.autoDownloadQueue)

        self.loadGameQueue()
        self.addFilter.clicked.connect(self.addFilterToQueue)
        self.clearFilters.clicked.connect(self.clearFilterQueue)

        self.startFinding.clicked.connect(self.startFindingProcess)
        self.stopFinding.clicked.connect(self.stopFindingProcess)
        self.startDownloading.clicked.connect(self.startDownloadingProcess)
        self.stopDownloading.clicked.connect(self.stopDownloadingProcess)
        self.refreshFilterClips.clicked.connect(self.logGetAmountClips)
        self.deleteClips.clicked.connect(self.deleteClipsByGame)
        self.updateStatus.clicked.connect(self.cleanDatabase)
        self.addNewFilter.clicked.connect(self.addFilterPopup)


        self.update_log_found_clips.connect(self.logAddClipFoundInfo)
        self.update_log_found_total_clips.connect(self.logAddTotalClipFoundInfo)
        self.update_log_start_downloading_game.connect(self.logStartDownloadFilterInfo)
        self.update_log_downloaded_clip.connect(self.updateProgressBar)
        self.update_done_downloading_game.connect(self.logDoneDownloadingFilterInfo)

        self.start_clip_search.connect(self.logStartClipSearchInfo)
        self.end_find_search.connect(self.logCompletedClipSearchInfo)
        self.end_download_search.connect(self.logCompletedDownloadInfo)
        self.start_download_search.connect(self.logStartDownloadInfo)

        self.update_combo_box_filter.connect(self.populateComboBox)

        self.startAuto.clicked.connect(self.startAutoProcess)
        self.stopAuto.clicked.connect(self.stopAutoProcess)
        self.addNewUser.clicked.connect(self.addNewFTPUser)
        self.removeUser.clicked.connect(self.deleteFTPUser)
        self.finishVidDirectory.clicked.connect(self.openFinishedVids)
        self.clipBinDirectory.clicked.connect(self.openClipBin)
        self.startAuto.setEnabled(False)

        self.populateComboBox()

        self.clipEditorWindow = clipEditorWindow
        self.clipFindIndex = 0
        self.updateAccountInfo()

    def closeEvent(self, evnt):
        sys.exit()

    def openFinishedVids(self):
        os.startfile(settings.final_video_path)

    def openClipBin(self):
        os.startfile(settings.vid_filepath)

    def addNewFTPUser(self):
        username = self.username.text()
        password = self.password.text()
        if username == "" or password == "":
            self.userAddStatus.setText("Please enter a password or username")
        elif username in [i[0] for i in server.usersList]:
            self.userAddStatus.setText("Account already exists with this name!")
        else:
            self.userAddStatus.setText("Successfully added new user %s" % username)
            server.usersList.append((username, password))
            self.updateAccountInfo()
            server.saveUsersTable()

    def deleteFTPUser(self):
        toRemove = self.userToRemove.currentText()
        index = [i for i in range(len(server.usersList)) if server.usersList[i][0] == toRemove]
        if toRemove:
            del server.usersList[index[0]]
            print("Successfully deleted user %s" % toRemove)
        else:
            print("Couldn't delete user %s" % toRemove)
        self.updateAccountInfo()
        server.saveUsersTable()



    def updateAccountInfo(self):
        self.accountInfo.clear()
        for user in server.usersList:
            username = user[0]
            password = user[1]

            self.accountInfo.append("User %s, password %s" % (username, password))
        self.populateRemoveUserList()

    def populateRemoveUserList(self):
        self.userToRemove.clear()
        users = []
        for user in server.usersList:
            if user[0] == settings.videoGeneratorFTPUser:
                continue
            users.append(user[0])
        self.userToRemove.addItems(users)


    def deleteClipsByGame(self):
        game = self.gameSelectToDelete.currentText()
        deleteClipsForFilter(game)

    def cleanDatabase(self):
        cleanDatabase()


    def addFilterPopup(self):

        self.filter_window = FilterCreationWindow(self)
        self.filter_window.show()

    def populateComboBox(self):
        self.filterSelect.clear()
        self.gameSelectToDelete.clear()
        filters = []
        saved_filters = database.getFilterNames()
        for filter in saved_filters:
            filters.append(filter)
        self.filterSelect.addItems(filters)
        self.gameSelectToDelete.addItems(filters)


    def startFindingProcess(self):
        self.refreshFilterClips.setEnabled(False)
        self.addFilter.setEnabled(False)
        self.clearFilters.setEnabled(False)
        self.startFinding.setEnabled(False)
        self.stopFinding.setEnabled(True)
        self.startAuto.setEnabled(False)
        self.stopAuto.setEnabled(False)

        self.autoWrapper.findClips()
        pass

    def stopFindingProcess(self):
        self.startFinding.setEnabled(True)
        self.startFinding.setEnabled(True)
        self.stopFinding.setEnabled(False)
        # self.startAuto.setEnabled(True)
        self.startAuto.setEnabled(False)
        self.stopAuto.setEnabled(False)
        self.autoWrapper.stop()
        pass

    def startDownloadingProcess(self):
        self.refreshFilterClips.setEnabled(False)
        self.addFilter.setEnabled(False)
        self.clearFilters.setEnabled(False)
        self.stopFinding.setEnabled(False)
        self.startAuto.setEnabled(False)
        self.stopAuto.setEnabled(False)
        self.startFinding.setEnabled(False)
        self.startDownloading.setEnabled(False)
        self.stopDownloading.setEnabled(True)

        self.autoWrapper.downloadClips()
        pass

    def stopDownloadingProcess(self):
        self.refreshFilterClips.setEnabled(True)
        self.addFilter.setEnabled(True)
        self.clearFilters.setEnabled(True)
        self.stopFinding.setEnabled(False)
        # self.startAuto.setEnabled(True)
        self.startAuto.setEnabled(False)
        self.stopAuto.setEnabled(False)
        self.startFinding.setEnabled(True)
        self.startDownloading.setEnabled(True)
        self.stopDownloading.setEnabled(False)

        self.autoWrapper.stop()
        pass


    def startAutoProcess(self):
        self.refreshFilterClips.setEnabled(False)
        self.addFilter.setEnabled(False)
        self.clearFilters.setEnabled(False)
        self.stopFinding.setEnabled(False)
        self.startFinding.setEnabled(True)
        self.startAuto.setEnabled(False)
        self.stopAuto.setEnabled(True)
        self.startFinding.setEnabled(False)
        self.startDownloading.setEnabled(False)

        self.autoWrapper.auto = True
        self.autoWrapper.startAutoMode()
        pass

    def stopAutoProcess(self):
        self.autoWrapper.auto = False
        self.autoWrapper.stop()

    def loadGameQueue(self):
        try:
            with open(f'{current_path}/autodownloaderfilters.save', 'rb') as pickle_file:
                self.autoDownloadQueue = pickle.load(pickle_file)
                self.autoWrapper.autoDownloadQueue = self.autoDownloadQueue
        except Exception:
            pass
        self.updateAutoDownloadQueue()
        self.logGetAmountClips()

    def addFilterToQueue(self):
        self.clearFilterQueue()
        filter = self.filterSelect.currentText()
        if filter not in [tempfilter[0] for tempfilter in self.autoDownloadQueue]:
            filterObject = database.getSavedFilterByName(filter)
            self.autoDownloadQueue.append([filter, filterObject])

        with open(f'{current_path}/autodownloaderfilters.save', 'wb') as pickle_file:
            pickle.dump(self.autoDownloadQueue, pickle_file)

        self.autoWrapper.autoDownloadQueue = self.autoDownloadQueue
        self.logGetAmountClips()
        self.updateAutoDownloadQueue()

    def clearFilterQueue(self):
        self.autoDownloadQueue.clear()
        self.autoWrapper.autoDownloadQueue.clear()
        self.updateAutoDownloadQueue()

    def updateAutoDownloadQueue(self):
        self.autoDownloadInfo.clear()
        for filter in self.autoDownloadQueue:
            self.autoDownloadInfo.append(filter[0])


    def logStartClipSearchInfo(self): # called in autodownloader
        self.downloadLog.append("Starting Clip Search for %s filters" % len(self.autoDownloadQueue))

    def logAddClipFoundInfo(self, game_name, amount, period): # called in twitch
        self.downloadLog.append("Found %s for filter %s for period %s" % (amount, game_name, period))

    def logAddTotalClipFoundInfo(self, game_name, amount): # called in twitch
        self.downloadLog.append("Found %s for filter %s" % (amount, game_name))
        self.autoWrapper.findClips()

    def logCompletedClipSearchInfo(self): # called in autodownloader
        self.downloadLog.append("Completed clip search for %s filters" % len(self.autoDownloadQueue))
        self.logGetAmountClips()
        self.refreshFilterClips.setEnabled(True)
        self.addFilter.setEnabled(True)
        self.clearFilters.setEnabled(True)
        self.startFinding.setEnabled(True)
        self.stopFinding.setEnabled(False)
        self.stopAuto.setEnabled(False)
        # self.startAuto.setEnabled(True)
        self.startAuto.setEnabled(False)


    def logGetAmountClips(self): # called here
        self.clipBinInformation.clear()
        filters = database.getAllSavedFilters() # get all saved filters
        total_downloaded = 0
        for filter in [i[0] for i in filters]:
            amount = database.getFilterClipCount(filter)[0][0]
            amount_downloaded = database.getFilterClipCountByStatus(filter, "DOWNLOADED")[0][0]
            amount_used = database.getFilterClipCountByStatus(filter, "USED")[0][0]
            total_downloaded += amount_downloaded
            self.clipBinInformation.append("Filter: %s amount clips %s (downloaded %s | used %s)" % (filter, amount, amount_downloaded, amount_used))
        self.clipBinInformation.append("Total Downloaded: %s" % total_downloaded)

    def logStartDownloadInfo(self): # called in autodownloader
        self.downloadLog.append("Starting downloads for %s filters" % len(self.autoDownloadQueue))

    def logStartDownloadFilterInfo(self, filter, amount): # called tiktok
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(amount)
        self.downloadLog.append("Downloading %s clips for filter %s" % (amount, filter))
        self.currentDownloadFilter.setText("Current Filter: %s" % filter)
        self.amountCurrentPass.setText("Amount in current pass: %s" % amount)

    def logDoneDownloadingFilterInfo(self, filter, amount): # called in tiktok
        self.downloadLog.append("Finished downloading %s clips for filter %s" % (amount, filter))
        self.autoWrapper.downloadClips()

    def logCompletedDownloadInfo(self): # called in autodownloader
        self.downloadLog.append("Completed downloading %s clips" % len(self.autoDownloadQueue))
        self.logGetAmountClips()
        self.refreshFilterClips.setEnabled(True)
        self.addFilter.setEnabled(True)
        self.clearFilters.setEnabled(True)
        self.startFinding.setEnabled(True)
        self.startDownloading.setEnabled(True)
        self.stopDownloading.setEnabled(False)
        self.stopFinding.setEnabled(False)

    def updateProgressBar(self, number): # called in twitch
        self.progressBar.setValue(number)
        self.downloadProgressAmount.setText("Download progress: %s" % number)


