#!/usr/bin/env python

import logging
import signal
import os
import hashlib
import random
import string
import subprocess
import shlex
import re
import time
import io
import tarfile
import zipfile
import threading
import mplayer

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options
import tornado.template

from modules import utils
from modules import db

class Main(object):
    def __init__(self):
        pass

    def shutdown(self, *args, **kwargs):
        if self._PID != os.getpid():
            return
        logging.info("SIGTERM received, shutting down")
        self.instance.stop()

    def main(self):
        signal.signal(signal.SIGTERM, self.shutdown)

        tornado.options.parse_command_line(["--logging=debug"])
        settings = {
            "debug": False, 
            "cookie_secret": "w98[0>DF%o'a5!JsOR@zqF{)8yqhP8A@_AA-.Eh)", 
            "static_path": os.path.join(os.getcwd(), "static"),
        }
        application = tornado.web.Application([
            (r"/css/(.*)", tornado.web.StaticFileHandler, {"path" : os.path.join(os.getcwd(), "static/css/")}),
            (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.getcwd(), "static/js/")}),
            (r"/img/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.getcwd(), "static/img/")}),
            (r"/", webroot),
            (r"/ajax", ajax),
        ], **settings)
        self._PID = os.getpid()
        #application._root = os.path.expanduser("~/torrents/downloading")
        application._root = os.path.expanduser("~/Unwatched")
        application._templ = tornado.template.Loader("templates")
        application._DB = db.Database(root=application._root)
        application.current = None
        application.status = None
        while True:
            dirname = os.path.join("/tmp", "pyPi" + utils.randomstring()) 
            try:
                os.mkdir(dirname)
                application._tmpdir = dirname 
                logging.info("Creating temporary directory: {0}".format(dirname))
                break
            except:
                pass

        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
        http_server.listen(11111)
        self.instance = tornado.ioloop.IOLoop.instance()
        self.instance.start()

class BaseHandler(tornado.web.RequestHandler):
    def _reldir(self, path):
        first = os.path.dirname(path)
        second = first.split("/", 1)
        if len(second) > 1:
            return second[1] + "/"
        else:
            return "/"
    def render(self, page, **kwargs):
        kwargs["page"] = page
        kwargs["reldir"] = self._reldir
        kwargs["basename"] = os.path.basename
        t = self.application._templ.load("{0}.html".format(page))
        self.write(t.generate(**kwargs))

class webroot(BaseHandler):
    def get(self):
        items = self.application._DB.getItems()
        items_alphabetical = utils.itemsAlphabetical(items)
        self.render("index", 
                    current=self.application.current, 
                    items=items_alphabetical) 

class ajax(BaseHandler):
    def initialize(self):
        self.commands = {
            "playable": self._playable,
            "play": self._play,
            "pause": self._pause,
            "stop": self._stop,
            "progress": self._progress,
            "seek": self._seek,
        }

    def get(self):
        command = self.get_argument("command", None)
        if command in self.commands:
            self.commands[command](**self.request.arguments)

    def _playable(self, **kwargs):
        itemID = kwargs["itemID"][0].decode("utf8")
        item = self.application._DB.getItemByID(itemID)
        response = {
            "playable": [(self._reldir(x), os.path.basename(x)) for x in item.playable],
        }
        self.write(response)

    def _play(self, **kwargs):
        # check for current and stop, then play this one
        itemID = kwargs["itemID"][0].decode("utf8")
        itemindex = int(kwargs["itemindex"][0])
        item = self.application._DB.getItemByID(itemID)
        pathtofile = os.path.join(self.application._root, item.playable[itemindex])

        player = mplayer.Player()
        player.loadfile(pathtofile)
        self.application.current = Current(item, player)
        self.application.current.player.loadfile(pathtofile)
        time.sleep(1)
        #self.application.current.player.fullscreen = True

    def _pause(self, **kwargs):
        if self.application.current:
            self.application.current.player.pause()
            if self.application.current.status == "playing":
                self.application.current.status = "paused"
            else:
                self.application.current.status = "playing"
            self.write({"status": self.application.current.status})

    def _stop(self, **kwargs):
        if self.application.current:
            self.application.current.player.quit()
            self.application.current = None

    def _progress(self, **kwargs):
        if self.application.current:
            self.write({"progress": self.application.current.get_timepos(), "percentage": self.application.current.get_perc()})
        else:
            self.write({"progress": None})

    def _seek(self, **kwargs):
        if self.application.current:
            self.application.current.player.time_pos = self.application.current.player.length - 3

class Current(object):
    def __init__(self, item, player):
        self.item = item
        self.player = player
        self.status = "playing"
        self.length = utils.secondstohumanstamp(player.length)

    def get_timepos(self):
        if self.player.time_pos:
            return utils.secondstohumanstamp(self.player.time_pos)
        else:
            return self.length

    def get_perc(self):
        if self.player.time_pos:
            return int(100*self.player.time_pos / self.player.length)
        else:
            return 100
