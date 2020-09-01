import os
import configparser

currentPath = os.path.dirname(os.path.realpath(__file__))



address = "127.0.0.1"
FTP_PORT = 2121
HTTP_PORT = 8000

FTP_USER = "Tom"
FTP_PASSWORD = "password"

autoLogin = False

block_size = 262144

config = configparser.ConfigParser()

enforceInterval = True
enforceIntro = True
enforceOutro = True
enforceFirstClip = True

def generateConfigFile():
    path = "%s\\config.ini" % currentPath
    if not os.path.isfile(path):
        print("Could not find config file in location %s, creating a new one" % path)
        config.add_section("server_location")
        config.set("server_location", 'address', '127.0.0.1')
        config.set("server_location", 'server_http_port', '8000')
        config.set("server_location", 'server_ftp_port', '2121')
        config.add_section("auto_login")
        config.set("auto_login", 'username', '')
        config.set("auto_login", 'password', '')
        config.set("auto_login", 'auto_login', 'False')
        config.add_section("video_settings")
        config.set("video_settings", "enforce_interval", "True")
        config.set("video_settings", "enforce_intro", "True")
        config.set("video_settings", "enforce_outro", "True")
        config.set("video_settings", "enforce_firstclip", "True")


        with open("%s\\config.ini" % currentPath, 'w') as configfile:
            config.write(configfile)
    else:
        print("Found config in location %s" % path)
        loadValues()

def loadValues():
    global FTP_USER, FTP_PASSWORD, FTP_PORT, HTTP_PORT, address, autoLogin, \
        enforceFirstClip, enforceInterval, enforceIntro, enforceOutro
    config = configparser.ConfigParser()
    config.read("%s\\config.ini" % currentPath)
    address = config.get('server_location', 'address')
    HTTP_PORT = config.getint('server_location', 'server_http_port')
    FTP_PORT = config.getint('server_location', 'server_ftp_port')
    FTP_USER = config.get('auto_login', 'username')
    FTP_PASSWORD = config.get('auto_login', 'password')
    autoLogin = config.getboolean('auto_login', 'auto_login')

    enforceInterval = config.getboolean('video_settings', 'enforce_interval')
    enforceIntro = config.getboolean('video_settings', 'enforce_intro')
    enforceOutro = config.getboolean('video_settings', 'enforce_outro')
    enforceFirstClip = config.getboolean('video_settings', 'enforce_firstclip')
