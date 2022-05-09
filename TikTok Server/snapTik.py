# Reverse engineered by RoseChilds - 2022

import re
import requests
import json


def _0xe72c(d, e, f):
    # This code *seems* to help deobfuscate the script response given by SnapTik. Clearly whoever made it didn't want to
    # have people using their service without seeing the ads.
    # Ported from JS by me
    reduceindex = 0
    letters = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/")
    h = letters[0:e]
    i = letters[0:f]

    j = 0
    for b in list(d)[::-1]:
        c = reduceindex
        reduceindex += 1
        try:
            bposition = h.index(b)
        except ValueError:
            continue
        j += bposition * (e ** c)
    k = ""
    while j > 0:
        k = i[j % f] + k
        j = round((j - (j % f)) / f)
    if k is None:
        return "0"
    return k


def deobfuscate(h, u, n, t, e, r):
    # Cute that the arguments here spell "hunter". Maybe SnapTik is trying to send me a message...
    # Although `u` and `r` are redundant, so I guess they were trying too hard to be cute
    r = ""
    length = len(h)
    i = 0
    while i < length:
        s = ""
        while h[i] != n[e]:
            s += h[i]
            i += 1
        for j in range(len(n)):
            s = s.replace(n[j], str(j))
        i += 1
        output = int(_0xe72c(s, e, 10))
        r += chr(int(output) - t)
    # `r` is now the deobfuscated JS code, however we don't need it so I'm just going to extract the download URL
    try:
        url = re.search(r"https://tikcdn\.net/file/\S+.mp4", r).group(0)
    except AttributeError:
        raise Exception("Could not find download URL")
    return url


def downloadFromID(tiktokid, path):
    # Get the obfuscated response from SnapTik and find the arguments used in the deobfuscation function
    obfuscated = requests.get(
        f"https://snaptik.app/abc.php?url=https%3A%2F%2Fwww.tiktok.com%2F%40owo%2Fvideo%2F{tiktokid}&lang=en&token=eyMTY1MTcwMjQzNA==c").text
    arguments = re.search(r"\"\S+\",\d+,\"\S+\",\d+,\d+,\d+", obfuscated).group(0).split(",")
    args = list(map(json.loads, arguments))
    # Find the URL
    url = deobfuscate(*args)
    # Download and write to disk, then we're done :)
    with open(path, "wb") as f:
        f.write(requests.get(url).content)
    return path
