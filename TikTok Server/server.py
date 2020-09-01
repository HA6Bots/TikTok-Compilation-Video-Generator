from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from threading import Thread
import http.server
import socketserver
import json
import cgi
import database
import scriptwrapper
from copy import deepcopy
import random
import pickle
import os
import settings
import ftplib
import requests
from time import sleep
import traceback, sys

current_path = os.path.dirname(os.path.realpath(__file__))

usersList = []

max_progress = None
current_progress = None
render_message = None



settings.generateConfigFile()
vidgenhttpaddress = "%s:%s" % (settings.videoGeneratorAddress, settings.videoGeneratorHTTPPort)


# The directory the FTP user will have full read/write access to.
FTP_DIRECTORY = current_path


def getGames():
    filters = database.getAllSavedFilters()
    formatted = []
    for filter in filters:
        formatted.append(filter[0])
    return formatted


def getClips(filter, amount):
    clips = database.getFilterClipsByStatusLimit(filter, "DOWNLOADED", amount)
    files = []
    for clip in clips:
        info = {"id" : clip.id, "mp4" : clip.mp4, "author_name" : clip.author_name, "duration" : clip.estDuration, "clip_title" : clip.text,
                "diggCount" : clip.diggCount, "shareCount" : clip.shareCount, "playCount" : clip.playCount, "commentCount" : clip.commentCount}
        files.append(info)
    return files
    #print(files)

def getClipsWithoutIds(game, amount, ids):
    clips = database.geClipsByStatusWithoutIds(game, "DOWNLOADED", amount, ids)
    files = []
    for clip in clips:
        info = {"id" : clip.id, "mp4" : clip.mp4, "author_name" : clip.author_name, "duration" : clip.estDuration, "clip_title" : clip.text,
                "diggCount" : clip.diggCount, "shareCount" : clip.shareCount, "playCount" : clip.playCount, "commentCount" : clip.commentCount}
        files.append(info)
    return files

def getFinishedVideosList():
    finished = []
    for file in os.listdir(settings.final_video_path):
        name = file.replace(".txt", "").replace(".mp4", "")
        if name not in finished:
            finished.append(name)

    return finished



def uploadVideo(message):
    # just marks them as used clips in database
    new_json = scriptwrapper.reformatPartialJson(message)

    random_name = str(random.randint(0, 100000))
    print(f'VideoData/vid{random_name}.save')
    with open(f'VideoData/vid{random_name}.json', 'w') as f:
        json.dump(new_json, f)
    print(new_json)
    return True



def getFileNames(file_path):
    files = [os.path.splitext(filename)[0] for filename in os.listdir(file_path)]
    return files

def sendVideoContentToVidGenerator(file):
    try:
        ftp = ftplib.FTP()
        ftp.connect(settings.videoGeneratorAddress, settings.videoGeneratorFTPPort)
        ftp.login(settings.videoGeneratorFTPUser, settings.videoGeneratorFTPPassword)
        ftp.cwd('Temp')
        folder_name = file.replace(".json", "")
        print("Sending %s to video generator" % folder_name)
        saveName = file
        try:
            ftp.mkd(folder_name)
        except ftplib.error_perm as e:
            print(e)
        ftp.cwd('/Temp/%s/' % folder_name)
        jsonFile = None
        jsonFileCopy = None
        with open(f'{settings.video_data_path}/{file}.json') as json_file:
            jsonFile = (json.load(json_file))
        jsonFileCopy = deepcopy(jsonFile)

        kept_clips = []
        for clip in jsonFile["clips"]:
            if clip["keep"]:
                mp4 = clip["mp4"]
                if ".mp4" not in mp4:
                    mp4 = "%s/%s.mp4"%(settings.vid_filepath, mp4)
                file = open(mp4,'rb')
                name = len(mp4.split("/"))
                mp4name = mp4.split("/")[name-1]

                ftp.storbinary('STOR %s' % mp4name, file, blocksize=262144)
                file.close()
                clip["mp4"] = '/Temp/%s/%s' % (folder_name, mp4name)

                kept_clips.append(clip)

        jsonFile["clips"] = kept_clips
        jsonFile["vid_folder"] = folder_name
        r = requests.get(f'http://{vidgenhttpaddress}/sendscript', json=jsonFile,  headers={'Accept-Encoding': None})
        sucess = r.json()["received"]
        os.remove(settings.video_data_path + "/" + str(saveName) + ".json")
        print("Done sending %s" % folder_name)

        for clip in jsonFileCopy["clips"]:
            mp4 = clip["mp4"]
            try:
                if "UploadedFiles" in mp4:
                    print("Deleting %s" % mp4)
                    os.remove(mp4)
                else:
                    print("deleting %s/%s.mp4" % (settings.vid_filepath, mp4))
                    os.remove("%s/%s.mp4" % (settings.vid_filepath, mp4))
            except Exception as e:
                print("could not delete mp4 %s" % mp4)


            #print(clip["mp4"])
            #print(clip["keep"])
        #print(ftp.nlst())
    except ConnectionRefusedError:
        print("Video Generator is offline")

def VideoGeneratorCommunications():
    while True:
        savedFiles = getFileNames(f'{settings.video_data_path}')
        saved_videos = []
        for file in savedFiles:
            with open(f'{settings.video_data_path}/{file}.json') as json_file:
                saved_videos.append(json.load(json_file))

        for name in savedFiles:
            sendVideoContentToVidGenerator(name)
        sleep(5)


def VideoGeneratorRenderStatus():
    global max_progress, current_progress, render_message
    while True:
        sleep(5)
        try:
            r = requests.get(f'http://{vidgenhttpaddress}/getrenderinfo',  headers={'Accept-Encoding': None})
            renderData = r.json()
            max_progress = renderData["max_progress"]
            current_progress = renderData["current_progress"]
            render_message = renderData["render_message"]

        except Exception:
            print("video generator offline")


def startFTPServer():
    authorizer = DummyAuthorizer()

    for user in usersList:
        authorizer.add_user(user[0], user[1], FTP_DIRECTORY, perm='elradfmw')



    handler = FTPHandler
    handler.authorizer = authorizer

    handler.banner = "pyftpdlib based ftpd ready."

    address = (settings.serveraddress, settings.FTP_PORT)
    server = FTPServer(address, handler)

    server.max_cons = 256
    server.max_cons_per_ip = 5

    server.serve_forever()


class HTTPHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        try:
            if "/getgames" == self.path:
                games = getGames()
                self.wfile.write(json.dumps({'games': games}).encode())
            elif "/getclips" == self.path:
                length = int(self.headers.get('content-length'))
                message = json.loads(self.rfile.read(length))
                game = message["game"]
                amount = message["amount"]
                clips = getClips(game, amount)
                self.wfile.write(json.dumps({'clips': clips}).encode())
            elif "/getclipswithoutids" == self.path:
                length = int(self.headers.get('content-length'))
                message = json.loads(self.rfile.read(length))
                game = message["game"]
                amount = message["amount"]
                ids = message["ids"]
                clips = getClipsWithoutIds(game, amount, ids)
                self.wfile.write(json.dumps({'clips': clips}).encode())
            elif "/uploadvideo" == self.path:
                length = int(self.headers.get('content-length'))
                message = json.loads(self.rfile.read(length))
                success = uploadVideo(message)
                self.wfile.write(json.dumps({'upload_success': success}).encode())
            elif "/getfinishedvideoslist" == self.path:
                finishedvideos = getFinishedVideosList()
                self.wfile.write(json.dumps({'videos': finishedvideos}).encode())
            elif "/getrenderinfo" == self.path:


                render_data = {'max_progress': max_progress,
                                             "current_progress" : current_progress,
                                             "render_message" : render_message}
                self.wfile.write(json.dumps(render_data).encode())
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
        #self.wfile.write(json.dumps({'hello': 'world', 'received': 'ok'}).encode())

    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))

        # add a property to the object, just to mess with data
        message['received'] = 'ok'

        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(message))


def startHTTPServer():
    with socketserver.TCPServer((settings.serveraddress, settings.HTTP_PORT), HTTPHandler) as httpd:
        print("serving at port", settings.HTTP_PORT)
        httpd.serve_forever()


def createDefaultUserTable():
    return [(settings.videoGeneratorFTPUser, settings.videoGeneratorFTPPassword)]

def saveUsersTable():
    print(f'Saving users table')
    with open(f"{current_path}/usertable.save", 'wb') as pickle_file:
        pickle.dump(usersList, pickle_file)


def init():
    global usersList
    if not os.path.exists(f"{current_path}/usertable.save"):
        print("Didn't find users table creating new one.")
        usersList = createDefaultUserTable()
        saveUsersTable()
    else:
        with open(f'{current_path}/usertable.save', 'rb') as pickle_file:
            print("Found users table.")
            usersList = pickle.load(pickle_file)

    Thread(target=startFTPServer).start()
    Thread(target=startHTTPServer).start()


