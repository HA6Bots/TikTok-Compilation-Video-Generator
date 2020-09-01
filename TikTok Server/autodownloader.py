import tiktok
import database
from time import sleep
from threading import Thread

class AutoDownloader():
    def __init__(self, window, downloadqueue):
        self.window = window
        self.autoDownloadQueue = downloadqueue
        self.clipIndex = 0
        self.auto = False


    def startAutoMode(self):
        self.auto = True
        self.findClips()

    def startDownloading(self):
        self.downloadClips()


    def startFinding(self):
        self.findClips()


    def stop(self):
        tiktok.forceStop = True


    def findClips(self):
        if self.clipIndex == 0:
            self.window.start_clip_search.emit()

        if not self.clipIndex == len(self.autoDownloadQueue):
            Thread(target=tiktok.getAllClips, args=(self.autoDownloadQueue[self.clipIndex], int(self.window.bulkFindAmount.text()), self.window)).start()
            self.clipIndex += 1
        else:
            self.clipIndex = 0
            self.window.end_find_search.emit()
            if self.auto:
                self.downloadClips()

    def downloadClips(self):
        if self.clipIndex == 0:
            self.window.start_download_search.emit()
        if not self.clipIndex == len(self.autoDownloadQueue):
            filter = self.autoDownloadQueue[self.clipIndex]
            clips = database.getFoundClips(filter[0], int(self.window.bulkDownloadAmount.text()))
            Thread(target=tiktok.autoDownloadClips, args=(filter[0], clips, self.window)).start()
            self.clipIndex += 1
        else:
            self.clipIndex = 0
            self.window.end_download_search.emit()
            if self.auto:
                self.findClips()
