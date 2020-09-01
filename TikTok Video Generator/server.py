from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from threading import Thread
import http.server
import socketserver
import json
import cgi
from time import sleep
import scriptwrapper
import random
import vidGen
import traceback, sys
import pickle
import os
import settings
import ftplib

current_path = os.path.dirname(os.path.realpath(__file__))


# The directory the FTP user will have full read/write access to.
FTP_DIRECTORY = current_path


def testFTPConnection():
    try:
        ftp = ftplib.FTP()
        ftp.connect(settings.server_address, settings.serverFTPPort)
        ftp.login(settings.FTP_USER, settings.FTP_PASSWORD)
        return True
    except Exception as e:
        return False



def getFileNames(file_path):
    files = [os.path.splitext(filename)[0] for filename in os.listdir(file_path)]
    return files

def uploadCompleteVideo(name):
    try:
        if os.path.exists("%s/%s.txt" % (settings.final_video_path, name)):
            ftp = ftplib.FTP()
            ftp.connect(settings.server_address, settings.serverFTPPort)
            ftp.login(settings.FTP_USER, settings.FTP_PASSWORD)
            ftp.cwd("FinalVideos")
            sleep(10)
            print("Uploading %s.mp4" % name)
            filemp4 = open("%s/%s.mp4" % (settings.final_video_path, name),'rb')
            ftp.storbinary('STOR %s.mp4' % name, filemp4, blocksize=262144)
            filemp4.close()
            print("Uploading %s.txt" % name)
            filetxt = open("%s/%s.txt" % (settings.final_video_path, name),'rb')
            ftp.storbinary('STOR %s.txt' % name, filetxt, blocksize=262144)
            filetxt.close()
            print("Done Uploading %s" % name)
            os.remove(f"{settings.final_video_path}/%s.mp4" % name)
            os.remove(f"{settings.final_video_path}/%s.txt" % name)
        else:
            pass
    except Exception as e:
        print(e)




def sendThread():
    while True:
        sleep(5)
        savedFilesDuplicates = getFileNames(f'{settings.final_video_path}')
        savedFiles = list(dict.fromkeys(savedFilesDuplicates))
        for file in savedFiles:
            uploadCompleteVideo(file)




def startFTPServer():
    authorizer = DummyAuthorizer()

    authorizer.add_user(settings.FTP_USER, settings.FTP_PASSWORD, FTP_DIRECTORY, perm='elradfmw')

    handler = FTPHandler
    handler.authorizer = authorizer

    handler.banner = "pyftpdlib based ftpd ready."

    address = (settings.videogeneratoraddress, settings.FTP_PORT)
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

    # GET sends back a Hello world message
    def do_GET(self):

        self._set_headers()
        try:
            if "/sendscript" == self.path:
                length = int(self.headers.get('content-length'))
                message = json.loads(self.rfile.read(length))
                video = scriptwrapper.createTwitchVideoFromJSON(message)
                folder = message["vid_folder"]
                scriptwrapper.saveTwitchVideo(folder, video)
                self.wfile.write(json.dumps({'received': True}).encode())
                pass
            if "/getrenderinfo" == self.path:


                render_data = {'max_progress': vidGen.render_max_progress,
                                             "current_progress" : vidGen.render_current_progress,
                                             "render_message" : vidGen.render_message, "music" : None}
                self.wfile.write(json.dumps(render_data).encode())
                pass
        except Exception as e:
            traceback.print_exc(file=sys.stdout)

            print(e)
            print("Error occured with http requests")
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
    with socketserver.TCPServer((settings.videogeneratoraddress, settings.HTTP_PORT), HTTPHandler) as httpd:
        print("serving at port", settings.HTTP_PORT)
        httpd.serve_forever()


def init():
    Thread(target=startFTPServer).start()
    Thread(target=startHTTPServer).start()


