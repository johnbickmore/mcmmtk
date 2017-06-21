### Copyright: Peter Williams (2014) - All rights reserved
###
### This program is free software; you can redistribute it and/or modify
### it under the terms of the GNU General Public License as published by
### the Free Software Foundation; version 2 of the License only.
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
###
### You should have received a copy of the GNU General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

'''
Edit/create paint colours
'''

import math
import os
import hashlib
import fractions

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import GLib

from .bab import mathx
from .bab import options

from .epaint import gpaint
from .epaint import lexicon
from .epaint import vpaint
from .epaint import pchar
from .epaint import pedit
from .epaint import pseries
from .epaint import rgbh

from .gtx import actions
from .gtx import coloured
from .gtx import dialogue
from .gtx import entries
from .gtx import gutils
from .gtx import recollect
from .gtx import screen

from .pixbufx import iview

from . import icons

class ModelPaintListNotebook(gpaint.PaintListNotebook):
    class PAINT_LIST_VIEW(gpaint.ModelPaintListView):
        UI_DESCR = '''
            <ui>
                <popup name='paint_list_popup'>
                    <menuitem action='edit_selected_paint'/>
                    <menuitem action='remove_selected_paints'/>
                </popup>
            </ui>
            '''
        def populate_action_groups(self):
            """
            Populate action groups ready for UI initialization.
            """
            self.action_groups[actions.AC_SELN_UNIQUE].add_actions(
                [
                    ('edit_selected_paint', Gtk.STOCK_EDIT, None, None,
                     _('Load the selected paint into the paint editor.'), ),
                ]
            )

class ModelPaintEditor(pedit.PaintEditor):
    PAINT = vpaint.ModelPaint
    RESET_CHARACTERISTICS = False

class ModelPaintSeriesEditor(pseries.PaintSeriesEditor):
    PAINT_EDITOR = ModelPaintEditor
    PAINT_LIST_NOTEBOOK = ModelPaintListNotebook

recollect.define("editor", "last_geometry", recollect.Defn(str, ""))

class TopLevelWindow(dialogue.MainWindow):
    """
    A top level window wrapper around a palette
    """
    def __init__(self):
        dialogue.MainWindow.__init__(self)
        self.parse_geometry(recollect.get("editor", "last_geometry"))
        self.set_icon_from_file(icons.APP_ICON_FILE)
        self.editor = ModelPaintSeriesEditor()
        self.editor.action_groups.get_action('close_colour_editor').set_visible(False)
        self.editor.connect("file_changed", self._file_changed_cb)
        self.editor.set_file_path(None)
        self._menubar = self.editor.ui_manager.get_widget('/paint_collection_editor_menubar')
        self.connect("destroy", self.editor._exit_colour_editor_cb)
        self.connect("configure-event", self._configure_event_cb)
        vbox = Gtk.VBox()
        vbox.pack_start(self._menubar, expand=False, fill=True, padding=0)
        vbox.pack_start(self.editor, expand=True, fill=True, padding=0)
        self.add(vbox)
        self.show_all()
    def _file_changed_cb(self, widget, file_path):
        self.set_title(_('mcmmtk: Paint Series Editor: {0}').format(file_path))
    def _configure_event_cb(self, widget, event):
        recollect.set("editor", "last_geometry", "{0.width}x{0.height}+{0.x}+{0.y}".format(event))
