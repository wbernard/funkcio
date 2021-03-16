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

@Gtk.Template(resource_path='/im/bernard/Funkcio/window.ui')

class Main_Window(Gtk.ApplicationWindow):
    __gtype_name__ = 'Main_Window'

    drawArea      = Gtk.Template.Child()
    messageLabel  = Gtk.Template.Child()
    messageWidget = Gtk.Template.Child()
    textAusgabe   = Gtk.Template.Child()
    gerade        = Gtk.Template.Child()
    parabel       = Gtk.Template.Child()
    kurve3o       = Gtk.Template.Child()
    parabelHor    = Gtk.Template.Child()
    kurve3hor     = Gtk.Template.Child()
    neustart      = Gtk.Template.Child()
    quadranten1   = Gtk.Template.Child()
    quadranten2   = Gtk.Template.Child()
    speichern     = Gtk.Template.Child()
    infoKnopf     = Gtk.Template.Child()
    zoomEin       = Gtk.Template.Child()
    zoomAus       = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.drawArea.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.drawArea.connect('draw', self.onDraw)
        self.drawArea.connect('configure-event', self.onConfigure)
        self.drawArea.connect("motion-notify-event", self.zeigeKoord)
        self.drawArea.connect('button-press-event', self.holePunkt)
        self.gerade.connect('clicked', self.zeichneGerade)
        self.parabel.connect('clicked', self.zeichneParabel)
        self.kurve3o.connect('clicked', self.zeichneKurve3_O)
        self.parabelHor.connect('clicked', self.zeichneParabelHor)
        self.kurve3hor.connect('clicked', self.zeichneKurve3_OHor)
        self.neustart.connect('clicked', self.neuStart)
        self.quadranten1.connect('clicked', self.einVierQuad, "1")
        self.quadranten2.connect('clicked', self.einVierQuad, "2")
        self.zoomEin.connect('clicked', self.beiZoomEin)
        self.zoomAus.connect('clicked', self.beiZoomAus)

        self.linfarb     = [[0.1,0.37,0.71], [0.38,0.21,0.51],[0.15,0.64,0.41], [0.65,0.11,0.18], [0.39,0.27,0.17]]
        self.zeichneneu  = True
        self.quadra      = 8
        self.typ         = 0
        self.surface     = None
        self.aktBreite   = 0
        self.aktHoehe    = 0
        self.crFarbe     = [0.88, 0.11, 0.14, 1.0]
        self.crDicke     = 4
        self.punkte      = []
        self.anfang      = True
        self.ende        = False

        self.quadranten1.set_active(True)
        self.quadranten2.set_active(False)
        self.zoomFaktor = 1

        self.success    = "#88cc27"
        self.warning    = "#00008b"
        self.error      = "#ff0000"

    def einVierQuad(self, widget, name):
        if name == "1":
            self.quadra = 8
            self.zeichneneu    = True
            self.onDraw(self.drawArea, self.cr)
            self.drawArea.queue_draw()

        elif name == "2":
            self.quadra = 2
            self.zeichneneu    = True
            self.onDraw(self.drawArea, self.cr)
            self.drawArea.queue_draw()

        else:
            print ("Da stimmt etwas nicht!")

    def vierEinQuad(self, widget):
        if self.quadranten2.get_active() and not self.quadranten1.get_active():
            pass
        else:
            self.quadranten2.set_active(True)
            self.quadranten1.set_active(False)
            if self.quadra != 2:
                self.quadra = 2
            self.zeichneneu    = True
            self.onDraw(self.drawArea, self.cr)
            self.drawArea.queue_draw()

    def beiZoomEin(self, widget):
        self.zoomFaktor = self.zoomFaktor+0.25
        self.zeichneneu    = True
        self.onDraw(self.drawArea, self.cr)
        self.drawArea.queue_draw()

    def beiZoomAus(self, widget):
        self.zoomFaktor = self.zoomFaktor-0.25
        self.zeichneneu    = True
        self.onDraw(self.drawArea, self.cr)
        self.drawArea.queue_draw()

    def onConfigure(self, area, eve, data = None): # wird bei Änderung des Fensters aufgerufen
        ab = area.get_allocated_width()   #liest die aktuellen Abmessungen des Fensters ein
        ah = area.get_allocated_height()

        _surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, ab, ah)

        # wenn das fenster verändert wird, wird eine neue Zeichenebene erstellt
        if self.surface is not None:
            #global sb, sh
            sb = self.surface.get_width()
            sh = self.surface.get_height()

            # bei Verkleinerung bleibt die alte Ebene
            if ab < sb and ah < sh:
                return False

            cr = cairo.Context(_surface)

            # die alte ebene wird in die neue geladen
            cr.set_source_surface(self.surface, 0.0, 0.0)
            cr.scale(ab, ah)
            cr.paint()

            self.aktBreite   = ab
            self.aktHoehe  = ah

            self.zeichneneu    = True  # d.h. dass in onDraw die Zeichenfläche neu gezeichnet wird


        else:
            self.drawArea.set_size_request(self.aktBreite, self.aktHoehe)

        self.surface = _surface
        self.cr   = cairo.Context(self.surface)
        return False

        # onDraw wird aufgerufen, wenn die Zeichebene neu gerendert wird
    def onDraw(self, area, cr):    # area ist das Fenster  cr ist ein context
        ab = area.get_allocated_width()   # liest die aktuellen Abmessungen des Fensters ein
        ah = area.get_allocated_height()

        if self.surface is not None:
            cr.set_source_surface(self.surface, 0.0, 0.0)
            cr.paint()
            global sb, sh, zf
            zf = self.zoomFaktor            #Zoomfaktor wird global definiert
            sb = self.surface.get_width()   # Breite der Zeichenebene
            sh = self.surface.get_height()  # Höhe der Zeichenebene

            # bei Verkleinerung bleibt die alte Ebene
            if ab < sb and ah < sh:
                return False

            if self.zeichneneu and self.quadra != 0:
                global pva, pha
                pva = sb/self.quadra
                pha = sh - sh/self.quadra

                if self.anfang:
                    self.zeigeAnweisung(self.warning, _("Klicke auf eine beliebige Anzahl Punkte im Koordinatensystem \n und wähle dann die gewünschte Funktion!"))
                    self.anfang = False
                else:
                    pass

                self.zeichneAchsen(pva, pha, zf)
                #print ("Punkte", self.punkte[:])

                for p in self.punkte:   # punkte sind die eingegebenen Punkte

                    x1 = p[0] + pva      # x1 und y1 sind die Punkte im absoluten System
                    y1 = -p[1] + pha
                    #print ("pva =", pva, "pha =", pha)
                    self.zeichnePunkt(x1, y1, pva, pha)

                if self.typ != 0:
                    self.berechneZeichne(pva, pha)

                if self.ende:
                    self.cr.move_to(70+sb/2, sh-40)
                    self.cr.set_font_size(16)
                    print (_("Gleichung:"), formel)
                    self.cr.show_text(formel)
                else:
                    pass

                #self.drawArea.queue_draw()
                self.zeichneneu = False

        else:
            print ("keine Zeichenebene !!")

        return False


    def zeigeKoord (self, area, eve):
        if self.quadra == 2 or self.quadra == 8:   # vier oder ein Quadranten
            (x1, y1) = eve.x, eve.y
            #global pva, pha         # Position der vertikalen/horizontalen Achse
            pva = sb/self.quadra
            pha = sh - sh/self.quadra
            x = int((x1-pva)/zf)         # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
            y = int((-y1+pha)/zf)

            koord = "  x  " + str(x) + ", y  " + str(y)
            self.textAusgabe.set_text(koord)
            #self.cr.move_to(150, sh-40)
            #self.cr.set_font_size(16)
            #self.cr.show_text(koord)
        else:
            self.displayMessage(self.error, "Da ist etwas faul!")

    def holePunkt(self, area, eve):
        x1 = eve.x-(zf-1)*(eve.x-pva)/zf
        y1 = eve.y+(zf-1)*(pha-eve.y)/zf

        x = int((x1- pva))         # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
        y = int((-y1+pha))
        #print("(" + str(x) + ", " + str(y) + ")")

        self.zeichnePunkt(x1,y1,pva,pha)

        self.drawArea.queue_draw()

    def zeichneAchsen(self, pva, pha, zf):
        self.cr.rectangle(0, 0, sb, sh)  # x, y, width, height
        self.cr.set_operator(0);
        self.cr.fill()
        self.cr.set_operator(1)
        self.linio(0, pha, sb, pha, 1.8) # zeichnet die horizontale Achse
        self.linio(pva, 0, pva, sh, 1.8)

        aa = 0
        rw = 50*zf              # Rasterweite
        while (aa < sh):
            aa = aa + rw
            self.linio(0, pha+aa, sb, pha+aa, 0.2) # zeichnet horizontale Rasterlinien
            self.linio(0, pha-aa, sb, pha-aa, 0.2)
        aa = 0
        while (aa < sb):
            aa = aa + rw
            self.linio(pva+aa, 0, pva+aa, sh, 0.2) # zeichnet vertikale Rasterlinien
            self.linio(pva-aa, 0, pva-aa, sh, 0.2)

    def neuStart(self, widget):

        self.zoomFaktor = 1
        zf = self.zoomFaktor
        self.ende = False
        self.zeichneAchsen(pva, pha, zf)
        self.drawArea.queue_draw()

        del self.punkte[:]
        #self.quadra = 8
        self.typ = 0

    def zeichnePunkt(self,x1,y1,pva,pha):
        rgba = self.crFarbe
        self.cr.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        self.cr.set_line_width(self.crDicke)
        self.cr.set_line_cap(1) # Linienende 0 = BUTT, 1 = rund  2 = eckig

        px = pva+(x1-pva)*zf
        py = pha-(pha-y1)*zf
        self.cr.arc(px, py, 3, 0, 2*math.pi)
        self.cr.fill()

        self.cr.set_source_rgba(0, 0, 0, 1)
        self.cr.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_NORMAL)
        self.cr.move_to(px+5, py)
        self.cr.set_font_size(12)

        x = int((x1- pva))      # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
        y = int((-y1+pha))
        self.cr.show_text(str(x) + ", " + str(y))

        #self.drawArea.queue_draw()

        if self.zeichneneu == False:   # wenn es nicht eine Anpassung der Zeichenfläche ist
            self.punkte.append([x, y])

    def berechneZeichne(self, pva, pha):

        n = len(self.punkte)
        #print (n)
        xp = []
        yp = []
        global formel

        for i in range(n):
            xp.append(self.punkte[i][0])
            yp.append(self.punkte[i][1])

        xa = np.array(xp)   # Liste wird in Datenfeld (array) umgewandelt
        ya = np.array(yp)

        # fit gibt die Faktoren der Kurvengleichung aus
        if self.typ == 4:
            fit = np.polyfit(ya,xa,2)  # horizonzale Parabel vertauscht x und y Werte
            #print (fit)
        elif self.typ == 5:
            fit = np.polyfit(ya,xa,3)  # horizonzale Kurve vertauscht x und y Werte
            #print (fit)
        else:
            fit = np.polyfit(xa,ya, self.typ)

        if self.typ == 1:
            af = fit[0]
            bf = fit[1]

            x = -sb/zf
            punkt = []          # hier geht es um die einzelnen Punkte der Kurve
            while x < sb/zf:
                y = af*x + bf   # Geradengleichnung y = a*x + b
                punkt.append((zf*x+ pva, -y*zf + pha))
                x += 1

            #print (punkt)
            self.zeichneFunktion(punkt)

            a = round(af,3)
            b = round(bf,0)
            formel = "y = " + "{:+}".format(a) + "x " + "{:+}".format(b)

        elif self.typ == 2:
            af = fit[0]
            bf = fit[1]
            cf = fit[2]

            x = -sb/zf
            punkt = []      # hier geht es um die einzelnen Punkte der Kurve
            while x < sb/zf:
                y = af*x**2 + bf*x + cf   # Gleichung der Parabel
                punkt.append((zf*x+ pva, -y*zf + pha))
                x += 1

            self.zeichneFunktion(punkt)

            a = round(af,5)
            b = round(bf,3)
            c = round(cf,0)

            formel = "y = " + "{:+}".format(a) + "x²  " + "{:+}".format(b)+ "x  " + "{:+}".format(c)

        elif self.typ == 3:     # 3. Grades vertikal
            af = fit[0]
            bf = fit[1]
            cf = fit[2]
            df = fit[3]

            x = -sb/zf
            punkt = []          # hier geht es um die einzelnen Punkte der Kurve
            while x < sb/zf:
                y = af*x**3 + bf*x**2 + cf*x + df  # Gleichung der Funkion 3.Grades
                punkt.append((zf*x+ pva, -y*zf + pha))
                x += 1

            self.zeichneFunktion(punkt)

            a = round(af,8)
            b = round(bf,5)
            c = round(cf,2)
            d = round(df,0)

            formel = "y = " + "{:+}".format(a) + "x³ " + "{:+}".format(b)+ "x² " + "{:+}".format(c)+ "x " + "{:+}".format(d)

        elif self.typ == 4:  # Parabel horizontal
            af = fit[0]
            bf = fit[1]
            cf = fit[2]

            x = -sb/zf
            punkt = []      # hier geht es um die einzelnen Punkte der Kurve
            while x < sb/zf:
                y = af*x**2 + bf*x + cf   # Gleichung der horizontalen Parabel
                punkt.append((zf*y+ pva, -x*zf + pha))
                x += 1

            self.zeichneFunktion(punkt)

            a = round(af,5)
            b = round(bf,3)
            c = round(cf,0)

            formel = "x = " + "{:+}".format(a) + "y² " + "{:+}".format(b)+ "y " + "{:+}".format(c)

        elif self.typ == 5:
            af = fit[0]
            bf = fit[1]
            cf = fit[2]
            df = fit[3]

            x = -sb/zf
            punkt = []      # hier geht es um die einzelnen Punkte der Kurve
            while x < sb/zf:
                y = af*x**3 + bf*x**2 + cf*x + df  # Gleichung der Funkion 3.Grades
                punkt.append((zf*y+ pva, -x*zf + pha))
                x += 1

            self.zeichneFunktion(punkt)

            a = round(af,8)
            b = round(bf,5)
            c = round(cf,3)
            d = round(df,0)

            formel = "x = " + "{:+}".format(a) + "y³ " + "{:+}".format(b)+ "y² " + "{:+}".format(c)+ "y " + "{:+}".format(d)

        #self.textAusgabe1.set_text(formel)
        self.drawArea.queue_draw()


    def zeichneFunktion(self,punkt):

        #for p in punkt[1:]:


        self.cr.move_to(*punkt[0])
        for p in punkt[1:]:
            self.cr.line_to(*p)

        self.cr.set_line_width(2)
        i = self.typ-1
        f = self.linfarb
        self.cr.set_source_rgb(f[i][0],f[i][1],f[i][2])
        self.cr.stroke()

    def zeichneGerade(self, widget):
        self.typ = 1
        print (_("Gerade "), len(self.punkte), _("Punkte"))
        if  len(self.punkte) < 2:
            self.displayMessage(self.success, _("Mindestens zwei Punkte!"))
        elif len(self.punkte) >= 2:
            self.berechneZeichne(pva, pha)
            self.letzteFunktion(widget)

    def zeichneParabel(self, widget):
        self.typ = 2
        print (_("Parabel "), len(self.punkte), _("Punkte"))
        if len(self.punkte) < 3:
            self.displayMessage(self.success, _("Mindestens drei Punkte!"))
        elif len(self.punkte) >= 3:
            self.berechneZeichne(pva, pha)
            self.letzteFunktion(widget)

    def zeichneKurve3_O(self, widget):
        self.typ = 3
        print (_("Kurve 3.Grad "), len(self.punkte), _("Punkte"))
        if len(self.punkte) < 4:
            self.displayMessage(self.success, _("Mindestens vier Punkte!"))
        elif len(self.punkte) >= 4:
            self.berechneZeichne(pva, pha)
            self.letzteFunktion(widget)

    def zeichneParabelHor(self, widget):
        self.typ = 4
        print (_("Parabel horizontal "), len(self.punkte), _("Punkte"))
        if len(self.punkte) < 3:
            self.displayMessage(self.success, _("Mindestens drei Punkte!"))
        elif len(self.punkte) >= 3:
            self.berechneZeichne(pva, pha)
            self.letzteFunktion(widget)

    def zeichneKurve3_OHor(self, widget):
        self.typ = 5
        print (_("Kurve 3.Grad horizontal "), len(self.punkte), _("Punkte"))
        if len(self.punkte) < 4:
            self.displayMessage(self.success, _("Mindestens vier Punkte!"))
        elif len(self.punkte) >= 4:
            self.berechneZeichne(pva, pha)
            self.letzteFunktion(widget)

    def linio(self, x1, y1, x2, y2, sd):  # Anfangspunkt, Endpunkt und Stridicke werden benötigt
        self.cr.move_to(x1, y1)
        self.cr.line_to(x2, y2)

        self.cr.set_source_rgb(0, 0, 0)
        self.cr.set_line_width(sd)
        self.cr.stroke()

    def displayMessage(self, type, text):
        markup = "<span foreground='" + type + "'>" + text + "</span>"
        self.messageLabel.set_markup(markup)
        self.messageWidget.popup()
        self.hideMessageTimed(1)

    def zeigeAnweisung(self, type, text):
        markup = "<span foreground='" + type + "'>" + text + "</span>"
        self.messageLabel.set_markup(markup)
        self.messageWidget.popup()
        self.hideMessageTimed(4)

    def letzteFunktion(self, widget):
        self.ende = True
        self.zeichneneu = True
        self.onDraw(self.drawArea, self.cr)

    @threaded
    def hideMessageTimed(self,t):
        time.sleep(t)
        GLib.idle_add(self.messageWidget.popdown)


