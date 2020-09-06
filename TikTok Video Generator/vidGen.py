import random
import os
import time
import shutil
import subprocess
import re
import cv2
from time import sleep
import datetime
from distutils.dir_util import copy_tree
import pickle
import settings

#File Paths



#Creating file paths that are needed


saved_videos = None
render_current_progress = None
render_max_progress = None
render_message = None


#------------------------------------------C O M P I L A T I O N   G E N E R A T O R------------------------------------------

#Getting Filename without extension and storing it into a list
def getFileNames(file_path):
    files = [os.path.splitext(filename)[0] for filename in os.listdir(file_path)]
    return files

def deleteSkippedClips(clips):
    for clip in clips:
        os.remove(f'{clip}')

def deleteAllFilesInPath(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def renderThread(renderingScreen):
    global saved_videos
    while True:
        time.sleep(5)
        savedFiles = getFileNames(f'{settings.temp_path}')
        saved_videos = []
        save_names = []
        for file in savedFiles:
            try:
                with open(f'{settings.temp_path}/{file}/vid.data', 'rb') as pickle_file:
                    script = pickle.load(pickle_file)
                    saved_videos.append(script)
                save_names.append(f'{settings.temp_path}/{file}')
            except FileNotFoundError:
                pass
                #print("No vid.data file in %s" % file)
        renderingScreen.script_queue_update.emit()

        for i, video in enumerate(saved_videos):
            print(f'Rendering script {i + 1}/{len(saved_videos)}')

            t0 = datetime.datetime.now()
            renderVideo(video, renderingScreen)
            t1 = datetime.datetime.now()

            total = t1-t0
            print("Rendering Time %s" % total)

            if settings.backupVideos:
                backupName = save_names[i].replace(settings.temp_path, settings.backup_path)
                if os.path.exists(backupName):
                    print("Backup for video %s already exists" % backupName)
                else:
                    print("Making backup of video to %s" % backupName)
                    copy_tree(save_names[i], backupName)


            print(f"Deleting video folder {save_names[i]}")
            shutil.rmtree(save_names[i])
            renderingScreen.update_backups.emit()
                # delete all the temp videos
            try:
                deleteAllFilesInPath(settings.vid_finishedvids)
            except Exception as e:
                print(e)
                print("Couldn't delete clips")



#Adding Streamer's name to the video clip
def renderVideo(video, rendering_screen):
    global render_current_progress, render_max_progress, render_message
    t0 = datetime.datetime.now()

    clips = video.clips
    videoName = video.name

    subprocess._cleanup = lambda: None
    credits = []
    streamers_in_cred = []

    render_current_progress = 0
    # see where render_current_progress += 1

    amount = 0
    for clip in clips:
        if clip.isUsed:
            amount += 1

    render_max_progress = amount * 2 + 1 + 1
    render_message = "Beginning Rendering"
    rendering_screen.render_progress.emit()

    current_date = datetime.datetime.today().strftime("%m-%d-%Y__%H-%M-%S")

    toCombine = []


    fpsList = []

    for i, clip in enumerate(clips):
        mp4 = clip.mp4
        mp4name = mp4
        mp4path = f"{mp4}.mp4"

        if len(mp4.split("/")) > 2:
            name = len(mp4.split("/"))
            mp4name = mp4.split("/")[name-1].replace(".mp4", "")
            mp4path = mp4[1:]
        cap=cv2.VideoCapture(mp4path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        fpsList.append(fps)

    chosenFps = settings.fps
    if settings.useMinimumFps:
        chosenFps = int(min(fpsList))

    if settings.useMaximumFps:
        chosenFps = int(max(fpsList))

    print("Using Fps %s" % chosenFps)

    # render progress 1
    for i, clip in enumerate(clips):
        if clip.isUsed:
            name = clip.author_name
            mp4 = clip.mp4

            if name is not None and name not in streamers_in_cred and not clip.isUpload:
                credits.append(f"{clip.author_name}")
                streamers_in_cred.append(clip.author_name)


            final_duration = round(clip.vid_duration, 1)


            print(f"Rendering video ({i + 1}/{len(clips)}) to \"{settings.vid_finishedvids}\"/{mp4}_finished.mp4")


            mp4name = mp4
            mp4path = f"{mp4}.mp4"

            if len(mp4.split("/")) > 2:
                name = len(mp4.split("/"))
                mp4name = mp4.split("/")[name-1].replace(".mp4", "")
                mp4path = mp4[1:]

            if not clip.isInterval and not clip.isIntro:
                os.system(f"ffmpeg -i \"{mp4path}\" -vf \"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1\" \"{settings.vid_finishedvids}/{mp4name}temp.mp4\"")
                os.system(f"ffmpeg -i \"{settings.vid_finishedvids}/{mp4name}temp.mp4\" -filter:v fps=fps={chosenFps} \"{settings.vid_finishedvids}/{mp4name}_finished.mp4\"")
                path = f"'{os.path.dirname(os.path.realpath(__file__))}/{settings.vid_finishedvids}/{mp4name}_finished.mp4'"
                path = path.replace("\\", "/")

                #path = f"'{mp4path}'"
                #path = path.replace("\\", "/")


                toCombine.append(path)
                #os.system(f"ffmpeg -y -fflags genpts -i \"{mp4path}\" -vf \"ass=subtitleFile.ass, scale=1920:1080\" \"{settings.vid_finishedvids}/{mp4name}_finished.mp4\"")

            render_current_progress += 1
            render_message = f"Done Adding text to video ({i + 1}/{len(clips)})"
            rendering_screen.render_progress.emit()


            render_message = f"Adding clip to list ({i + 1}/{len(clips)})"
            rendering_screen.render_progress.emit()


            render_current_progress += 1
            render_message = f"Done Adding clip to list ({i + 1}/{len(clips)})"
            rendering_screen.render_progress.emit()



    # render progress 2
    render_message = "Creating audio loop"
    rendering_screen.render_progress.emit()
    #audio = AudioFileClip(f'{settings.asset_file_path}/Music/{musicFiles[0]}.mp3').fx(afx.volumex, float(video.background_volume))




    render_current_progress += 1
    render_message = "Done Creating audio loop"
    rendering_screen.render_progress.emit()
    # render progress 3
    render_message = "Writing final video"
    rendering_screen.render_progress.emit()


    sleep(5)

    vid_concat = open("concat.txt", "a")
    #Adding comment thread video clips and interval video file paths to text file for concatenating
    for files in toCombine:
        vid_concat.write(f"file {files}\n")
    vid_concat.close()




    os.system(f"ffmpeg -safe 0 -f concat -segment_time_metadata 1 -i concat.txt -vf select=concatdec_select -af aselect=concatdec_select,aresample=async=1 \"{settings.final_video_path}/{videoName}_{current_date}.mp4\"")
    #os.system(f"ffmpeg -f concat -safe 0 -i concat.txt -s 1920x1080 -c copy {settings.final_video_path}/TikTokMoments_{current_date}.mp4")

    open("concat.txt", 'w').close()


    #final_vid_with_music.write_videofile(f'{settings.final_video_path}/TikTokMoments_{current_date}.mp4', fps=settings.fps, threads=16)
    render_current_progress += 1
    t1 = datetime.datetime.now()
    total = t1-t0
    render_message = "Done writing final video (%s)" % total
    rendering_screen.render_progress.emit()

    f= open(f"{settings.final_video_path}/{videoName}_{current_date}.txt","w+")
    f.write("A special thanks to the following: \n\n")
    for cred in credits:
        f.write(cred + "\n")
    f.close()
    sleep(10)

