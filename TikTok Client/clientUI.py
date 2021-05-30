from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5 import QtGui
from pymediainfo import MediaInfo
from PyQt5.QtGui import QIcon

import cv2
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSignal, QPoint, QRect, QObject
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QVideoFrame, QAbstractVideoSurface, QAbstractVideoBuffer, QVideoSurfaceFormat
import client
from PyQt5.QtWidgets import *
import scriptwrapper
import pickle
from threading import Thread
import settings
import os

games = None

moreClips = None

selected_game = ''
current_path = os.path.dirname(os.path.realpath(__file__))


class LoginWindow(QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi(f"{current_path}/UI/login.ui", self)
        try:
            self.setWindowIcon(QIcon('Assets/tiktoklogo.png'))
        except Exception as e:
            pass
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        if settings.autoLogin:
            self.autoLogin.setChecked(True)
            self.username.setText(settings.FTP_USER)
            self.password.setText(settings.FTP_PASSWORD)
        self.login.clicked.connect(self.attemptLogin)


    def attemptLogin(self):
        username = self.username.text()
        password = self.password.text()
        success = client.testFTPConnection(username, password)
        if success:
            self.loginSuccess()
        else:
            self.loginMessage.setText("Incorrect username or password")

    def loginSuccess(self):
        self.menu = MainMenu()
        self.menu.show()
        client.mainMenuWindow = self.menu
        self.close()


class MainMenu(QMainWindow):
    update_progress_bar = pyqtSignal(int)
    finish_downloading = pyqtSignal()
    download_finished_videos_names = pyqtSignal(list)
    update_render_progress = pyqtSignal(dict)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi(f"{current_path}/UI/menu.ui", self)
        try:
            self.setWindowIcon(QIcon('Assets/tiktoklogo.png'))
        except Exception as e:
            pass
        self.welcomeMessage.setText("Welcome %s!" % settings.FTP_USER)
        self.editVideo.clicked.connect(self.startEditingVideo)
        self.openVideos.clicked.connect(self.openDownloadLocation)
        self.refreshFinishedVideos.clicked.connect(self.getFinishedVideos)
        self.downloadSingle.clicked.connect(self.downloadFinishedVideo)
        self.getFinishedVideos()
        self.progressBar.setMaximum(2)
        self.update_progress_bar.connect(self.updateDownload)
        self.finish_downloading.connect(self.finishDownloading)
        self.update_render_progress.connect(self.updateRenderProgress)
        self.download_finished_videos_names.connect(self.populateFinishedVideos)


    def updateRenderProgress(self, dictionary):
        max_progress = dictionary["max_progress"]
        current_progress = dictionary["current_progress"]
        render_message = dictionary["render_message"]
        if max_progress is not None:
            self.renderProgress.setMaximum(max_progress)
        if current_progress is not None:
            self.renderProgress.setValue(current_progress)
        self.renderMessage.setText(render_message)


    def downloadFinishedVideo(self):
        self.downloadSingle.setEnabled(False)
        self.progressBar.setValue(0)
        name = self.finishedVidSelect.currentText()
        Thread(target=client.downloadFinishedVideo, args=(name, self)).start()


    def populateFinishedVideos(self, names):
        self.finishedVidSelect.clear()
        names.reverse()
        self.finishedVidSelect.addItems(names)
        self.downloadSingle.setEnabled(True)
        self.completedVideos.setText("%s Completed Videos" % len(names))

    def getFinishedVideos(self):
        self.downloadSingle.setEnabled(False)
        Thread(target=client.requestFinishedVideoList, args=(self,)).start()


    def startEditingVideo(self):
        self.download_menu = ClipDownloadMenu()
        self.download_menu.show()
        client.mainMenuWindow = self
        self.close()

    def updateDownload(self, number):
        self.progressBar.setValue(number)

    def finishDownloading(self):
        self.downloadSingle.setEnabled(True)
        self.openDownloadLocation()

    def openDownloadLocation(self):
        os.startfile("Finished Videos")
        # options = QFileDialog.Options()
        # fileName, _ = QFileDialog.getOpenFileName(self,"Select The First Clip", f"Finished Videos/","All Files (*);;MP4 Files (*.mp4)", options=options)




class ClipDownloadMenu(QMainWindow):
    update_progress_bar = pyqtSignal(int)
    set_max_progres_bar = pyqtSignal(int)
    finished_downloading = pyqtSignal(scriptwrapper.ScriptWrapper)



    def __init__(self, clipEditorWindow = None):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi(f"{current_path}/UI/clipDownload.ui", self)
        try:
            self.setWindowIcon(QIcon('Assets/tiktoklogo.png'))
        except Exception as e:
            pass
        self.progressBar.hide()
        self.addingToDBLabel.hide()
        self.downloadButton.clicked.connect(self.downloadClips)
        self.update_progress_bar.connect(self.updateProgressBar)
        self.set_max_progres_bar.connect(self.setMaxProgressBar)
        self.finished_downloading.connect(self.finishedDownloading)

        self.clipEditorWindow = clipEditorWindow
        self.populateGames()


    def populateGames(self):
        self.games.clear()
        self.games.addItems(games)


    def downloadClips(self):
        #Getting all the necessary information for getting the clips
        self.downloadButton.hide()
        self.addingToDBLabel.show()
        self.progressBar.show()
        num_clips = str(self.clipNumCombo.currentText())
        game = str(self.games.currentText())

        already_scripts = None
        if self.clipEditorWindow is not None:
            already_scripts = self.clipEditorWindow.videoWrapper.scriptWrapper.rawScript

        if already_scripts is None:
            Thread(target=client.requestClips, args=(game, num_clips, self)).start()
        else:
            Thread(target=client.requestClipsWithoutClips, args=(game, num_clips, already_scripts, self)).start()

    def setMaxProgressBar(self, number):
        self.progressBar.setMaximum(number)


    def updateProgressBar(self, downloadno):
        self.progressBar.setValue(downloadno)

    def finishedDownloading(self, newscriptwrapper):
        if not len(newscriptwrapper.scriptMap) == 0:
            self.close()
            if self.clipEditorWindow is None:
                twitchvideo = scriptwrapper.TwitchVideo(newscriptwrapper)
                self.clipEditor = clipEditor(twitchvideo)
                self.clipEditor.show()
            else:
                self.clipEditorWindow.videoWrapper.scriptWrapper.addScriptWrapper(newscriptwrapper)
                self.clipEditorWindow.downloaded_more_scripts.emit()
        else:
            self.downloadFail("Failure")
            self.close()
            if self.clipEditorWindow is None:
                client.mainMenuWindow.show()


    def downloadFail(self, msg):
        buttonReply = QMessageBox.information(self, msg, 'No clips able to download. Please try with more clips', QMessageBox.Ok)




class ClipUploadMenu(QMainWindow):
    update_progress_bar = pyqtSignal()
    set_max_progres_bar = pyqtSignal(int)
    finished_downloading = pyqtSignal()



    def __init__(self, videowrapper, name):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi(f"{current_path}/UI/clipUpload.ui", self)

        try:
            self.setWindowIcon(QIcon('Assets/tiktoklogo.png'))
        except Exception as e:
            pass

        self.update_progress_bar.connect(self.updateProgressBar)
        self.set_max_progres_bar.connect(self.setMaxProgressBar)
        self.finished_downloading.connect(self.finishedDownloading)
        Thread(target=client.exportVideo, args=(videowrapper, name, self)).start()
        self.i = 0


    def setMaxProgressBar(self, number):
        self.progressBar.setMaximum(number)

    def updateProgressBar(self):
        self.i += 1
        self.progressBar.setValue(self.i)

    def finishedDownloading(self):
        self.close()
        self.mainMenu = MainMenu()
        self.mainMenu.show()
        client.mainMenuWindow = self.mainMenu




class clipEditor(QMainWindow):

    downloaded_more_scripts = pyqtSignal()

    def __init__(self, videoWrapper):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi(f"{current_path}/UI/ClipEditor.ui", self)

        try:
            self.setWindowIcon(QIcon('Assets/tiktoklogo.png'))
        except Exception as e:
            pass


        #Variables and stuff for the editor to send to the video generator
        self.videoWrapper = videoWrapper
        self.mainCommentIndex = 0
        self.populateTreeWidget()
        self.treeWidget.currentItemChanged.connect(self.setSelection)
        self.treeWidget.clicked.connect(self.setSelection)
        self.downloaded_more_scripts.connect(self.receiveMoreClips)
        self.introClipPath = None
        self.firstClipPath = None
        self.intervalClipPath = None
        self.outroClipPath = None


        self.keep = []
        #All of the stuff to make the clip editor work
        self.playlist = QMediaPlaylist()
        vid_path = QUrl.fromLocalFile(f'{current_path}/VideoFiles')
        self.mediaPlayer = QMediaPlayer()
        self.playPauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        #self.addClipsToPlaylist()
        self.mediaPlayer.stateChanged.connect(self.playPauseMedia)
        self.mediaPlayer.setVideoOutput(self.clipPlayer)
        self.mediaPlayer.setPlaylist(self.playlist)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.videoDurationSlider.sliderMoved.connect(self.setPosition)
        self.defaultIntro.stateChanged.connect(self.defaultIntroToggle)
        self.chooseFirstClip.clicked.connect(self.firstClipFileDialog)
        self.chooseIntro.clicked.connect(self.introFileDialog)
        self.chooseInterval.clicked.connect(self.intervalFileDialog)
        self.chooseOutro.clicked.connect(self.outroFileDialog)
        self.timer = QTimer(self, interval=1)
        self.timer.start()


        self.mediaPlayer.positionChanged.connect(self.vidTimeStamp)
        self.playPauseButton.clicked.connect(self.play)
        self.skipButton.clicked.connect(self.skipComment)
        self.downloadMore.clicked.connect(self.downloadMoreScripts)
        self.keepButton.clicked.connect(self.keepComment)
        self.exportButton.clicked.connect(self.videoExportConfirmation)

        self.moveDown.clicked.connect(self.moveClipDown)
        self.moveUp.clicked.connect(self.moveClipUp)

        #self.nextButton.clicked.connect(self.nextClip)
        self.playlist.currentIndexChanged.connect(self.checkForLastClip)
        if settings.enforceInterval:
            self.loadDefaultInterval()
        else:
            self.chooseInterval.hide()
            self.defaultInterval.hide()

        if settings.enforceIntro:
            self.loadDefaultIntro()
        else:
            self.chooseIntro.hide()
            self.defaultIntro.hide()

        if settings.enforceOutro:
            self.loadDefaultOutro()
        else:
            self.chooseOutro.hide()
            self.defaultOutro.hide()

        if not settings.enforceFirstClip:
            self.chooseFirstClip.hide()
            self.firstClipCred.hide()
            self.firstClipNameLabel.hide()

        self.updateDisplay()



    def muteBackgroundVolume(self):
        self.backgroundVolume.setText("0")


    def defaultIntroToggle(self):
        print(self.defaultIntro.isChecked())

    def receiveMoreClips(self):
        self.populateTreeWidget()

    def downloadMoreScripts(self):
        self.gameSelect = ClipDownloadMenu(self)
        self.gameSelect.show()
        pass

    def moveClipDown(self):
        self.videoWrapper.scriptWrapper.moveUp(self.mainCommentIndex)
        self.updateDisplay()

    def moveClipUp(self):
        self.videoWrapper.scriptWrapper.moveDown(self.mainCommentIndex)
        self.updateDisplay()

    def updateDisplay(self):
        #self.scriptWrapper.saveScriptWrapper()
        self.getCurrentWidget(self.mainCommentIndex).setForeground(0, QtGui.QBrush(QtGui.QColor("blue")))

        twitchclip = self.videoWrapper.scriptWrapper.getCommentInformation(self.mainCommentIndex)
        mp4file = twitchclip.mp4
        video_duration = twitchclip.vid_duration
        audio = twitchclip.audio
        self.clipTitle.setText(f'{twitchclip.author_name}-{twitchclip.clip_name}')

        self.likeCount.setText("Likes: %s" % twitchclip.diggCount)
        self.shareCount.setText("Shares: %s" % twitchclip.shareCount)
        self.playCount.setText("Plays: %s" % twitchclip.playCount)
        self.commentCount.setText("Comments: %s" % twitchclip.commentCount)

        self.updateClipDuration()
        self.mediaPlayer.stop()
        if len(mp4file.split("/")) > 2:
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(f'{current_path}/{mp4file}')));
        else:
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(f'{current_path}/TempClips/{mp4file}.mp4')))
        self.mediaPlayer.setVolume(audio * 100)
        self.estTime.setText(str(self.videoWrapper.scriptWrapper.getEstimatedVideoTime()))
        self.videoLength.setText(f'{round(video_duration, 1)}')
        self.mediaPlayer.play()
        self.clipCountLabel.setText(f"Clip {self.mainCommentIndex+1}/{len(self.videoWrapper.scriptWrapper.rawScript)}")


    def setSelection(self):


        try:
            self.currentTreeWidget = self.treeWidget.currentItem()
            if self.currentTreeWidget.parent() is None:
                self.mainCommentIndex = int(str(self.currentTreeWidget.text(0)).split(" ")[1])

            self.updateColors()
            self.updateDisplay()
        except Exception:
            print("error trying to update selection index")




    def getCurrentWidget(self, x):
        return self.getTopLevelByName("Vid %s" % str(x))

    def incrimentSelection(self):
        if not self.mainCommentIndex + 1 > self.videoWrapper.scriptWrapper.getCommentAmount() - 1:
            self.mainCommentIndex += 1

    def updateColors(self):
        for x, mainComment in enumerate(self.videoWrapper.scriptWrapper.scriptMap):
            self.selectedMainComment = self.getTopLevelByName("Vid %s" % str(x))
            if mainComment is True:
                self.selectedMainComment.setForeground(0, QtGui.QBrush(QtGui.QColor("green")))
            else:
                self.selectedMainComment.setForeground(0, QtGui.QBrush(QtGui.QColor("red")))

    def keepComment(self):
        self.videoWrapper.scriptWrapper.keep(self.mainCommentIndex)
        self.incrimentSelection()
        self.updateColors()
        self.updateDisplay()

    def skipComment(self):
        self.videoWrapper.scriptWrapper.skip(self.mainCommentIndex)
        self.updateColors()
        self.nextMainComment()
        self.updateDisplay()

    def nextMainComment(self):
        if not self.mainCommentIndex + 1 > self.videoWrapper.scriptWrapper.getCommentAmount() - 1:
            self.mainCommentIndex += 1
            self.selectedMainComment = self.getTopLevelByName("Main Comment %s" % str(self.mainCommentIndex))


    def populateTreeWidget(self):
        self.treeWidget.clear()
        for i, clip in enumerate(self.videoWrapper.scriptWrapper.rawScript):
            treeParentName = "Vid %s"%str(i)
            self.addTopLevel(treeParentName)
        self.selectedMainComment = self.getTopLevelByName("Vid %s" % str(0))
        self.updateColors()


    def getTopLevelByName(self, name):
        for index in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(index)
            if item.text(0) == name:
                return item
        return None

    def addTopLevel(self, name):
        if self.getTopLevelByName(name) is None:
            QTreeWidgetItem(self.treeWidget, [name])


    def checkForLastClip(self):
        if self.playlist.currentIndex() == len(self.startCut) - 1:
            self.playlist.setPlaybackMode(0)


    def updateClipDuration(self):
        twitchclip = self.videoWrapper.scriptWrapper.getCommentInformation(self.mainCommentIndex)
        #self.clipDurationLabel.setText(f'Clip Duration: {duration}')


    #Getting the timestamp for the video player
    def vidTimeStamp(self):
        self.timeStamp.setText(f"00:{self.getPositionInSecs()}")
    
    #Controlling the play/pause of the videos, kinda obvious
    def playPauseMedia(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playPauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playPauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        
    #Giving the play button function
    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
    
    #This makes the duration slider move with the video
    def positionChanged(self, position):
        self.videoDurationSlider.setValue(position)

    #Sets the range of each slider to the duration of each video
    def durationChanged(self, duration):
        self.videoDurationSlider.setRange(0, duration)

    #This is to control the position of the video in the media player so I can control the video with the duration slider
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)
        self.mediaPlayer.play()


    def introFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"Select The Intro Clip", f"{current_path}/Intros","All Files (*);;MP4 Files (*.mp4)", options=options)
        if fileName:
            try:
                vid = cv2.VideoCapture(fileName)
                height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                if width != int(1920) or height != int(1080):
                    self.uploadFail("Incorrect resolution for file %s.\n Resolution was %sx%s, required 1920x1080" % (fileName, width, height))
                else:
                    self.introClipPath = fileName
                    self.chooseIntro.setText("Reselect Intro")
            except Exception as e:
                self.uploadFail("Error occured uploading file \n %s" % (e))





    def outroFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"Select The Outro Clip", f"{current_path}/Outros","All Files (*);;MP4 Files (*.mp4)", options=options)
        if fileName:
            try:
                vid = cv2.VideoCapture(fileName)
                height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                if int(width) != 1920 or int(height) != 1080:
                    self.uploadFail("Incorrect resolution for file %s.\n Resolution was %sx%s, required 1920x1080" % (fileName, width, height))
                else:
                    self.outroClipPath = fileName
                    self.chooseOutro.setText("Reselect Outro")
            except Exception as e:
                self.uploadFail("Error occured uploading file \n %s" % (e))


    def intervalFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"Select The Interval Clip", f"{current_path}/Intervals","All Files (*);;MP4 Files (*.mp4)", options=options)
        if fileName:
            try:
                vid = cv2.VideoCapture(fileName)
                height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                if int(width) != 1920 or int(height) != 1080:
                    self.uploadFail("Incorrect resolution for file %s.\n Resolution was %sx%s, required 1920x1080" % (fileName, width, height))
                else:
                    self.intervalClipPath = fileName
                    self.chooseInterval.setText("Reselect Interval")
            except Exception as e:
                self.uploadFail("Error occured uploading file \n %s" % (e))


    def firstClipFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"Select The First Clip", f"{current_path}/FirstClips","All Files (*);;MP4 Files (*.mp4)", options=options)
        if fileName:
            # name = len(fileName.split("/"))
            # self.firstClipPath = (fileName.split("/")[name-1])

            try:
                vid = cv2.VideoCapture(fileName)
                height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                if int(width) != 1920 or int(height) != 1080:
                    self.uploadFail("Incorrect resolution for file %s.\n Resolution was %sx%s, required 1920x1080" % (fileName, width, height))
                else:
                    self.firstClipPath = fileName
                    name = len(self.firstClipPath.split("/"))
                    new_name = (self.firstClipPath.split("/")[name-1]).replace(".mp4", "")
                    self.firstClipCred.setText(new_name)

                    firstClip = scriptwrapper.DownloadedTwitchClipWrapper("", "", "", "", None, 0, 0, 0, 0)
                    firstClip.author_name = new_name
                    firstClip.mp4 = self.firstClipPath
                    firstClip.upload = True

                    media_info = MediaInfo.parse(self.firstClipPath)
                    duration = media_info.tracks[0].duration / 1000
                    firstClip.vid_duration = float(duration)



                    self.videoWrapper.scriptWrapper.addClipAtStart(firstClip)
                    self.populateTreeWidget()
                    self.chooseFirstClip.setText("Reselect First Clip")
            except Exception as e:
                self.uploadFail("Error occured uploading file \n %s" % (e))



    def saveDefaultIntro(self):
        with open(f'Save Data/defaultintro.save', 'wb') as pickle_file:
            pickle.dump(self.introClip, pickle_file)

    def saveDefaultInterval(self):
        with open(f'Save Data/defaultinterval.save', 'wb') as pickle_file:
            pickle.dump(self.intervalClipPath, pickle_file)


    def saveDefaultOutro(self):
        with open(f'Save Data/defaultoutro.save', 'wb') as pickle_file:
            pickle.dump(self.outroClipPath, pickle_file)


    def loadDefaultIntro(self):
        if os.path.exists("Save Data/defaultintro.save"):
            with open(f'Save Data/defaultintro.save', 'rb') as pickle_file:
                self.introClip = pickle.load(pickle_file)
                self.introClipPath = self.introClip.mp4
                self.defaultIntro.setChecked(True)
                self.chooseIntro.setText("Reselect Intro")

    def loadDefaultInterval(self):
        if os.path.exists("Save Data/defaultinterval.save"):
            with open(f'Save Data/defaultinterval.save', 'rb') as pickle_file:
                self.intervalClip = pickle.load(pickle_file)
                self.intervalClipPath = self.intervalClip
                self.defaultInterval.setChecked(True)
                self.chooseInterval.setText("Reselect Interval")


    def loadDefaultOutro(self):
        if os.path.exists("Save Data/defaultoutro.save"):
            with open(f'Save Data/defaultoutro.save', 'rb') as pickle_file:
                self.outroClip = pickle.load(pickle_file)
                self.outroClipPath = self.outroClip
                self.defaultOutro.setChecked(True)
                self.chooseOutro.setText("Reselect Outro")


    #Collecting all of the information for video generator
    def exportVideo(self):
        intervalCheck = True if (self.intervalClipPath is not None and settings.enforceInterval) or not settings.enforceInterval else False
        firstClipCheck = True if (self.firstClipPath is not None and settings.enforceFirstClip) or not settings.enforceFirstClip else False
        introClipCheck = True if (self.introClipPath is not None and settings.enforceIntro) or not settings.enforceIntro else False
        outroClipCheck = True if (self.outroClipPath is not None and settings.enforceOutro) or not settings.enforceOutro else False

        if intervalCheck is True and firstClipCheck is True and introClipCheck is True and outroClipCheck is True:
            self.mediaPlayer.stop()
            final_clips = self.videoWrapper.scriptWrapper.getFinalClips()




            with_intro = []

            if settings.enforceIntro:
                self.introClip = scriptwrapper.DownloadedTwitchClipWrapper("", "", " ", "", None, 0, 0, 0, 0)
                self.introClip.author_name = None
                self.introClip.mp4 = self.introClipPath
                self.introClip.isIntro = True
                self.introClip.isInterval = False
                self.introClip.upload = True
                self.introClip.isUsed = True


                media_info_intro = MediaInfo.parse(self.introClipPath)
                duration_intro = media_info_intro.tracks[0].duration / 1000

                self.introClip.vid_duration = float(duration_intro)


            if settings.enforceInterval:
                self.intervalClip = scriptwrapper.DownloadedTwitchClipWrapper("", "", " ", "", None, 0, 0, 0, 0)
                self.intervalClip.author_name = None
                self.intervalClip.mp4 = self.intervalClipPath
                self.intervalClip.isInterval = True
                self.intervalClip.isIntro = False
                self.intervalClip.upload = True
                self.intervalClip.isUsed = True

                media_info_interval = MediaInfo.parse(self.intervalClipPath)
                duration_interval = media_info_interval.tracks[0].duration / 1000

                self.intervalClip.vid_duration = float(duration_interval)


            if settings.enforceOutro:
                self.outroClip = scriptwrapper.DownloadedTwitchClipWrapper("", "", " ", "", None, 0, 0, 0, 0)
                self.outroClip.author_name = None
                self.outroClip.mp4 = self.outroClipPath
                self.outroClip.isOutro = True
                self.outroClip.upload = True
                self.outroClip.isUsed = True
                media_info_outro = MediaInfo.parse(self.outroClipPath)
                duration_outro = media_info_outro.tracks[0].duration / 1000
                self.outroClip.vid_duration = float(duration_outro)



            if self.defaultIntro.isChecked():
                self.saveDefaultIntro()

            if self.defaultInterval.isChecked():
                self.saveDefaultInterval()

            if self.defaultOutro.isChecked():
                self.saveDefaultOutro()


            for i, clip in enumerate(final_clips):
                with_intro.append(clip)
                if i == 0:
                    if settings.enforceInterval:
                        with_intro.append(self.intervalClip)
                    if settings.enforceIntro:
                        with_intro.append(self.introClip)

            if settings.enforceOutro:
                with_intro.append(self.outroClip)


            self.videoWrapper.final_clips = with_intro
            self.clipupload = ClipUploadMenu(self.videoWrapper, self.videoName.text())
            self.clipupload.show()



        else:
            print("Choose intro clip and first clip")

    #Converting the video duration/position to seconds so it makes sense
    def getPositionInSecs(self):
        try:
            index = self.playlist.currentIndex()
            vid_position = self.mediaPlayer.position()
            vid_duration = self.mediaPlayer.duration()
            vid_percentage = (vid_position / vid_duration)
            twitchclip = self.videoWrapper.scriptWrapper.getCommentInformation(self.mainCommentIndex)
            return int(twitchclip.vid_duration * vid_percentage)
        except:
            pass
    

    def videoExportConfirmation(self):
        msg = 'Is the video long enough?\nIs everything properly cut?'
        buttonReply = QMessageBox.information(self, 'Video Export Confirmation', msg, QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if buttonReply == QMessageBox.Yes:


            intervalCheck = True if (self.intervalClipPath is not None and settings.enforceInterval) or not settings.enforceInterval else False
            firstClipCheck = True if (self.firstClipPath is not None and settings.enforceFirstClip) or not settings.enforceFirstClip else False
            introClipCheck = True if (self.introClipPath is not None and settings.enforceIntro) or not settings.enforceIntro else False
            outroClipCheck = True if (self.outroClipPath is not None and settings.enforceOutro) or not settings.enforceOutro else False


            msg = "Could not publish due to the following reasons: \n"
            if not intervalCheck:
                msg += "No interval selected, but interval expected (see config.ini)\n"
            if not firstClipCheck:
                msg += "No first clip selected, but first clip expected (see config.ini)\n"
            if not introClipCheck:
                msg += "No intro clip selected, but intro expected (see config.ini)\n"
            if not outroClipCheck:
                msg += "No outro clip selected, but outro expected (see config.ini)\n"

            amountClips = len(self.videoWrapper.scriptWrapper.getKeptClips())
            if amountClips < 2:
                msg += "Not enough clips! Need at least two clips to be kept."

            if intervalCheck is False or firstClipCheck is False or introClipCheck is False or outroClipCheck is False or amountClips < 2:
                self.publishFail(msg)
                return



            self.mediaPlayer.stop()
            self.close()
            self.exportVideo()
            print('Yes clicked.')
        if buttonReply == QMessageBox.Cancel:
            print('Cancel')

    def uploadFail(self, msg):
        buttonReply = QMessageBox.information(self, 'Upload fail', msg, QMessageBox.Ok)

    def publishFail(self, msg):
        buttonReply = QMessageBox.information(self, 'Publish fail', msg, QMessageBox.Ok)




