
import string
import requests
import urllib.request
import database
import scriptwrapper
from TikTokApi import TikTokApi
import shutil
import traceback, sys
import subprocess
import settings
from time import sleep
from pymediainfo import MediaInfo


forceStop = False

#GreyFieldMedia


def getAllClips(filter, amount, window):
    global all_clips_found, forceStop
    # format the saved_ids by taking it out of tuple form

    bad_ids = []

    for id in database.getAllSavedClipIDs():
        bad_ids.append(id[0])

    clips = []

    filterName = filter[0]
    filterObject = filter[1]

    print(f"Looking for all clips for filter {filterName}")


    oldIds = []

    def attemptAddScripts(results, typeofrequest):
        newIds = []
        amountJustAdded = 0
        for i, tiktok in enumerate(results):
            #print("downloading %s/%s" % (i+1, len(result)))
            # Prints the text of the tiktok

            videoURL = None
            author = None
            vidId = None
            createTime = None
            text = None
            diggCount = None
            shareCount = None
            playCount = None
            commentCount = None
            duration = None
            hashtags = None

            if typeofrequest == "Hashtag":
                videoURL = tiktok["itemInfos"]["video"]["urls"][0]
                author = tiktok["musicInfos"]["authorName"]
                vidId = tiktok["itemInfos"]["id"]
                createTime = tiktok["itemInfos"]["createTime"]
                text = tiktok["itemInfos"]["text"]
                diggCount = tiktok["itemInfos"]["diggCount"]
                shareCount = tiktok["itemInfos"]["shareCount"]
                playCount = tiktok["itemInfos"]["playCount"]
                commentCount = tiktok["itemInfos"]["commentCount"]
                duration = tiktok["itemInfos"]["video"]["videoMeta"]["duration"]
                hashtags = []
                for hashtag in tiktok["textExtra"]:
                    tag = hashtag["HashtagName"]
                    if not tag == "":
                        hashtags.append(hashtag["HashtagName"])
            elif typeofrequest == "Author" or typeofrequest == "Trending":
                try:
                    videoURL = tiktok["video"]["downloadAddr"]
                    author = tiktok["music"]["authorName"]
                    vidId = tiktok["id"]
                    createTime = tiktok["createTime"]
                    text = tiktok["desc"]
                    diggCount = tiktok["stats"]["diggCount"]
                    shareCount = tiktok["stats"]["shareCount"]
                    playCount = tiktok["stats"]["playCount"]
                    commentCount = tiktok["stats"]["commentCount"]
                    duration = tiktok["video"]["duration"]
                    try:
                        hashtags = []
                        for hashtag in tiktok["textExtra"]:
                            tag = hashtag["hashtagName"]
                            if not tag == "":
                                hashtags.append(hashtag["hashtagName"])
                    except Exception as e:
                        print("no hashtags")
                except Exception as e:
                    print("error parsing data")
                    continue

            newIds.append(vidId)

            if vidId in bad_ids:
                continue

            if vidId in [newclip.id for newclip in clips]:
                continue

            if filterObject.likeCount is not None:
                if diggCount < filterObject.likeCount:
                    bad_ids.append(vidId)
                    continue

            if filterObject.shareCount is not None:
                if shareCount < filterObject.shareCount:
                    bad_ids.append(vidId)
                    continue

            if filterObject.playCount is not None:
                if playCount < filterObject.playCount:
                    bad_ids.append(vidId)
                    continue

            if filterObject.commentCount is not None:
                if commentCount < filterObject.commentCount:
                    bad_ids.append(vidId)
                    continue

            tiktok_clip = scriptwrapper.ClipWrapper(vidId, videoURL, author, createTime, text, diggCount, shareCount, playCount, commentCount, duration)
            clips.append(tiktok_clip)
            amountJustAdded += 1

        return newIds

    searchAmount = amount

    while True:
        try:
            api = TikTokApi()

            # The Number of trending TikToks you want to be displayed

            new_ids = []

            if filterObject.searchType == "Hashtag":
                hashtags = filterObject.inputText
                evenSplitHashtag = int(searchAmount / len(hashtags))
                for hashtag in hashtags:
                    print("Looking for %s clips for hashtag %s" % (evenSplitHashtag, hashtag))
                    results = api.byHashtag(hashtag, evenSplitHashtag)

                    new_ids.append(attemptAddScripts(results, "Hashtag"))

            elif filterObject.searchType == "Author":
                authors = filterObject.inputText
                evenSplitAuthors = int(searchAmount / len(authors))


                for author in authors:
                    print("Looking for %s clips for author %s" % (evenSplitAuthors, author))
                    results = api.byUsername(author, evenSplitAuthors)


                    new_ids.append(attemptAddScripts(results, "Author"))
            elif filterObject.searchType == "Trending":
                print("Looking for %s trending clips" % searchAmount)

                results = api.trending(count=searchAmount)


                new_ids.append(attemptAddScripts(results, "Trending"))

            if new_ids == oldIds:
                print("Found exactly the same ids in two consecutive searches. Terminating search process")
                break

            oldIds = new_ids


            print(f"{len(clips)} unique {filterName} clips found")


            if len(clips) >= amount:
                break
            else:
                searchAmount *= 2


            if forceStop:
                print("Forced Stop Finding Process")
                forceStop = False
                break
        except Exception as e:
            traceback.print_exc(file=sys.stdout)

            print(e)
            print("exception occured downloading. waiting and retrying")
            sleep(5)

    print(f"Found {len(clips)} unique clips")
    window.update_log_found_total_clips.emit(filterName, len(clips))

    for clip in clips:
        database.addFoundClip(clip, filterName)

    return clips



def autoDownloadClips(filterName, clips, window):
    global forceStop
    #Downloading the clips with custom naming scheme
    window.update_log_start_downloading_game.emit(filterName, len(clips))
    print('Downloading...')
    for i, clip in enumerate(clips):
        print("Downloading Clip %s/%s" % (i + 1, len(clips)))
        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'okhttp'), ('referer', 'https://www.tiktok.com/')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(clip.url, f"{settings.vid_filepath}/{clip.author_name}-{clip.id}.mp4")
            clip.mp4 = f"{clip.author_name}-{clip.id}"

            media_info = MediaInfo.parse(f"{settings.vid_filepath}/{clip.author_name}-{clip.id}.mp4")
            duration = media_info.tracks[0].duration
            clip.vid_duration = float(duration) / 1000
            database.updateStatusWithClip(clip.id, "DOWNLOADED", clip)
        except Exception as e:
            print(e)
            print("Error downloading clip")
            database.updateStatusWithClip(clip.id, "BAD", clip)

        window.update_log_downloaded_clip.emit(i + 1)
        if forceStop:
            print("Forced Stop Downloading Process")
            forceStop = False
            break
    window.update_done_downloading_game.emit(filterName, len(clips))




