import subprocess
import os
import math
import datetime
current_path = os.path.dirname(os.path.realpath(__file__))



class TwitchVideo():
    def __init__(self, scriptwrapper):
        self.scriptWrapper = scriptwrapper
        self.final_clips = None


class DownloadedTwitchClipWrapper():
    def __init__(self, id, author_name, clip_title, mp4name, vid_duration, diggCount, shareCount, playCount, commentCount):

        self.id = id
        self.author_name = author_name
        self.mp4 = mp4name
        self.clip_name = clip_title
        self.vid_duration = vid_duration
        self.upload = False
        self.isIntro = False
        self.isOutro = False
        self.isInterval = False
        self.isUsed = False
        self.audio = 1
        self.diggCount = diggCount
        self.shareCount = shareCount
        self.playCount = playCount
        self.commentCount = commentCount
        #Getting duration of video clips to trim a percentage of the beginning off



class ScriptWrapper():
    def __init__(self, script):
        self.rawScript = script
        self.scriptMap = []
        self.setupScriptMap()


    def addClipAtStart(self, clip):
        self.rawScript = [clip] + self.rawScript
        self.scriptMap = [True] + self.scriptMap


    def addScriptWrapper(self, scriptwrapper):
        self.rawScript = self.rawScript + scriptwrapper.rawScript
        self.scriptMap = self.scriptMap + scriptwrapper.scriptMap


    def moveDown(self, i):
        if i > 0:
            copy1 = self.scriptMap[i-1]
            copy2 = self.rawScript[i-1]

            self.scriptMap[i-1] = self.scriptMap[i]
            self.rawScript[i-1] = self.rawScript[i]

            self.scriptMap[i] = copy1
            self.rawScript[i] = copy2
        else:
            print("already at bottom!")

    def moveUp(self, i):
        if i < len(self.scriptMap) - 1:
            copy1 = self.scriptMap[i+1]
            copy2 = self.rawScript[i+1]

            self.scriptMap[i+1] = self.scriptMap[i]
            self.rawScript[i+1] = self.rawScript[i]

            self.scriptMap[i] = copy1
            self.rawScript[i] = copy2
        else:
            print("already at top!")

    def setupScriptMap(self):
        for mainComment in self.rawScript:
            line = False
            self.scriptMap.append(line)


    def keep(self, mainCommentIndex):
        self.scriptMap[mainCommentIndex] = True

    def skip(self, mainCommentIndex):
        self.scriptMap[mainCommentIndex] = False

    def setCommentStart(self, x, start):
        self.rawScript[x].start_cut = start

    def setCommentEnd(self, x, end):
        self.rawScript[x].end_cut = end

    def setCommentAudio(self, x, audio):
        self.rawScript[x].audio = audio

    def getCommentData(self, x, y):
        return self.rawScript[x][y]

    def getCommentAmount(self):
        return len(self.scriptMap)

    def getEditedCommentThreadsAmount(self):
        return len([commentThread for commentThread in self.scriptMap if commentThread[0] is True])

    def getEditedCommentAmount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        count = 0
        for commentThread in commentThreads:
            for comment in commentThread:
                if comment is True:
                    count += 1
        return count

    def getEditedWordCount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        word_count = 0
        for x, commentThread in enumerate(commentThreads):
            for y, comment in enumerate(commentThread):
                if comment is True:
                    word_count += len(self.rawScript[x][y].text.split(" "))
        return word_count

    def getEditedCharacterCount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        word_count = 0
        for x, commentThread in enumerate(commentThreads):
            for y, comment in enumerate(commentThread):
                if comment is True:
                    word_count += len(self.rawScript[x][y].text)
        return word_count


    def getCommentInformation(self, x):
        return self.rawScript[x]


    def getKeptClips(self):
        final_script = []
        for i, clip in enumerate(self.scriptMap):
            if clip:
                final_script.append(self.rawScript[i])
        return final_script


    def getFinalClips(self):
        final_script = []
        for i, clip in enumerate(self.scriptMap):
            clipwrapper = self.rawScript[i]
            clipwrapper.isUsed = clip
            final_script.append(self.rawScript[i])
        return final_script


    def getEstimatedVideoTime(self):
        time = 0
        for i, comment in enumerate(self.scriptMap):
            if comment is True:
                time += round(self.rawScript[i].vid_duration, 1)
        obj = datetime.timedelta(seconds=math.ceil(time))
        return  obj
