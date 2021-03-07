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


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='im.bernard.funkcio',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        self.win = self.props.active_window
        if not self.win:
            self.win = Main_Window(application=self)
        self.win.present()

        self.AktionMenu()


    def AktionMenu(self):
        infoAktion = Gio.SimpleAction.new("about", None)
        infoAktion.connect("activate", self.beiInfoKlick)
        self.add_action(infoAktion)


    def beiInfoKlick(self, action, widget):
        infoDialog = Gtk.AboutDialog()
        infoDialog.set_logo_icon_name("im.bernard.funkcio")
        infoDialog.set_destroy_with_parent(True)
        infoDialog.set_name("Funkcio")
        infoDialog.set_version("0.7")
        infoDialog.set_authors(["Walter Bernard"])
        infoDialog.set_artists(["Tobias Bernard"])
        infoDialog.set_license_type(Gtk.License.GPL_3_0)
        infoDialog.set_copyright("© 2021 Walter Bernard")
        infoDialog.set_modal(True)
        infoDialog.set_transient_for(self.win)

        infoDialog.run()
        infoDialog.destroy()


def main(version):
    app = Application()
    return app.run(sys.argv)


