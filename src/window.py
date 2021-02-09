# window.py
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
from sklearn.linear_model import LinearRegression

# Gtk Imports

import sys
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk, Gio
from gi.repository import GLib


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper

@Gtk.Template(resource_path='/im/bernard/funkcitrovilo/window.ui')
class Main_Window(Gtk.Window):
    __gtype_name__ = 'Main_Window'

    drawArea      = Gtk.Template.Child()
    messageLabel  = Gtk.Template.Child()
    messageWidget = Gtk.Template.Child()
    textAusgabe   = Gtk.Template.Child()
    gerade        = Gtk.Template.Child()
    parabel       = Gtk.Template.Child()
    kurve3o       = Gtk.Template.Child()
    kurve4o       = Gtk.Template.Child()
    neustart      = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        #self.drawArea.add_events (Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawArea.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.drawArea.connect('draw', self.onDraw)
        self.drawArea.connect('configure-event', self.onConfigure)
        self.drawArea.connect("motion-notify-event", self.zeigeKoord)
        self.drawArea.connect('button-press-event', self.holePunkt)
        self.gerade.connect('clicked', self.zeichneGerade)
        self.parabel.connect('clicked', self.zeichneParabel)
        self.kurve3o.connect('clicked', self.zeichneKurve3_O)
        self.kurve4o.connect('clicked', self.zeichneKurve4_O)
        self.neustart.connect('clicked', self.novStart)

        self.zeichne       = True
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
        aw = area.get_allocated_width()   #liest die aktuellen Abmessungen des Fensters ein
        ah = area.get_allocated_height()

        _surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, aw, ah)

        # if surface and area updated create new surface
        if self.surface is not None:
            global sw, sh
            sw = self.surface.get_width()
            sh = self.surface.get_height()

            # if we have shrunk keep old surface
            if aw < sw and ah < sh:
                return False

            brush = cairo.Context(_surface)

            # Load former surface to new surface
            brush.set_source_surface(self.surface, 0.0, 0.0)
            brush.scale(aw, ah)
            brush.paint()

            self.curWidth   = aw
            self.curHeight  = ah

            self.zeichne    = True     # d.h. dass in onDraw die Zeichenfläche neu gezeichnet wird


        else:
            self.drawArea.set_size_request(self.curWidth, self.curHeight)

        self.surface = _surface
        self.brush   = cairo.Context(self.surface)
        return False

    def onDraw(self, area, brush):   # area ist das Fenster  brush ist ein context
        aw = area.get_allocated_width()   # liest die aktuellen Abmessungen des Fensters ein
        ah = area.get_allocated_height()

        if self.surface is not None:
            brush.set_source_surface(self.surface, 0.0, 0.0)
            brush.paint()

            sw = self.surface.get_width()
            sh = self.surface.get_height()

            print ("aw", aw, ah)
            print ("sw", sw, sh)
            # if we have shrunk keep old surface
            if aw < sw and ah < sh:
                return False

            print (self.zeichne)
            if self.zeichne:
                self.brush.rectangle(0, 0, sw, sh)  # x, y, width, height
                self.brush.set_operator(0);
                self.brush.fill()
                self.brush.set_operator(1)
                self.linio(0, sh/2, sw, sh/2) # zeichnet das Achsenkreuz
                self.linio(sw/2, 0, sw/2, sh)


                print ("Punkte", self.punkte[:])

                for i in self.punkte:
                    x1 = i[0] + sw/2
                    y1 = -i[1] +sh/2
                    print ("Punkt", i, x1, y1)
                    self.zeichnePunkt([x1,y1])

            self.zeichne = False

        else:
            print ("No surface info...")

        return False

    def zeigeKoord (self, area, eve):
        (x1, y1) = eve.x, eve.y
        x = int(x1-sw/2)         # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
        y = int(-y1+sh/2)
        print("(x = " + str(x) + ", y = " + str(y) + ")")

        #self.zeigeKoordinaten(self.success, "(x = " + str(x) + ", y = " + str(y) + ")")
        #self.schreibKoord([x1,y1], eve)

        #self.drawArea.queue_draw()

    def holePunkt(self, area, eve):

        x1 = eve.x
        y1 = eve.y

        x = int(x1-sw/2)         # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
        y = int(-y1+sh/2)
        print("(" + str(x) + ", " + str(y) + ")")

        self.zeichnePunkt([x1,y1])

        self.drawArea.queue_draw()

    def neuStart(self, eve):
        sw = self.surface.get_width()
        sh = self.surface.get_height()
        self.brush.rectangle(0, 0, sw, sh)  # x, y, width, height
        self.brush.set_operator(0);
        self.brush.fill()
        self.brush.set_operator(1)
        self.linio(0, sh/2, sw, sh/2)
        self.linio(sw/2, 0, sw/2, sh)

        del self.punkte[:]

    def novStart(self, widget):
        sw = self.surface.get_width()
        sh = self.surface.get_height()
        self.brush.rectangle(0, 0, sw, sh)  # x, y, width, height
        self.brush.set_operator(0);
        self.brush.fill()
        self.brush.set_operator(1)
        self.linio(0, sh/2, sw, sh/2)
        self.linio(sw/2, 0, sw/2, sh)

        self.drawArea.queue_draw()
        del self.punkte[:]

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
        x = int(x1y1[0]-sw/2)         # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
        y = int(-(x1y1[1]-sh/2))
        #self.drawArea.queue_draw()
        self.brush.show_text(str(x) + ", " + str(y))

        #self.drawArea.queue_draw()

        if self.zeichne == False:   # wenn es nicht eine Anpassung der Zeichenfläche ist
            self.punkte.append([x, y])
            #print (x, y)
            print (len(self.punkte))
            if len(self.punkte) == 5:
                self.displayMessage(self.success, "Keine weitern Punkte anklicken, Funktion wählen!")

    def zeichneGerade(self, widget):
        self.drawType = "Gerade"
        if len(self.punkte) > 5:   # self.punkte sind die eingegeben Punkte der Kurve
            self.displayMessage(self.success, "Zu viele Punkte angeklickt!")
            self.neuStart(self)
        elif len(self.punkte) < 2:
            self.displayMessage(self.success, "Zu wenig Punkte angeklickt!")
            self.neuStart(self)
        elif len(self.punkte) == 2:
            p1 = self.punkte[0]
            p2 = self.punkte[1]

            m = (p2[1]-p1[1])/(p2[0]-p1[0])
            x = -sw
            punkt = []      # hier geht es um die einzelnen Punkte der Kurve
            while x < sw:
                y = m*(x-p1[0]) + p1[1]   # Geradengleichnung y = m*x + n
                punkt.append((x+ sw/2, -y + sh/2))
                x += 1

            self.brush.move_to(*punkt[0])
            for p in punkt[1:]:
                self.brush.line_to(*p)

            self.brush.set_line_width(2)
            self.brush.set_source_rgb(0, 0, 0.5)
            self.brush.stroke()

            self.brush.move_to(sw-150, sh-30)
            a = round(m,3)
            bf = -m*p1[0]+p1[1]
            b = round(bf,0)
            self.brush.show_text("y = " + str(a) + "x + " + str(b))


            self.drawArea.queue_draw()
        else:
            pass

    def zeichneParabel(self, widget):
        self.drawType = "Parabel"
        print (len(self.punkte))
        if len(self.punkte) > 5:
            self.displayMessage(self.success, "Zu viele Punkte angeklickt!")
            self.neuStart(self)
        elif len(self.punkte) < 3:
            self.displayMessage(self.success, "Zu wenig Punkte angeklickt!")
            self.neuStart(self)
        elif len(self.punkte) == 3:
            p1 = self.punkte[0]
            p2 = self.punkte[1]
            p3 = self.punkte[2]

            mx = [[(p1[0])**2, p1[0], 1], [(p2[0])**2, p2[0], 1], [(p3[0])**2, p3[0], 1]]
            my = [p1[1], p2[1], p3[1]]
            kp = np.linalg.solve(mx, my)  # gibt die Faktoren der Parabelgleichnung aus

            x = -sw
            punkt = []
            while x < sw:
                y = kp[0]*x*x + kp[1]*x + kp[2]
                punkt.append((x+ sw/2, -y + sh/2))
                x += 1

            self.brush.move_to(*punkt[0])
            for p in punkt[1:]:
                self.brush.line_to(*p)
            #print ("letzer Punkt", p)
            self.brush.set_line_width(2)
            self.brush.set_source_rgb(0, 0, 1)
            self.brush.stroke()

            self.drawArea.queue_draw()
        else:
            pass

    def zeichneKurve3_O(self, widget):
        self.drawType = "Kurve 3.Ord."
        print (len(self.punkte))
        if len(self.punkte) > 5:
            self.displayMessage(self.success, "Zu viele Punkte angeklickt!")
            self.neuStart(self)
        elif len(self.punkte) < 4:
            self.displayMessage(self.success, "Zu wenig Punkte angeklickt!")
            self.neuStart(self)
        elif len(self.punkte) == 4:
            p1 = self.punkte[0]
            p2 = self.punkte[1]
            p3 = self.punkte[2]
            p4 = self.punkte[3]

            mx = ([[p1[0]**3, p1[0]**2, p1[0], 1], [p2[0]**3, p2[0]**2, p2[0], 1],
                    [p3[0]**3, p3[0]**2, p3[0], 1], [p4[0]**3, (p4[0])**2, p4[0], 1]])
            my = [p1[1], p2[1], p3[1], p4[1]]
            kp = np.linalg.solve(mx, my)  # gibt die Faktoren der Funktionsgleichung aus

            x = -sw
            punkt = []
            while x < sw:
                y = kp[0]*x**3 + kp[1]*x**2 + kp[2]*x + kp[3]
                punkt.append((x+ sw/2, -y + sh/2))
                x += 1

            self.brush.move_to(*punkt[0])
            for p in punkt[1:]:
                self.brush.line_to(*p)
            #print ("letzer Punkt", p)
            self.brush.set_line_width(2)
            self.brush.set_source_rgb(0, 0, 1)
            self.brush.stroke()

            self.drawArea.queue_draw()
        else:
            pass

    def zeichneKurve4_O(self, widget):
        self.drawType = "Kurve 4.Ord."
        print (len(self.punkte))
        if len(self.punkte) > 5:
            self.displayMessage(self.success, "Zu viele Punkte angeklickt!")
            self.neuStart(self)
        elif len(self.punkte) < 5:
            self.displayMessage(self.success, "Zu wenig Punkte angeklickt!")
            self.neuStart(self)
        else:
            p1 = self.punkte[0]
            p2 = self.punkte[1]
            p3 = self.punkte[2]
            p4 = self.punkte[3]
            p5 = self.punkte[4]

            mx = ([[p1[0]**4, p1[0]**3, p1[0]**2, p1[0], 1], [p2[0]**4, p2[0]**3, p2[0]**2, p2[0], 1],
                    [p3[0]**4, p3[0]**3, p3[0]**2, p3[0], 1], [p4[0]**4, p4[0]**3, (p4[0])**2, p4[0], 1],
                    [p5[0]**4, p5[0]**3, (p5[0])**2, p5[0], 1]])
            my = [p1[1], p2[1], p3[1], p4[1], p5[1]]
            kp = np.linalg.solve(mx, my)  # gibt die Faktoren der Funktionsgleichung aus

            x = -sw
            punkt = []
            while x < sw:
                y = kp[0]*x**4 + kp[1]*x**3 + kp[2]*x**2 + kp[3]*x + kp[4]
                punkt.append((x+ sw/2, -y + sh/2))
                x += 1

            self.brush.move_to(*punkt[0])
            for p in punkt[1:]:
                self.brush.line_to(*p)
            #print ("letzer Punkt", p)
            self.brush.set_line_width(2)
            self.brush.set_source_rgb(0, 0, 1)
            self.brush.stroke()

            self.drawArea.queue_draw()

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

    def zeigeKoordinaten(self, type, text):
        markup = "<span foreground='" + type + "'>" + text + "</span>"
        self.xyAnzeige.set_markup(markup)
        self.Koordinaten.popup()
        #self.hideMessageTimed()

    @threaded
    def hideMessageTimed(self):
        time.sleep(1)
        GLib.idle_add(self.messageWidget.popdown)


