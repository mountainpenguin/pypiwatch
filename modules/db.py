#!/usr/bin/env python

import sqlite3
import os

from modules import utils

class Database(object):
    def __init__(self, root):
        self.root = root
        self.conn = sqlite3.connect("data/main.db")
        self.cursor = self.conn.cursor()
        self._checkItemTable()

    def _checkItemTable(self):
        try:
            c = self.cursor.execute("""
                SELECT id FROM items
                LIMIT 1
            """)
            result = c.fetchone()
        except:
            self._createItemTable()

    def _createItemTable(self):
        self.cursor.execute("""
            CREATE TABLE items
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                typeID INTEGER,
                title TEXT,
                qualityID INTEGER,
                added DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        self.indexItems()

    def insertItem(self, path, typeID, title, qualityID):
        ins = self.cursor.execute("""
            INSERT INTO items
            (path, typeID, title, qualityID)
            VALUES (?, ?, ?, ?)
        """, (path, typeID, title, qualityID))
        self.conn.commit()
        return self.getItemByID(ins.lastrowid)

    def getItemByID(self, itemID):
        query = self.cursor.execute("""
            SELECT * FROM items
            WHERE id=?
        """, (itemID,))
        result = query.fetchone()
        if result:
            return Item(raw=result, root=self.root)

    def getItems(self):
        query = self.cursor.execute("""
            SELECT * FROM items
            ORDER BY added DESC
            LIMIT 50
        """)
        return [Item(raw=x, root=self.root) for x in query.fetchall()]

    def getItemByPath(self, path):
        query = self.cursor.execute("""
            SELECT * FROM items
            WHERE path = ? 
        """, (path,))
        result = query.fetchone()
        if result:
            return Item(raw=result, root=self.root)

    def indexItems(self):
        files = os.listdir(self.root) 
        for fn in files:
            path = os.path.join(self.root, fn)
            check = self.getItemByPath(path)
            if check:
                continue

            result = utils.parseFilePath(fn)
            if result.isTv:
                if result.hd and result.hd == "720p":
                    qualityID = 2
                elif result.hd and result.hd == "1080p":
                    qualityID = 3
                else:
                    qualityID = 1
                self.insertItem(path, 1, result.title.replace(".", " "), qualityID) 
            elif result.isFilm:
                if result.hd and result.hd == "720p":
                    qualityID = 2
                elif result.hd and result.hd == "1080p":
                    qualityID = 3
                else:
                    qualityID = 1
                self.insertItem(path, 2, result.title.replace(".", " "), qualityID)
            elif result.isEbook:
                self.insertItem(path, 3, result.title.replace(".", " "), 1)
            else:
                self.insertItem(path, 0, fn, 0)
        
def convertTypeID(typeID):
    types = {
        1: "tv",            #icon-facetime-video
        2: "film",          #icon-film
        3: "ebook",         #icon-book
        4: "application",   #icon-hdd
        5: "music",         #icon-music
        0: "unknown",       #icon-question-sign
    }
    if int(typeID) in types:
        return types[int(typeID)]
    else:
        return "unknown"

def convertQualityID(qualityID):
    qualities = {
        1: "standard definition",
        2: "high definition (720p)",
        3: "ultra-high definition (1080p)",
        4: "DVD",
        5: "BluRay",
        6: "N/A",
        0: "unknown",
    }
    if int(qualityID) in qualities:
        return qualities[int(qualityID)]
    else:
        return "unknown"

class Item(object):
    def __init__(self, ID=None, path=None, typeID=None, title=None, qualityID=None, added=None, raw=None, root=None):
        if raw:
            self.ID          = raw[0]
            path             = raw[1]
            self.typeID      = raw[2]
            self.type_str    = convertTypeID(self.typeID)
            self.title       = raw[3]
            self.qualityID   = raw[4]
            self.quality_str = convertQualityID(self.qualityID)
            self.added       = raw[5]
        else:
            self.ID          = ID
            path             = path
            self.typeID      = typeID
            self.type_str    = convertTypeID(self.typeID)
            self.title       = title
            self.qualityID   = qualityID
            self.quality_str = convertQualityID(self.qualityID)
            self.added       = added
        self.size = utils.getSize(path) 

        self.path = path.replace(root, "")

        self.files = utils.identifyFiles(path)
        self.playable = utils.identifyPlayable(self.files)
        self.filetree = utils.filetree(self.files, toplevel=True)
        self.mediainfo = utils.parseFilePath(self.path)
    def __repr__(self):
        return "<Item - ID: {ID}, title: {title}, type: {type_str}, quality: {quality_str}".format(**self.__dict__)
