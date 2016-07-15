#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

from __future__ import division
import pcbnew

import HelpfulFootprintWizardPlugin as HFWP
import FootprintWizardDrawingAids as FWDA
import PadArray_Thm as PA

class SOT_Wizard(HFWP.HelpfulFootprintWizardPlugin):

    def GetName(self):
        return "SOT Wizard"

    def GetDescription(self):
        return "SOT Footprint Wizard"

    def GenerateParameterList(self):
        # Tab Pads, opcion n, recibe numeros naturales, valor por defecto = 3
        self.AddParam("Pads", "n", self.uNatural, 3)
	self.AddParam("Pads", "Pitch", self.uMM, 0.2)        
        self.AddParam("Pads", "pad width", self.uMM, 0.3)
        self.AddParam("Pads", "pad length", self.uMM, 0.9)
        self.AddParam("Pads", "vertical pitch", self.uMM, 8.9)
        self.AddParam("Pads", "horizontal pitch", self.uMM, 8.9)
        self.AddParam("Pads", "oval", self.uBool, True)
        self.AddParam("Pads", "package width", self.uMM, 9)
        self.AddParam("Pads", "package height", self.uMM, 9)
        self.AddParam("Pads", "epad width", self.uMM, 7.5)
        self.AddParam("Pads", "epad length", self.uMM, 7.5)
        self.AddParam("Pads", "epad subdivision h", self.uNatural, 2)
        self.AddParam("Pads", "epad subdivision v", self.uNatural, 2)
        self.AddParam("Pads", "epad thermal h pitch", self.uMM, 1.0)
        self.AddParam("Pads", "epad thermal v pitch", self.uMM, 1.0)
        self.AddParam("Pads", "epad solder paste ratio", self.uNatural, 0.8)
        self.AddParam("Pads", "epad thermal via diam", self.uMM, 0.3)
        self.AddParam("Pads", "epad thermal via size", self.uMM, 0.5)
        # Tab Naming
        self.AddParam("FootprintName", "Prefix", self.uString, 'SOT')
	# IPC
	self.AddParam("IPC", "Density, M (Most), N(Nominal), L(Least)", self.uString, 'N')

    def CheckParameters(self):
        self.CheckParamInt("Pads", "*n", is_multiple_of = 1)
        self.CheckParamBool("Pads", "*oval")

    def GetValue(self):
	_density = self.parameters["IPC"]["*Density, M (Most), N(Nominal), L(Least)"]
	"""
	if _density == 'N':
		_toe = 0.20
		_heel = 0.00
		_side = 0.00
		_roundOff = 0.1
		_courtyard = 0.15
	else if _density == 'M':
		_toe = 0.30
		_heel = 0.00
		_side = 0.05
		_roundOff = 0.1
		_courtyard = 0.20
	else if _density == 'L':
		_toe = 0.10
		_heel = 0.00
		_side = -0.05
		_roundOff = 0.1
		_courtyard = 0.12
	"""
	_prefix = self.parameters["FootprintName"]["*Prefix"]
	_padNo = self.parameters["Pads"]["*n"]
	_pitch = self.parameters["Pads"]["Pitch"] / 10000
	_width = self.parameters["Pads"]["package width"] / 10000
	_height = self.parameters["Pads"]["package height"] / 10000
        return "%s%dP%dX%d%d-%s" % (_prefix, _pitch, _width, _height, _padNo, _density)

    def BuildThisFootprint(self):
        pads = self.parameters["Pads"]
	name = self.parameters["FootprintName"]

        module_prefix = name["*Prefix"]
        pad_pitch = pads["Pitch"]
        pad_length = self.parameters["Pads"]["pad length"]
        pad_width = self.parameters["Pads"]["pad width"]

        epad_length = self.parameters["Pads"]["epad length"]
        epad_width = self.parameters["Pads"]["epad width"]
        epad_subd_l = pads["*epad subdivision h"]
        epad_subd_w = pads["*epad subdivision v"]

        epad_th_pitch_l = self.parameters["Pads"]["epad thermal h pitch"]
        epad_th_pitch_w = self.parameters["Pads"]["epad thermal v pitch"]
        epad_paste_ratio = pads["*epad solder paste ratio"]

        epad_th_via_dm = self.parameters["Pads"]["epad thermal via diam"]
        epad_th_via_sz = self.parameters["Pads"]["epad thermal via size"]

        v_pitch = pads["vertical pitch"]
        h_pitch = pads["horizontal pitch"]

        pads_per_row = pads["*n"] // 4

        row_len = (pads_per_row - 1) * pad_pitch

        pad_shape = pcbnew.PAD_SHAPE_OVAL if pads["*oval"] else pcbnew.PAD_SHAPE_RECT

        h_pad = PA.PadMaker(self.module).SMDPad(
            pad_width, pad_length, shape=pad_shape)
        v_pad = PA.PadMaker(self.module).SMDPad(
            pad_length, pad_width, shape=pad_shape)

        #left row
        pin1Pos = pcbnew.wxPoint(-h_pitch / 2, 0)
        array = PA.PadLineArray(h_pad, pads_per_row, pad_pitch, True,
                                pin1Pos)
        array.SetFirstPadInArray(1)
        array.AddPadsToModule(self.draw)

        #bottom row
        pin1Pos = pcbnew.wxPoint(0, v_pitch / 2)
        array = PA.PadLineArray(v_pad, pads_per_row, pad_pitch, False,
                                pin1Pos)
        array.SetFirstPadInArray(pads_per_row + 1)
        array.AddPadsToModule(self.draw)

        #right row
        pin1Pos = pcbnew.wxPoint(h_pitch / 2, 0)
        array = PA.PadLineArray(h_pad, pads_per_row, -pad_pitch, True,
                                pin1Pos)
        array.SetFirstPadInArray(2*pads_per_row + 1)
        array.AddPadsToModule(self.draw)

        #top row
        pin1Pos = pcbnew.wxPoint(0, -v_pitch / 2)
        array = PA.PadLineArray(v_pad, pads_per_row, -pad_pitch, False,
                                pin1Pos)
        array.SetFirstPadInArray(3*pads_per_row + 1)
        array.AddPadsToModule(self.draw)

        #epad
        if epad_length!=0 and epad_width!=0:  #there is exposed pad
            e_pad = PA.PadMaker(self.module).SMDePad(
            epad_width, epad_length, shape=pcbnew.PAD_SHAPE_RECT)
            epadPos = pcbnew.wxPoint (0, 0)
            array = PA.PadLineArray(e_pad, 1, 1, False,
                                    epadPos)
            array.SetFirstPadInArray(pads["*n"]+1)
            array.AddPadsToModule(self.draw)

            if epad_subd_l!=0 and epad_subd_w!=0 and epad_th_pitch_w!=0 and epad_th_pitch_l!=0:
            #if we want epad
                epad_width_part_size_w = epad_width / epad_subd_w  #size of one part of exposed pad
                epad_width_part_size_l = epad_length / epad_subd_l
                epad_paste = PA.PadMaker(self.module).SMDPad(
                epad_width_part_size_w*epad_paste_ratio, epad_width_part_size_l*epad_paste_ratio, shape=pcbnew.PAD_SHAPE_RECT)

                n_epad_parts_w = int(epad_width/epad_th_pitch_w)
                n_epad_parts_l = int(epad_length/epad_th_pitch_l)

                array_epad = PA.PadThermalArray(epad_paste, epad_subd_l, epad_subd_w,
                                    epad_width_part_size_l, epad_width_part_size_w, epadPos)

                array_epad.SetFirstPadInArray(pads["*n"]+1)
                array_epad.AddPadsToModule(self.draw)

                if epad_th_via_sz!=0 and epad_th_via_dm!=0:
                    #if we want epad thermal vias
                    epad_th_pad = PA.PadMaker(self.module).THPad(epad_th_via_sz,
                                epad_th_via_sz, epad_th_via_dm, shape=pcbnew.PAD_SHAPE_CIRCLE)
                    array_epad_th = PA.PadThermalArray(epad_th_pad, n_epad_parts_l, n_epad_parts_w,
                                                epad_th_pitch_l, epad_th_pitch_w, epadPos)
                    array_epad_th.SetFirstPadInArray(pads["*n"]+1)
                    array_epad_th.AddPadsToModule(self.draw)

        lim_x = pads["package width"] / 2
        lim_y = pads["package height"] / 2
        inner = (row_len / 2) + pad_pitch

        #top left - diagonal
        self.draw.Line(-lim_x, -inner, -inner, -lim_y)
        # top right
        self.draw.Polyline([(inner, -lim_y), (lim_x, -lim_y), (lim_x, -inner)])
        # bottom left
        self.draw.Polyline([(-inner, lim_y), (-lim_x, lim_y), (-lim_x, inner)])
        # bottom right
        self.draw.Polyline([(inner, lim_y), (lim_x, lim_y), (lim_x, inner)])

        #reference and value
        text_size = pcbnew.FromMM(1.2)  # IPC nominal

        text_offset = v_pitch / 2 + text_size + pad_length / 2

        self.draw.Value(0, -text_offset, text_size)
        self.draw.Reference(0, text_offset, text_size)

SOT_Wizard().register()
