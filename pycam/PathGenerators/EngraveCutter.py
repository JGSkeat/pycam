# -*- coding: utf-8 -*-
"""
$Id$

Copyright 2010 Lars Kruse <devel@sumpfralle.de>
Copyright 2008-2009 Lode Leroy

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

import pycam.PathProcessors.PathAccumulator
from pycam.Geometry.Line import Line
from pycam.Geometry.Plane import Plane
from pycam.Geometry.utils import ceil
from pycam.PathGenerators import get_max_height_dynamic, get_free_paths_ode, \
        get_free_paths_triangles
from pycam.Utils import ProgressCounter
import pycam.Utils.log

log = pycam.Utils.log.get_logger()


class EngraveCutter(object):

    def __init__(self, path_processor, physics=None):
        self.pa_push = path_processor
        # We use a separated path processor for the last "drop" layer.
        # This path processor does not need to be configurable.
        self.pa_drop = pycam.PathProcessors.PathAccumulator.PathAccumulator(
                reverse=self.pa_push.reverse)
        self.physics = physics

    def GenerateToolPath(self, cutter, models, motion_grid, minz=None,
            maxz=None, draw_callback=None):
        quit_requested = False

        model = pycam.Geometry.Model.get_combined_model(models)

        if draw_callback:
            draw_callback(text="Engrave: optimizing polygon order")

        # resolve the generator
        motion_grid = list(motion_grid)
        num_of_layers = len(motion_grid)

        push_layers = motion_grid[:-1]
        push_generator = pycam.PathGenerators.PushCutter.PushCutter(
                self.pa_push, physics=self.physics)
        current_layer = 0
        for push_layer in push_layers:
            # update the progress bar and check, if we should cancel the process
            if draw_callback and draw_callback(text="Engrave: processing " \
                        + "layer %d/%d" % (current_layer + 1, num_of_layers)):
                # cancel immediately
                quit_requested = True
                break
            # no callback: otherwise the status text gets lost
            push_generator.GenerateToolPath(cutter, [model], [push_layer])
            if draw_callback and draw_callback():
                # cancel requested
                quit_requested = True
                break
            current_layer += 1

        if quit_requested:
            return self.pa_push.paths

        drop_generator = pycam.PathGenerators.DropCutter.DropCutter(self.pa_drop,
                physics=self.physics)
        drop_layers = motion_grid[-1:]
        if draw_callback:
            draw_callback(text="Engrave: processing layer " + \
                "%d/%d" % (current_layer + 1, num_of_layers))
        drop_generator.GenerateToolPath(cutter, [model], drop_layers,
                minz=minz, maxz=maxz, draw_callback=draw_callback)
        return self.pa_push.paths + self.pa_drop.paths

