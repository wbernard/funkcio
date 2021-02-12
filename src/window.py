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

# Gtk Imports

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
    textAusgabe1  = Gtk.Template.Child()
    gerade        = Gtk.Template.Child()
    parabel       = Gtk.Template.Child()
    kurve3o       = Gtk.Template.Child()
    kurve4o       = Gtk.Template.Child()
    parabelHor    = Gtk.Template.Child()
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
        self.parabelHor.connect('clicked', self.zeichneParabelHor)
        self.neustart.connect('clicked', self.neuStart)

        self.zeichne       = True
        self.surface       = None
        self.aktBreite      = 0
        self.aktHoehe     = 0
        self.crFarbe    = [1.0, 0.0, 0.0, 1.0]
        self.crDicke     = 4
        self.punkte        = []

        self.success    = "#88cc27"
        self.warning    = "#ffa800"
        self.error      = "#ff0000"

    def onConfigure(self, area, eve, data = None):
        ab = area.get_allocated_width()   #liest die aktuellen Abmessungen des Fensters ein
        ah = area.get_allocated_height()

        _surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, ab, ah)

        # if surface and area updated create new surface
        if self.surface is not None:
            global sb, sh
            sb = self.surface.get_width()
            sh = self.surface.get_height()

            # if we have shrunk keep old surface
            if ab < sb and ah < sh:
                return False

            cr = cairo.Context(_surface)

            # Load former surface to new surface
            cr.set_source_surface(self.surface, 0.0, 0.0)
            cr.scale(ab, ah)
            cr.paint()

            self.aktBreite   = ab
            self.aktHoehe  = ah

            self.zeichne    = True     # d.h. dass in onDrab die Zeichenfläche neu gezeichnet wird


        else:
            self.drawArea.set_size_request(self.aktBreite, self.aktHoehe)

        self.surface = _surface
        self.cr   = cairo.Context(self.surface)
        return False

    def onDraw(self, area, cr):   # area ist das Fenster  cr ist ein context
        ab = area.get_allocated_width()   # liest die aktuellen Abmessungen des Fensters ein
        ah = area.get_allocated_height()

        if self.surface is not None:
            cr.set_source_surface(self.surface, 0.0, 0.0)
            cr.paint()

            sb = self.surface.get_width()
            sh = self.surface.get_height()

            #print ("ab", ab, ah)
            #print ("sb", sb, sh)
            # if we have shrunk keep old surface
            if ab < sb and ah < sh:
                return False

            #print (self.zeichne)
            if self.zeichne:
                self.cr.rectangle(0, 0, sb, sh)  # x, y, width, height
                self.cr.set_operator(0);
                self.cr.fill()
                self.cr.set_operator(1)
                self.linio(0, sh/2, sb, sh/2) # zeichnet das Achsenkreuz
                self.linio(sb/2, 0, sb/2, sh)

                print ("Punkte", self.punkte[:])

                for p in self.punkte:
                    x1 = p[0] + sb/2
                    y1 = -p[1] +sh/2
                    print ("Punkt", p, x1, y1)
                    self.zeichnePunkt([x1,y1])

            self.zeichne = False

        else:
            print ("No surface info...")

        return False

    def zeigeKoord (self, area, eve):
        (x1, y1) = eve.x, eve.y
        x = int(x1-sb/2)         # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
        y = int(-y1+sh/2)
        koord = "  x  " + str(x) + ", y  " + str(y)
        #print (text)

        self.textAusgabe.set_text(koord)

    def holePunkt(self, area, eve):

        x1 = eve.x
        y1 = eve.y

        x = int(x1-sb/2)         # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
        y = int(-y1+sh/2)
        print("(" + str(x) + ", " + str(y) + ")")

        self.zeichnePunkt([x1,y1])

        self.drawArea.queue_draw()

    def neuStart(self, widget):
        sb = self.surface.get_width()
        sh = self.surface.get_height()
        self.cr.rectangle(0, 0, sb, sh)  # x, y, width, height
        self.cr.set_operator(0);
        self.cr.fill()
        self.cr.set_operator(1)
        self.linio(0, sh/2, sb, sh/2)
        self.linio(sb/2, 0, sb/2, sh)

        self.drawArea.queue_draw()
        del self.punkte[:]

    def zeichnePunkt(self,x1y1):
        rgba = self.crFarbe
        self.cr.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        self.cr.set_line_width(self.crDicke)
        self.cr.set_line_cap(1) # Linienende 0 = BUTT, 1 = rund  2 = eckig

        self.cr.arc(x1y1[0], x1y1[1], 3, 0, 2*math.pi)
        self.cr.fill()

        self.cr.set_source_rgba(0, 0, 0, 1)
        self.cr.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_NORMAL)
        self.cr.move_to(x1y1[0]+5, x1y1[1])
        self.cr.set_font_size(12)
        x = int(x1y1[0]-sb/2)         # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
        y = int(-(x1y1[1]-sh/2))
        self.cr.show_text(str(x) + ", " + str(y))

        #self.drawArea.queue_draw()

        if self.zeichne == False:   # wenn es nicht eine Anpassung der Zeichenfläche ist
            self.punkte.append([x, y])

    def berechneZeichne(self, typ):
        n = len(self.punkte)
        print (n)
        xp = []
        yp = []

        for i in range(n):
            xp.append(self.punkte[i][0])
            yp.append(self.punkte[i][1])

        xa = np.array(xp)   # Liste wird in Datenfeld (array) umgewandelt
        ya = np.array(yp)

        # fit gibt die Faktoren der Kurvengleichung aus
        if typ == 5:
            fit = np.polyfit(ya,xa,2)  # horizonzale Parabel vertauscht x und y Werte
            print (fit)
        else:
            fit = np.polyfit(xp,yp,typ)

        if typ == 1:
            af = fit[0]
            bf = fit[1]

            x = -sb
            punkt = []      # hier geht es um die einzelnen Punkte der Kurve
            while x < sb:
                y = af*x + bf   # Geradengleichnung y = a*x + b
                punkt.append((x+ sb/2, -y + sh/2))
                x += 1

            self.zeichneFunktion(punkt)

            a = round(af,3)
            b = round(bf,0)
            formel = "y = " + str(a) + "x + " + str(b)

        elif typ == 2:
            af = fit[0]
            bf = fit[1]
            cf = fit[2]

            x = -sb
            punkt = []      # hier geht es um die einzelnen Punkte der Kurve
            while x < sb:
                y = af*x**2 + bf*x + cf   # Gleichung der Parabel
                punkt.append((x+ sb/2, -y + sh/2))
                x += 1

            self.zeichneFunktion(punkt)

            a = round(af,4)
            b = round(bf,3)
            c = round(cf,0)

            formel = "y = " + str(a) + "x² + " + str(b)+ "x + " + str(c)

        elif typ == 3:
            af = fit[0]
            bf = fit[1]
            cf = fit[2]
            df = fit[3]

            x = -sb
            punkt = []      # hier geht es um die einzelnen Punkte der Kurve
            while x < sb:
                y = af*x**3 + bf*x**2 + cf*x + df  # Gleichung der Funkion 3.Ordnung
                punkt.append((x+ sb/2, -y + sh/2))
                x += 1

            self.zeichneFunktion(punkt)

            a = round(af,5)
            b = round(bf,4)
            c = round(cf,2)
            d = round(df,0)

            formel = "y = " + str(a) + "x³ + " + str(b)+ "x² + " + str(c)+ "x +" + str(d)

        elif typ == 4:
            af = fit[0]
            bf = fit[1]
            cf = fit[2]
            df = fit[3]
            ef = fit[4]

            x = -sb
            punkt = []      # hier geht es um die einzelnen Punkte der Kurve
            while x < sb:
                y = af*x**4 + bf*x**3 + cf*x**2 + df*x + ef # Gleichung der Funkion 4.Ordnung
                punkt.append((x+ sb/2, -y + sh/2))
                x += 1

            self.zeichneFunktion(punkt)

            a = round(af,7)
            b = round(bf,6)
            c = round(cf,4)
            d = round(df,2)
            e = round(ef,0)

            formel = "y = " + str(a)+ "x**4 + " +  str(b) + "x³ + " + str(c)+ "x² +" + str(d)+ "x + " + str(e)

        elif typ == 5:
            af = fit[0]
            bf = fit[1]
            cf = fit[2]

            x = -sb
            punkt = []      # hier geht es um die einzelnen Punkte der Kurve
            while x < sb:
                y = af*x**2 + bf*x + cf   # Gleichung der Parabel
                punkt.append((y+ sb/2, -x + sh/2))
                x += 1

            self.zeichneFunktion(punkt)

            a = round(af,4)
            b = round(bf,3)
            c = round(cf,0)

            formel = "x = " + str(a) + "y² + " + str(b)+ "y + " + str(c)

        self.textAusgabe1.set_text(formel)
        self.drawArea.queue_draw()

    def zeichneFunktion(self,punkt):
        self.cr.move_to(*punkt[0])
        for p in punkt[1:]:
            self.cr.line_to(*p)

        self.cr.set_line_width(2)
        self.cr.set_source_rgb(0, 0, 0.5)
        self.cr.stroke()

    def zeichneGerade(self, widget):
        typ = 1
        print ("Gerade ", len(self.punkte), "Punkte")
        if  len(self.punkte) < 2:
            self.displayMessage(self.success, "Mindestens zwei Punkte!")
        elif len(self.punkte) >= 2:
            self.berechneZeichne(typ)

    def zeichneParabel(self, widget):
        typ = 2
        print ("Parabel ", len(self.punkte), "Punkte")
        if len(self.punkte) < 3:
            self.displayMessage(self.success, "Mindestens drei Punkte!")
        elif len(self.punkte) >= 3:
            self.berechneZeichne(typ)

    def zeichneKurve3_O(self, widget):
        typ = 3
        print ("Kurve 3.Ordnung ", len(self.punkte), "Punkte")
        if len(self.punkte) < 4:
            self.displayMessage(self.success, "Mindestens vier Punkte!")
        elif len(self.punkte) >= 4:
            self.berechneZeichne(typ)

    def zeichneKurve4_O(self, widget):
        typ = 4
        print ("Kurve 4.Ordnung ", len(self.punkte), "Punkte")
        if len(self.punkte) < 5:
            self.displayMessage(self.success, "Mindestens fünf Punkte!")
        elif len(self.punkte) >= 5:
            self.berechneZeichne(typ)

    def zeichneParabelHor(self, widget):
        typ = 5
        print ("Parabel horizontal ", len(self.punkte), "Punkte")
        if len(self.punkte) < 3:
            self.displayMessage(self.success, "Mindestens drei Punkte!")
        elif len(self.punkte) >= 3:
            self.berechneZeichne(typ)

    def linio(self, x1, y1, x2, y2):
        self.cr.move_to(x1, y1)
        self.cr.line_to(x2, y2)

        self.cr.set_source_rgb(0, 0, 0)
        self.cr.set_line_width(1.5)
        self.cr.stroke()

    def displayMessage(self, type, text):
        markup = "<span foreground='" + type + "'>" + text + "</span>"
        self.messageLabel.set_markup(markup)
        self.messageWidget.popup()
        self.hideMessageTimed()


    @threaded
    def hideMessageTimed(self):
        time.sleep(1)
        GLib.idle_add(self.messageWidget.popdown)


