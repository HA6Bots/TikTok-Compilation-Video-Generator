import os
import configparser
from sys import platform

currentPath = os.path.dirname(os.path.realpath(__file__))

vid_filepath = "VideoFiles"
final_video_path = "FinalVideos"
asset_file_path = "Assets"
video_data_path = "VideoData"
backup_path = "Backup"

serveraddress = "127.0.0.1"
# The port the FTP server will listen on.
# This must be greater than 1023 unless you run this script as root.
FTP_PORT = 2121
HTTP_PORT = 8000


temp_path = "Temp"

first_clip_name = ''


videoGeneratorAddress = "127.0.0.1"
videoGeneratorFTPPort = 2122
videoGeneratorHTTPPort = 8001
videoGeneratorFTPUser = "VidGen"
videoGeneratorFTPPassword = "password"


databasehost = "localhost"
databaseuser = "root"
databasepassword = ""
s_v_web_id = ""
tt_webid = ""

language = "en"

config = configparser.RawConfigParser()

configpath = None

if platform == "linux" or platform == "linux2" or platform == "darwin":
    configpath = "%s/config.ini" % currentPath
else:
    configpath = "%s\\config.ini" % currentPath

def generateConfigFile():
    if not os.path.isfile(configpath):
        print("Could not find config file in location %s, creating a new one" % configpath)
        config.add_section("server_details")
        config.set("server_details", 'address', '127.0.0.1')
        config.set("server_details", 'http_port', '8000')
        config.set("server_details", 'ftp_port', '2121')
        config.add_section("video_generator_location")
        config.set("video_generator_location", 'address', '127.0.0.1')
        config.set("video_generator_location", 'http_port', '8001')
        config.set("video_generator_location", 'ftp_port', '2122')
        config.set("video_generator_location", 'ftp_user', 'VidGen')
        config.set("video_generator_location", 'ftp_password', 'password')
        config.add_section("tiktok")
        config.set("tiktok", 'language', 'en')
        config.set("tiktok", 's_v_web_id', '')
        config.set("tiktok", 'tt_webid', '')
        config.add_section("mysql_database")
        config.set("mysql_database", 'databasehost', 'localhost')
        config.set("mysql_database", 'databaseuser', 'root')
        config.set("mysql_database", 'databasepassword', '')

        with open(configpath, 'w') as configfile:
            config.write(configfile)
    else:
        print("Found config in location %s" % configpath)
        loadValues()

def loadValues():
    global FTP_PORT, HTTP_PORT, serveraddress, videoGeneratorAddress, videoGeneratorFTPPort, videoGeneratorHTTPPort, videoGeneratorFTPUser,\
        videoGeneratorFTPPassword, language, databasehost, databasepassword, databaseuser, s_v_web_id, tt_webid
    config = configparser.RawConfigParser()
    config.read(configpath)
    serveraddress = config.get('server_details', 'address')
    HTTP_PORT = config.getint('server_details', 'http_port')
    FTP_PORT = config.getint('server_details', 'ftp_port')
    videoGeneratorAddress = config.get('video_generator_location', 'address')
    videoGeneratorHTTPPort = config.getint('video_generator_location', 'http_port')
    videoGeneratorFTPPort = config.getint('video_generator_location', 'ftp_port')
    videoGeneratorFTPUser = config.get('video_generator_location', 'ftp_user')
    videoGeneratorFTPPassword = config.get('video_generator_location', 'ftp_password')
    language = config.get('tiktok', 'language')
    s_v_web_id = config.get('tiktok', 's_v_web_id')
    tt_webid = config.get('tiktok', 'tt_webid')
    databasehost = config.get("mysql_database", 'databasehost')
    databaseuser = config.get("mysql_database", 'databaseuser')
    databasepassword = config.get("mysql_database", 'databasepassword')
