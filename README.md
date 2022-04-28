
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]




<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/HA6Bots/TikTok-Compilation-Video-Generator">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">TikTok Compilation Video Generator</h3>

  <p align="center">
    A system of bots that collects clips automatically via custom made filters, lets you easily browse these clips, and puts them together into a compilation video ready to be uploaded straight to any social media platform
    <br />
    <a href="https://github.com/HA6Bots/TikTok-Compilation-Video-Generator"><strong>Explore the docs »</strong></a>
    <br />
    <br />
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
	    <li><a href="#Full-VPS-Support-and-Account-System">Full VPS Support and Account System</a></li>
	    <li><a href="#What-this-bot-does">What this bot does</a></li>
        <li><a href="#Bot-Showcase-Video">Bot Showcase Video</a></li>
		<li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
	<li>
      <a href="#file-system">File System and Explanation</a>
      <ul>
	    <li><a href="#server-program">Server Program</a></li>
	    <li><a href="#video-editor-program">Video Editor Program</a></li>
        <li><a href="#video-generator-program">Video Generator Program</a></li>
	  </ul>
	</li>
    <li>	 
	  <a href="#config-file-explanation">Config Files and Explanation</a>
      <ul>
	    <li><a href="#server-config">Server Config</a></li>
	    <li><a href="#video-editor-config">Video Editor Config</a></li>
        <li><a href="#video-generator-config">Video Generator Config</a></li>
      </ul> 
	</li> 
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project



A system of bots that collects clips automatically via custom made filters, lets you easily browse these clips, and puts them together into a compilation video ready to be uploaded straight to any social media platform. Full VPS support is provided, along with an accounts system so multiple users can use the bot at once. This bot is split up into three separate programs. The server. The client. The video generator. These programs perform different functions that when combined creates a very powerful system for auto generating compilation videos.

TikTok compilation videos are a new phenomena that are quickly taking over the internet. They wrack up a lot of views and can quickly grow a channels follower base. There’s quite literally an endless supply of TikTok videos to choose from so the potential for growing channels is limitless. However there are several challenges involved in creating compilation videos. This bot (or series of programs) addresses many of these issues.

### Full VPS Support and Account System
Since the bot is split up into three different programs, communications between the programs uses a combination HTTP and FTP servers to move information from one program to the other. The FTP servers are used to move mp4 files around while the HTTP servers are for general information and usually are in the form of json. FTP requires authorisation for each client and therefore this provides the basis of the account system. You can add or remove users and set there password in the server program. This username and password combination is required in the video editor program. Therefore this works perfectly for a multi man operation as allows for multiple people to use the bot at once.

### What this bot does
Passively downloads and stores clips from TikTok for any user created filter. The clips are automatically kept track of in a clip bin database.

Provides a video editor interface connected directly to the clip bin database, allowing you to easily go through the clips. The interface is somewhat similar to that of tinder, where you can keep/skip a video clip.

A video generator that compiles the clips from the video editor, generating a mp4 video where that you can upload to any platform.

### Bot Showcase Video
* [Youtube](https://www.youtube.com/watch?v=-yXEDeiQBuk) 

There are three separate programs that make up the TikTok bot.

### Built With

This section should list any major frameworks used in development.
* [Python](https://www.python.org/)



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* FFMPEG
* [Download FFMPEG](https://www.ffmpeg.org/download.html)
  ```
  Must be added to system path so can be called from command line.
  ```
* MySql
* [Download MySql](https://dev.mysql.com/downloads/)

### Installation

1. Install Modules
   ```sh
    pip install -r requirements.txt
   ```
2. Get TikTok Cookies
   * Go to [tiktok](https://www.tiktok.com/)
   * Login to you account
   * Go to your profile
   * Open Developer Tools (cltr+shift+i)
   * In Developer console go to apllication
   * Find cookies Folder .
   * In cookies folder find 's_v_web_id' and 'sid_ucp_v1'
3. Edit config file in `Tiktok server`
   * Add value of 's_v_web_id' and 'sid_ucp_v1' from cookie.
   * Edit database details.
3. Check and edit config file in `Tiktok Client` and `TikTok Video Generator`


<!-- USAGE EXAMPLES -->
## Usage

1. Start mysql database.

2. Go to `Tiktok Server` and start server.
    ```sh
    py main.py
   ```   
   * Add filter , make it live.
   * search and download Clips
   
3. Go to `Tiktok Client` and start.
    ```sh
    py main.py
   ```
   *Edit clips
   *Change duration, Intro, Outro and Interval.
   
4. Go to `Tiktok Video Generator` and start.
	```sh
    py main.py
   ```
   *Select and Render Final Video file .

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/HA6Bots/TikTok-Compilation-Video-Generator/issues) for a list of proposed features (and known issues).




<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.





## FIle System 


### Server Program

Function:

• Automatically downloads clips from TikTok for any categories that you select.

• Can manage accounts for the client logins

Automatic Downloader Notes

The automatic downloader side of the server is designed in a way to get around the TikTok limitations for getting the highlight clips.

It is split into two different processes:

Finding the clip and obtaining it’s URL

Downloading the clip via the URL

There are no restrictions on downloading the clips and this is simple to do once a URL is obtained. However finding the top clips in the first place is another story.

TikTok only gives you access to about 2000 clips for each request entered in the API call. This would not be a sufficient amount of clips if the find/download process is only initiated when the bot is used for video editing. Therefore it is recommended to run this process automatically to build up a large clip bin, preferably on a VPS. This is largely down to the usage of the bot - heavy usage will demand a large amount of clips, and therefore turning on the automated find/download process is recommended for this case.

* main.py : start point

* database.py : all the sql queries are written here

* server.py : FTP and HTTP Servers are handled here.

* settings.py : Data loaded in from config.ini

* tiktok.py : Where the API calls are made to TikTok with the download/find methods.

* autodownloader.py : A wrapper for the download/find process utilised in autodownloaderUI.py

* autodownloaderUI.py : Where the UI is programmed

scriptwrapper.py : Various wrappers for the TikTok clips here. Formatting of the video occurs here in the “reformatPartialJson” method

### Video Editor Program

This is the actual user interface used to browse the clips in the server clip bin. This is a fairly simple process, for any one clip you have the option to keep or remove it.

* main.py : start point

* client.py : Communications with the server http and ftp occur here

* settings.py : Data loaded in from config.ini

* scriptwrapper.py : Various wrappers for tiktok clips / entire videos are stored here

* clientUI.py : Where the UI is programmed

### Video Generator Program

This actually puts together the clips into a compilation video. It also generates a credits text file with all the usernames of the TikToks used in the video.

* main.py : start point

* server.py : FTP and HTTP Servers are handled here.

* settings.py : Data loaded in from config.ini

* scriptwrapper.py : Various wrappers for tiktok clips / entire videos are stored here

* vidGen.py : Methods for video rendering here see “renderVideo”

* vidgenUI.py : Where the UI is programmed


## Config File Explanation

Additional settings that only take effect on start-up are stored in a config file for each program. Any changes made require a restart to the particular program.

### Server Config

[server_details]

* address = 127.0.0.1 <-- Server Address

* http_port = 8000 <-- Server HTTP Port

* ftp_port = 2121 <-- Server FTP Port

[video_generator_location]

* address = 127.0.0.1 <-- Video Generator Address

* http_port = 8001 <-- Video Generator HTTP Port

* ftp_port = 2122 <-- Video Generator FTP Port

* ftp_user = VidGen <-- Video Generator FTP Client name

* ftp_password = password <-- Video Generator FTP Client password

[tiktok]

* language = en <-- Clip language

* s_v_web_id = value <-- Get from TikTok Cookies , Read Above.

* tt_webid = value <-- Get from TikTok Cookies , Read Above.

[mysql_database]

* databasehost = localhost <-- MySQL Server address

* databaseuser = root <-- MySQL Server user

* databasepassword =  <-- MySQL Server user password

### Video Editor Config

[server_location]

* address = 127.0.0.1 <-- Server address

* server_http_port = 8000 <-- Server HTTP port

* server_ftp_port = 2121 <-- Server FTP port

[auto_login]

* username = admin <-- User registered in server

* password = password <-- User registered in server’s password

* auto_login = true <-- Insert the above details into the login window on startup

[video_settings]

* enforce_interval = True <-- Forces you to select a interval for your video

* enforce_intro = True <-- Forces you to select a intro for your video

* enforce_outro = True <-- Forces you to select a outro for your video

* enforce_firstclip = True <-- Forces you to select a first clip for your video

### Video Generator Config

[video_generator_details]

* address = 127.0.0.1 <-- Video Generator Address

* http_port = 8001 <-- Video Generator HTTP port

* ftp_port = 2122 <-- Video Generator FTP port

* ftp_user = VidGen <-- Video Generator FTP user

* ftp_password = password <-- Video Generator FTP user’s password

[server_location]

* address = 127.0.0.1 <-- Server address

* http_port = 8000 <-- Server HTTP port

* ftp_port = 2121 <-- Server FTP port

[rendering]

* fps = 30 <-- FPS to render video at if useMinimumFps or useMaximumFps are both true

* useMinimumFps = True <-- Sets all the individual clips FPS to the lowest FPS of the clips (recommended)

* useMaximumFps = False <-- Sets all the individual clips FPS to the highest FPS of the clips

* backupVideos = True <-- Will automatically backup each video send to the video generator. These can be rerendered or deleted via the UI


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/HA6Bots/TikTok-Compilation-Video-Generator.svg?style=for-the-badge
[contributors-url]: https://github.com/HA6Bots/TikTok-Compilation-Video-Generator/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/HA6Bots/TikTok-Compilation-Video-Generator.svg?style=for-the-badge
[forks-url]: https://github.com/HA6Bots/TikTok-Compilation-Video-Generator/network/members
[stars-shield]: https://img.shields.io/github/stars/HA6Bots/TikTok-Compilation-Video-Generator.svg?style=for-the-badge
[stars-url]: https://github.com/HA6Bots/TikTok-Compilation-Video-Generator/stargazers
[issues-shield]: https://img.shields.io/github/issues/HA6Bots/TikTok-Compilation-Video-Generator.svg?style=for-the-badge
[issues-url]: https://github.com/HA6Bots/TikTok-Compilation-Video-Generator/issues
[license-shield]: https://img.shields.io/github/license/HA6Bots/TikTok-Compilation-Video-Generator.svg?style=for-the-badge
[license-url]: https://github.com/HA6Bots/TikTok-Compilation-Video-Generator/blob/master/LICENSE

[product-screenshot]: images/screenshot.png
