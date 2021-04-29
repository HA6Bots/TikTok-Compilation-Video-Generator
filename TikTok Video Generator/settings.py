import os
import configparser
from sys import platform
currentPath = os.path.dirname(os.path.realpath(__file__))


server_address = "127.0.0.1"
serverFTPPort = 2121

videogeneratoraddress = "127.0.0.1"

# The port the FTP server will listen on.
# This must be greater than 1023 unless you run this script as root.
FTP_PORT = 2122
HTTP_PORT = 8001

FTP_USER = "VidGen"
FTP_PASSWORD = "password"


vid_finishedvids = "FinishedVids"
vid_filepath = "VideoFiles"
final_video_path = "FinalVideos"
old_clip_path = "OldClips"
video_data_path = "VideoData"
backup_path = "Backup"


server_port = 8000

fps = 15

temp_path = "Temp"

first_clip_name = ''

useMinimumFps = False
useMaximumFps = False

backupVideos = False


config = configparser.ConfigParser()

configpath = None

if platform == "linux" or platform == "linux2" or platform == "darwin":
    configpath = "%s/config.ini" % currentPath
else:
    configpath = "%s\\config.ini" % currentPath


def generateConfigFile():
    if not os.path.isfile(configpath):
        print("Could not find config file in location %s, creating a new one" % configpath)
        config.add_section("video_generator_details")
        config.set("video_generator_details", 'address', '127.0.0.1')
        config.set("video_generator_details", 'http_port', '8001')
        config.set("video_generator_details", 'ftp_port', '2122')
        config.set("video_generator_details", 'FTP_USER', 'VidGen')
        config.set("video_generator_details", 'FTP_PASSWORD', 'password')
        config.add_section("server_location")
        config.set("server_location", 'address', '127.0.0.1')
        config.set("server_location", 'http_port', '8000')
        config.set("server_location", 'ftp_port', '2122')

        config.add_section("rendering")
        config.set("rendering", 'fps', '30')
        config.set("rendering", 'useMinimumFps', 'True')
        config.set("rendering", 'useMaximumFps', 'False')
        config.set("rendering", 'backupVideos', 'True')


        with open(configpath, 'w') as configfile:
            config.write(configfile)
    else:
        print("Found config in location %s" % configpath)
        loadValues()

def loadValues():
    global server_address, serverFTPPort, videogeneratoraddress, FTP_PORT, HTTP_PORT, FTP_USER, FTP_PASSWORD, fps, server_port, useMinimumFps, useMaximumFps, backupVideos
    config = configparser.ConfigParser()
    config.read(configpath)
    videogeneratoraddress = config.get('video_generator_details', 'address')
    FTP_PORT = config.getint('video_generator_details', 'ftp_port')
    HTTP_PORT = config.getint('video_generator_details', 'http_port')
    FTP_USER = config.get('video_generator_details', 'FTP_USER')
    FTP_PASSWORD = config.get('video_generator_details', 'FTP_PASSWORD')


    server_address = config.get('server_location', 'address')
    server_port = config.get('server_location', 'http_port')
    serverFTPPort = config.getint('server_location', 'ftp_port')
    fps = config.getint('rendering', 'fps')
    useMinimumFps = config.getboolean('rendering', 'useMinimumFps')
    useMaximumFps = config.getboolean('rendering', 'useMaximumFps')
    backupVideos = config.getboolean('rendering', 'backupVideos')

