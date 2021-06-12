# NOW FIXED using new TikTok API! Special thanks to https://github.com/avilash/TikTokAPI-Python for the API! Thanks for being patient. See below server config file instructions for new info. Feedback Welcome!

# TikTok-Compilation-Video-Generator

A system of bots that collects clips automatically via custom made filters, lets you easily browse these clips, and puts them together into a compilation video ready to be uploaded straight to any social media platform. Full VPS support is provided, along with an accounts system so multiple users can use the bot at once.
This bot is split up into three separate programs. The server. The client. The video generator. These programs perform different functions that when combined creates a very powerful system for auto generating compilation videos.


TikTok compilation videos are a new phenomena that are quickly taking over the internet. They wrack up a lot of views and can quickly grow a channels follower base. There’s quite literally an endless supply of TikTok videos to choose from so the potential for growing channels is limitless. However there are several challenges involved in creating compilation videos. This bot (or series of programs) addresses many of these issues.


# Full VPS Support and Account System
Since the bot is split up into three different programs, communications between the programs uses a combination HTTP and FTP servers to move information from one program to the other. The FTP servers are used to move mp4 files around while the HTTP servers are for general information and usually are in the form of json. FTP requires authorisation for each client and therefore this provides the basis of the account system. You can add or remove users and set there password in the server program. This username and password combination is required in the video editor program. Therefore this works perfectly for a multi man operation as allows for multiple people to use the bot at once. 

# What this bot does.
1.	Passively downloads and stores clips from TikTok for any user created filter. The clips are automatically kept track of in a clip bin database. 

2.	Provides a video editor interface connected directly to the clip bin database, allowing you to easily go through the clips. The interface is somewhat similar to that of tinder, where you can keep/skip a video clip. 

3.	A video generator that compiles the clips from the video editor, generating a mp4 video where that you can upload to any platform.

Bot Showcase Video:
https://www.youtube.com/watch?v=-yXEDeiQBuk


There are three separate programs that make up the TikTok bot.

# 1.	Server Program

Function:

•	Automatically downloads clips from TikTok for any categories that you select.

•	Can manage accounts for the client logins

Automatic Downloader Notes

The automatic downloader side of the server is designed in a way to get around the TikTok limitations for getting the highlight clips. 

It is split into two different processes:

1.	Finding the clip and obtaining it’s URL

2.	Downloading the clip via the URL

There are no restrictions on downloading the clips and this is simple to do once a URL is obtained. However finding the top clips in the first place is another story.

TikTok only gives you access to about 2000 clips for each request entered in the API call. This would not be a sufficient amount of clips if the find/download process is only initiated when the bot is used for video editing. Therefore it is recommended to run this process automatically to build up a large clip bin, preferably on a VPS. This is largely down to the usage of the bot - heavy usage will demand a large amount of clips, and therefore turning on the automated find/download process is recommended for this case. 


# 2.	Video Editor Program

This is the actual user interface used to browse the clips in the server clip bin. This is a fairly simple process, for any one clip you have the option to keep or remove it. 


# 3.	Video Generator Program
This actually puts together the clips into a compilation video. It also generates a credits text file with all the usernames of the TikToks used in the video.

# Dependencies.

FFMPEG is required for the Video Generator Program. (must be added to system path so can be called from command line)

A MySQL server is required for the Server program.


# Config Settings

Additional settings that only take effect on start-up are stored in a config file for each program. Any changes made require a restart to the particular program.



# Code pointers

# Database: (tiktokdb)
Table clip_bin

clip_num : iterator

clip_id : Unique id for clip provided by TikTok

date: Date when clip recorded

status: The status of the clip
•	FOUND = information found about clip but not downloaded yet.

•	DOWNLOADED = Clip downloaded and ready for editing

•	USED = Used in video (mp4 file has been deleted)

•	MISSING = Can occur after “Update Missing Status” clicked. Clips with status previously marked as DOWNLOADED, but mp4 cannot be found will be marked as MISSING.

clipwrapper: clip’s ClipWrapper() from scriptwrapper.py

filter_name: Filter name that was used to obtain this clip


Table filters

num : iterator

name : The filter name

filterwrapper : The pickled filter object. Contains all the rules required for the finding process


# Server

main.py : start point

database.py : all the sql queries are written here

server.py : FTP and HTTP Servers are handled here.

settings.py : Data loaded in from config.ini

tiktok.py : Where the API calls are made to TikTok with the download/find methods.

autodownloader.py : A wrapper for the download/find process utilised in autodownloaderUI.py

autodownloaderUI.py : Where the UI is programmed

scriptwrapper.py : Various wrappers for the TikTok clips here. Formatting of the video occurs here in the “reformatPartialJson” method


# Client

main.py : start point

client.py : Communications with the server http and ftp occur here

settings.py : Data loaded in from config.ini

scriptwrapper.py : Various wrappers for tiktok clips / entire videos are stored here

clientUI.py : Where the UI is programmed


# Video Generator

main.py : start point

server.py : FTP and HTTP Servers are handled here.

settings.py : Data loaded in from config.ini

scriptwrapper.py : Various wrappers for tiktok clips / entire videos are stored here

vidGen.py : Methods for video rendering here see “renderVideo”

vidgenUI.py : Where the UI is programmed


# Config settings:

Server config

[server_details]

address = 127.0.0.1  Server Address

http_port = 8000   Server HTTP Port

ftp_port = 2121  Server FTP Port


[video_generator_location]

address = 127.0.0.1  Video Generator Address

http_port = 8001 Video Generator HTTP Port

ftp_port = 2122  Video Generator FTP Port

ftp_user = VidGen  Video Generator FTP Client name

ftp_password = password  Video Generator FTP Client password


[tiktok]

language = en  Clip language

s_v_web_id =

tt_webid = 

"Get your keys from Cookie. You can get them from the Applications tab in Chrome developer console.
By default it used hardcoded values which may not work after some time.
The keys to extract are s_v_web_id and tt_webid"

[mysql_database]

databasehost = localhost  MySQL Server address

databaseuser = root  MySQL Server user

databasepassword =  MySQL Server user password


# Video editor client config
[server_location]

address = 127.0.0.1  Server address

server_http_port = 8000  Server HTTP port

server_ftp_port = 2121  Server FTP port


[auto_login]

username = admin  User registered in server

password = password  User registered in server’s password

auto_login = true  Insert the above details into the login window on startup


[video_settings]

enforce_interval = True  Forces you to select a interval for your video

enforce_intro = True  Forces you to select a intro for your video

enforce_outro = True  Forces you to select a outro for your video

enforce_firstclip = True  Forces you to select a first clip for your video


# Video Generator config file

[video_generator_details]

address = 127.0.0.1  Video Generator Address

http_port = 8001  Video Generator HTTP port

ftp_port = 2122  Video Generator FTP port

ftp_user = VidGen  Video Generator FTP user

ftp_password = password  Video Generator FTP user’s password


[server_location]

address = 127.0.0.1  Server address

http_port = 8000  Server HTTP port

ftp_port = 2121  Server FTP port


[rendering]

fps = 30  FPS to render video at if useMinimumFps or useMaximumFps are both true

useMinimumFps = True  Sets all the individual clips FPS to the lowest FPS of the clips (recommended)

useMaximumFps = False  Sets all the individual clips FPS to the highest FPS of the clips 

backupVideos = True  Will automatically backup each video send to the video generator. These can be rerendered or deleted via the UI


# Python (recommend 3.7+ and 64bit on windows)


•	requests

•	PyQt5

•	Pymediainfo

•	Opencv-python

•	Pyftpdlib

•	Pydub

•	mysql-connector-python

•	PyTikTokAPI

