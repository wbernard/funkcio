# main.py
#
# Copyright 2021 walter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/python3

# Python Imports
import cairo
import math
import os, threading, time, datetime
import numpy as np

# Gtk Imports

import sys
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk, Gio
from gi.repository import GLib


from .window import Main_Window

def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper

class MouseButton:

    LEFT_BUTTON   = 1
    MIDDLE_BUTTON = 2
    RIGHT_BUTTON  = 3


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='im.bernard.funkcitrovilo',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)


        #,self.drawArea       = Gtk.DrawingArea()
        #self.messageWidget  = Gtk.Popover()
        #self.messageLabel   = Gtk.Label()

        #self.drawArea.add_events (Gdk.EventMask.BUTTON_PRESS_MASK)
        #self.drawArea.connect("button-press-event", self.onButtonPress)

        #self._init_drawArea()
        '''
        self.surface       = None
        self.curWidth      = 0
        self.curHeight     = 0
        self.brushColorVal = [1.0, 0.0, 0.0, 1.0]
        self.brushSizeVal  = 4
        self.abCoords      = [ [0.0, 0.0], [0.0, 0.0] ]
        self.punkte        = []

        self.success    = "#88cc27"
        self.warning    = "#ffa800"
        self.error      = "#ff0000"


    def onConfigure(self, area, eve, data = None):
        aw = area.get_allocated_width()
        ah = area.get_allocated_height()

        _surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, aw, ah)

        # if surface and area updated create new surface
        if self.surface is not None:
            global sw, sh
            sw = self.surface.get_width()
            sh = self.surface.get_height()

            # if we have shrunk keep old surface
            if aw < sw or ah < sh:
                return False

            brush = cairo.Context(_surface)

            # Load former surface to new surface
            brush.set_source_surface(self.surface, 0.0, 0.0)
            brush.scale(aw, ah)
            brush.paint()

            self.curWidth      = aw
            self.curHeight     = ah
        else:
            self.drawArea.set_size_request(self.curWidth, self.curHeight)


        self.surface = _surface
        self.brush   = cairo.Context(self.surface)
        return False


    def onDraw(self, area, brush):   # area ist das Zeichenfeld  brush ist ein context
        if self.surface is not None:
            brush.set_source_surface(self.surface, 0.0, 0.0)
            brush.paint()

            self.linio(0, sh/2, sw, sh/2)   # zeichnet das Achsenkreuz
            self.linio(sw/2, 0, sw/2, sh)

        else:
            print ("No surface info...")

        return False

    def onMotion(self, area, eve):
        self.abCoords[1] = [eve.x, eve.y]
        p1 = self.abCoords[0]
        p2 = self.abCoords[1]

        sw = self.surface.get_width()    # liest die Abmessungen des Fensters ein
        sh = self.surface.get_height()

        print (sw, sh)

        x1 = p1[0]
        y1 = p1[1]
        x2 = p2[0]
        y2 = p2[1]
        w  = x2 - x1
        h  = y2 - y1
        r  = math.sqrt(w**2 + h**2)

        self.zeichnePunkt([x1,y1])
        self.drawArea.queue_draw()



    def onButtonPress(self, event, widget):
            if event.type == Gdk.EventType.BUTTON_PRESS and event.button == MouseButton.LEFT_BUTTON:
                self.abCoords[0] = [event.x, event.y]
            print (abCoords[0])

    def zeichnePunkt(self,x1y1):
        rgba = self.brushColorVal
        self.brush.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        self.brush.set_line_width(self.brushSizeVal)
        self.brush.set_line_cap(1) # Linienende 0 = BUTT, 1 = rund  2 = eckig

        self.brush.arc(x1y1[0], x1y1[1], 3, 0, 2*math.pi)
        self.brush.fill()

        self.brush.set_source_rgba(0, 0, 0, 1)
        self.brush.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_NORMAL)
        self.brush.move_to(x1y1[0]+5, x1y1[1])
        self.brush.set_font_size(12)
        x = int(x1y1[0]-sw/2)
        y = int(-(x1y1[1]-sh/2))
        self.brush.show_text(str(x) + ", " + str(y))
        self.punkte.append([x, y])
        print (x, y)
        print (len(self.punkte))
        if len(self.punkte) == 5:
            self.displayMessage(self.success, "Keine weitern Punkte anklicken, Funktion wählen!")
    '''
    def do_activate(self):
        win = self.props.active_window
        #win.add(self.drawArea)
        if not win:
            win = Main_Window(application=self)
        win.present()
    '''
    def linio(self, x1, y1, x2, y2):
        self.brush.move_to(x1, y1)
        self.brush.line_to(x2, y2)

        self.brush.set_source_rgb(0, 0, 0)
        self.brush.set_line_width(1.5)
        self.brush.stroke()

    def displayMessage(self, type, text):
        markup = "<span foreground='" + type + "'>" + text + "</span>"
        self.messageLabel.set_markup(markup)
        self.messageWidget.popup()
        self.hideMessageTimed()
    '''

    @threaded
    def hideMessageTimed(self):
        time.sleep(1)
        GLib.idle_add(self.messageWidget.popdown)


def main(version):
    app = Application()
    return app.run(sys.argv)


