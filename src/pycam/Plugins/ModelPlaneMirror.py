# -*- coding: utf-8 -*-
"""
$Id$

Copyright 2011 Lars Kruse <devel@sumpfralle.de>

This file is part of PyCAM.

PyCAM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyCAM is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyCAM.  If not, see <http://www.gnu.org/licenses/>.
"""


import pycam.Plugins


class ModelPlaneMirror(pycam.Plugins.PluginBase):

    UI_FILE = "model_plane_mirror.ui"
    DEPENDS = ["Models"]

    def setup(self):
        if self.gui:
            mirror_box = self.gui.get_object("ModelMirrorBox")
            mirror_box.unparent()
            self.core.register_ui("model_handling", "Mirror", mirror_box, 0)
            self.gui.get_object("PlaneMirrorButton").connect("clicked",
                    self._plane_mirror)
            self.core.register_event("model-selection-changed",
                    self._update_plane_widgets)
            self._update_plane_widgets()
        return True

    def teardown(self):
        if self.gui:
            self.core.unregister_ui("model_handling",
                    self.gui.get_object("ModelMirrorBox"))

    def _update_plane_widgets(self):
        plane_widget = self.gui.get_object("ModelMirrorBox")
        if self.core.get("models").get_selected():
            plane_widget.show()
        else:
            plane_widget.hide()

    def _plane_mirror(self, widget=None):
        models = self.core.get("models").get_selected()
        if not models:
            return
        self.core.emit_event("model-change-before")
        progress = self.core.get("progress")
        progress.update(text="Mirroring model")
        progress.disable_cancel()
        progress.set_multiple(len(models), "Model")
        for plane in ("XY", "XZ", "YZ"):
            if self.gui.get_object("MirrorPlane%s" % plane).get_active():
                break
        for model in models:
            model.transform_by_template("%s_mirror" % plane.lower(),
                    callback=progress.update)
            progress.update_multiple()
        progress.finish()
        self.core.emit_event("model-change-after")
