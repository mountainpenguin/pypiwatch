#!/usr/bin/env python

from __future__ import print_function
import hmac
import hashlib
import time
import re
import datetime
import time
import os
import magic
import random
import string

SECRET1 = "dzb9^oCl&ObUK3xx.nkDf]n+3k=)R*cl:8!Nd0O.".encode("utf8")
SECRET2 = "eo`ctiEZZ7A?2J^:v@7/>S%wvr<qbd<[U&!+ii".encode("utf8")
SECRET3 = "N2=1yv3X29M/@wxp5j;djU5up1,a@YH%5d4BzHmm".encode("utf8")

def hashpassword(user_id, password):
    combined = str(user_id) + password
    combined = combined.encode("utf8")
    round1 = hmac.new(SECRET1, combined, hashlib.sha512).digest()
    round2 = hmac.new(SECRET2, round1, hashlib.sha512).digest()
    round3 = hmac.new(SECRET3, round2, hashlib.sha512).hexdigest()
    return round3

def hashcookie(session, ip_addr, user_agent):
    combined = session + ip_addr + user_agent
    combined = combined.encode("utf8")
    round1 = hmac.new(SECRET1, combined, hashlib.sha512).digest()
    round2 = hmac.new(SECRET2, round1, hashlib.sha512).digest()
    round3 = hmac.new(SECRET3, round2, hashlib.sha512).hexdigest()
    return round3

def hashauth(user_id, email_addr):
    combined = str(user_id) + email_addr + str(int(time.time() / 3600))
    combined = combined.encode("utf8")
    round1 = hmac.new(SECRET1, combined, hashlib.sha256).digest()
    round2 = hmac.new(SECRET2, round1, hashlib.sha256).digest()
    round3 = hmac.new(SECRET3, round2, hashlib.sha256).hexdigest()
    return round3

class Media(object):
    def __init__(self, media_type, **data):
        self.type = media_type
        self.__dict__.update(data)
        self.isTv, self.isFilm, self.isEbook, self.isUnknown = False, False, False, False
        if self.type == "tv":
            self.isTv = True
        elif self.type == "film":
            self.isFilm = True
        elif self.type == "ebook":
            self.isEbook = True
        else:
            self.isUnknown = True

    def __repr__(self):
        return repr(self.__dict__)

def parseFilePath(filepath):
    # TV scene type 1
    # The.Walking.Dead.S03E14.720p.HDTV.x264-IMMERSE
    tv = re.match(r"(?P<title>.*?)\.S(?P<season>\d+)E(?P<episode>\d+)\.(?P<junk>.*?)\.?(?P<hd>\d+p)?\.?(?P<source>[HP]DTV)\.(?P<encoding>.*?)-(?P<group>.*$)", filepath, re.I)
    if tv:
        return Media("tv", **tv.groupdict())
    
    # Generic eBook
    # The.Globe.And.Mail.Prairie.Edition.03.04.2013.RETAiL.eBook-eMAG
    # Wiley.Fundamentals.Of.Wireless.Sensor.Networks.Theory.and.Practice.2010.RETAiL.eBook-DeBTB00k
    # Apress.-.Windows.8.MVVM.Patterns.Revealed.2012.RETAiL.ePUB.eBOOk-NEWSPAPER
    ebook = re.match(r"(?P<title>.*?)\.(?P<day>\d{2})?\.?(?P<month>\d{2})?\.?(?P<year>\d{4})\.(?P<source>.*?)\.eBook-(?P<group>.*$)", filepath, re.I)
    if ebook:
        return Media("ebook", **ebook.groupdict())

    # Generic film 
    # Title.Of.The.Movie.YEAR.Source.Codec-GROUP
    # Argo.2012.576p.BDRip.x264-HANDJOB.mkv
    # Jiro.Dreams.Of.Sushi.2011.DVDRip.XViD-MULTiPLY
    # Drive.Angry.720p.BluRay.x264-TWiZTED
    # The.Rum.Diary.2011.720p.BluRay.x264-SPARKS
    film = re.match(r"(?P<title>.*?)\.(?P<year>\d+)\.(?P<hd>\d+p)?\.?(?P<source>.*?)\.(?P<encoding>.*?)-(?P<group>.*$)", filepath, re.I)
    if film:
        return Media("film", **film.groupdict())

    return Media("unknown", path=filepath)

def testparse():
    passed = 0
    failed = 0
    tv = [
        ("The.Walking.Dead.S03E14.720p.HDTV.x264-IMMERSE", True),
        ("The.Walking.Dead.S03E15.HDTV.x264-IMMERSE", True),
        ("The.Walking.Dead.S03E16.PDTV.x264-IMMERSE", True),
        ("De.Rijdende.Rechter.S24E09.DUTCH.PDTV.x264-iFH", True),
        ("Argo.2012.576p.BDRip.x264-HANDJOB.mkv", False),
    ]
    for i,j in tv:
        r = parseFilePath(i)
        print("{0}".format(i), end=" ")
        if r and j and r.isTv:
            print("passed [valid match]")
            passed += 1
        elif r and not j and r.isTv:
            print("failed [invalid match]")
            failed += 1
        elif r and not j and not r.isTv:
            print("passed [valid non-match]")
            passed += 1
        elif not r and j:
            print("failed [invalid non-match")
            failed += 1
        elif not r and not j:
            print("passed [valid non-match]")
            passed += 1

    film = [
        ("Argo.2012.576p.BDRip.x264-HANDJOB.mkv", True),
        ("Jiro.Dreams.Of.Sushi.2011.DVDRip.XViD-MULTiPLY", True),
        ("Drive.Angry.720p.BluRay.x264-TWiZTED", True),
        ("The.Rum.Diary.2011.720p.BluRay.x264-SPARKS", True),
        ("Indie.Game.The.Movie.720p.x264-N0NSC3N3", True),
        ("Silver.Linings.Playbook.2012.DVDSCR.XviD.AC3-VAiN", True),
        ("The.Walking.Dead.S03E16.PDTV.x264-IMMERSE", False),
    ]
    for i,j in film:
        r = parseFilePath(i)
        print("{0}".format(i), end=" ")
        if r and j and r.isFilm:
            print("passed [valid match]")
            passed += 1
        elif r and not j and r.isFilm:
            print("failed [invalid match]")
            failed += 1
        elif r and not j and not r.isFilm:
            print("passed [valid non-match]")
            passed += 1
        elif not r and j:
            print("failed [invalid non-match")
            failed += 1
        elif not r and not j:
            print("passed [valid non-match]")
            passed += 1    
            
    ebook = [
        ("The.Globe.And.Mail.Prairie.Edition.03.04.2013.RETAiL.eBook-eMAG", True),
        ("Wiley.Fundamentals.Of.Wireless.Sensor.Networks.Theory.and.Practice.2010.RETAiL.eBook-DeBTB00k", True),
        ("Apress.-.Windows.8.MVVM.Patterns.Revealed.2012.RETAiL.ePUB.eBOOk-NEWSPAPER", True),
        ("The.Walking.Dead.S03E16.PDTV.x264-IMMERSE", False),
    ]
    for i,j in ebook:
        r = parseFilePath(i)
        print("{0}".format(i), end=" ")
        if r and j and r.isEbook:
            print("passed [valid match]")
            passed += 1
        elif r and not j and r.isEbook:
            print("failed [invalid match]")
            failed += 1
        elif r and not j and not r.isEbook:
            print("passed [valid non-match]")
            passed += 1
        elif not r and j:
            print("failed [invalid non-match")
            failed += 1
        elif not r and not j:
            print("passed [valid non-match]")
            passed += 1        
            
    nonscene = [
        ("20120727_Olympics 2012 Opening Ceremony.SD.thebox.hannibal", False),
        ("Esselmont, Ian - Return of the Crimson Guard", False),
        ("Various Artists-Django Unchained (2012) [FLAC]", False),
    ]
    for i,j in nonscene:
        r = parseFilePath(i)
        print("{0}".format(i), end=" ")
        if r:
            print("failed [invalid match]")
            failed += 1
        elif not r:
            print("passed [valid non-match]")
            passed += 1

    print("{0} passed, {1} failed".format(passed, failed))

def _plural(val):
    if val == 1:
        return ""
    else:
        return "s"

def secondstohumanstamp(seconds):
    hours = int(seconds / (60*60))
    seconds -= hours*60*60
    minutes = int(seconds / 60)
    seconds -= minutes*60
    seconds = int(seconds)
    return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)

def _secondstohuman(seconds):
    human = ""
    if seconds > 60*60:
        hours = int(seconds / (60*60))
        seconds -= hours*(60*60)
        human = "{0} hour{1}".format(hours, _plural(hours))
    if seconds > 60:
        minutes = int(seconds / 60)
        seconds -= minutes*60
        if human:
            human += ", {0} minute{1}".format(minutes, _plural(minutes))
        else:
            human = "{0} minute{1}".format(minutes, _plural(minutes))
    if human:
        human += ", {0} second{1}".format(seconds, _plural(seconds))
    else:
        human = "{0} second{1}".format(seconds, _plural(seconds))
    return human

def timestamptohuman(timestamp):
    timestamp = "2013-04-03 16:51:25"
    ts = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    timenow = datetime.datetime.utcnow()
    timediff = timenow - ts
    human = ""
    if timediff.days > 0:
        human = "{0} day{1}, ".format(timediff.days, _plural(timediff.days)) 
    if timediff.seconds > 0:
        human += _secondstohuman(timediff.seconds)
    human += " ago"
    return human

def bytestohuman(byte):
    if byte > 1024**3:
        return "{0:.2f} GiB".format(byte / (1024**3))
    elif byte > 1024**2:
        return "{:.2f} MiB".format(byte / (1024**2))
    elif byte > 1024:
        return "{:.2f} KiB".format(byte / 1024)
    else:
        return "{0} B".format(byte)

def getSize(path):
    if os.path.isdir(path):
        total_size = 0
        for item in os.listdir(path):
            itempath = os.path.join(path, item)
            if os.path.isfile(itempath):
                total_size += os.path.getsize(itempath)
            elif os.path.isdir(itempath):
                total_size += getSize(itempath)
    else:
        total_size = os.path.getsize(path)
    return total_size

def identifyFiles(path):
    data = {}
    if os.path.isfile(path):
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            filetype = m.id_filename(path) 
        extension = path.split(".")[-1]
        if len(extension) > 4:
            extension = "unknown"
        return {os.path.basename(path): (filetype, extension)}
    elif os.path.isdir(path):
        for item in os.listdir(path):
            itempath = os.path.join(path, item)
            if os.path.basename(path) in data:
                data[os.path.basename(path)].update(identifyFiles(itempath))
            else:
                data[os.path.basename(path)] = identifyFiles(itempath)
    return data

def filetree(files, toplevel=False):
    file_templ = """
        <li class="item-page-tree item-page-file file-mime-{mimeclass} file-ext-{ext}"
            data-mime-type="{mime}"
            data-ext="{ext}">
            <span>{filename}</span>
        </li>
    """
    dir_templ = """
        <li class="item-page-tree item-page-directory item-page-directory-collapsed">
            <a href="#" class="item-page-directory-link">{dirname}/</a>
            {dirhtml}
        </li>
    """
    if toplevel:
        html = "<ul class='item-page-tree'>"
    else:
        html = "<ul class='item-page-tree' style='display: none;'>"
    keys = list(files.keys())
    keys.sort()
    for k in keys:
        v = files[k]
        if type(v) is tuple:
            html += file_templ.format(
                mimeclass = v[0].replace("/","-").replace("+","-"), 
                ext = v[1], 
                mime = v[0], 
                filename = k
            )
        elif type(v) is dict:
            html += dir_templ.format(
                dirname = k, 
                dirhtml = filetree(v)
            )
    html += "</ul>"
    return html

def identifyPlayable(files, key=""):
    playable = []
    for k,v in files.items():
        if type(v) is tuple:
            if v[0] == "video/mp4":
                playable += [(k, key)]
            elif v[0] == "video/x-matroska":
                playable += [(k, key)]
        elif type(v) is dict:
            s = identifyPlayable(v, key=k)
            if s:
                for x in s:
                    playable += [(x, key)]
    # recompile paths
    paths = []
    for x in playable:
        path = os.path.join(key, x[0])
        paths += [path]
    return paths

def baseLevel(files, key=""):
    base = []
    for k,v in files.items():
        if type(v) is tuple:
            base += [(k, key)]
        elif type(v) is dict:
            f = baseLevel(v, key=k)
            for x in f:
                base += [(x, key)]
    paths = []
    for x in base:
        path = os.path.join(key, x[0])
        paths += [path]
    return paths

def randomstring(length=10):
    return "".join([random.choice(string.ascii_letters + string.digits) for x in range(length)])

def itemsAlphabetical(items):
    items = sorted(items, key=lambda x: x.title.upper())
    items_alpha = []
    for i in items:
        firstchar = i.title[0].upper()
        if len(items_alpha) == 0:
            items_alpha += [[firstchar, [i]]]
        else:
            if items_alpha[-1][0] == firstchar:
                items_alpha[-1][1] += [i]
            else:
                items_alpha += [[firstchar, [i]]]
    return items_alpha

