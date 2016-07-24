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
import PadArray_Thm as PA

class SOT_Wizard(HFWP.HelpfulFootprintWizardPlugin):

    def GetName(self):
        return "SOT Wizard"

    def GetDescription(self):
        return "SOT Footprint Wizard"

    def GenerateParameterList(self):
        # Tab Pads, opcion n, recibe numeros naturales, valor por defecto = 3
	self.AddParam("Pads", "Family: SOT23, SOT89, SOT143, SOT223, SOTFL", self.uString, 'SOT223')
        self.AddParam("Pads", "n", self.uNatural, 3)
	self.AddParam("Pads", "Pitch", self.uMM, 0.2)        
        self.AddParam("Pads", "Pad width", self.uMM, 0.3)
        self.AddParam("Pads", "Pad length", self.uMM, 0.9)
        self.AddParam("Pads", "Vertical pitch", self.uMM, 8.9)
        self.AddParam("Pads", "Horizontal pitch", self.uMM, 8.9)
        self.AddParam("Pads", "Oval", self.uBool, True)
        self.AddParam("Pads", "Package width", self.uMM, 9)
        self.AddParam("Pads", "Package height", self.uMM, 9)

        # Tab Naming
        self.AddParam("FootprintName", "Prefix", self.uString, 'SOT')
	# IPC
	self.AddParam("IPC", "Density, M(Most), N(Nominal), L(Least)", self.uString, 'N')
	# Silkscreen pin 1 mark
	self.AddParam("IPC", "Pin 1 mark, c(circle), l(line)", self.uString, 'l')

    def CheckParameters(self):
        self.CheckParamInt("Pads", "*n", is_multiple_of = 1)
        self.CheckParamBool("Pads", "*Oval")

    def GetValue(self):
	_density = self.parameters["IPC"]["*Density, M(Most), N(Nominal), L(Least)"]

	_prefix = self.parameters["FootprintName"]["*Prefix"]
	_padNo = self.parameters["Pads"]["*n"]
	_pitch = self.parameters["Pads"]["Pitch"] / 10000
	_width = self.parameters["Pads"]["Package width"] / 10000
	_height = self.parameters["Pads"]["Package height"] / 10000
        return "%s%dP%dX%d%d-%s" % (_prefix, _pitch, _width, _height, _padNo, _density)

    def DrawOriginGravityCenter(self):

	# Draw the Origin of Gravity Center circle and cross lines.
        self.draw.SetLayer(pcbnew.F_Fab)
	_thickness = pcbnew.FromMM(0.05)
	self.draw.SetLineThickness(_thickness)
	# Drawing the circle in ( 0 , 0 ) with radius 0.25 mm
	self.draw.Circle(0, 0, (pcbnew.FromMM(0.25) - (_thickness / 2)))
	# Drawing vertical line
	self.draw.Line(0, - pcbnew.FromMM(0.35), 0, pcbnew.FromMM(0.35))
	# Draw horizontal line
	self.draw.Line(- pcbnew.FromMM(0.35), 0, pcbnew.FromMM(0.35), 0)

    def CalculatePadDimentions(self):
        print "Que tranza prros"
	
	_family = self.parameters["Pads"]["*Family: SOT23, SOT89, SOT143, SOT223, SOTFL"]
	_density = self.parameters["IPC"]["*Density, M(Most), N(Nominal), L(Least)"]
	
	if _family in ['SOTFL', 'SOT89'] and _density == 'N':

		if _density == 'N':
			_toe = 0.20
			_heel = 0.00
			_side = 0.00
			_roundOff = 0.1
			_courtyard = 0.15
		elif _density == 'M':
			_toe = 0.30
			_heel = 0.00
			_side = 0.05
			_roundOff = 0.1
			_courtyard = 0.20
		elif _density == 'L':
			_toe = 0.10
			_heel = 0.00
			_side = -0.05
			_roundOff = 0.1
			_courtyard = 0.12
	else:
		if _density == 'N':
			_toe = 0.35
			_heel = 0.35
			_side = 0.03
			_roundOff = 0.1
			_courtyard = 0.25
		elif _density == 'M':
			_toe = 0.55
			_heel = 0.45
			_side = 0.05
			_roundOff = 0.1
			_courtyard = 0.50
		elif _density == 'L':
			_toe = 0.15
			_heel = 0.25
			_side = 0.01
			_roundOff = 0.1
			_courtyard = 0.12


    def BuildThisFootprint(self):
	
	self.DrawOriginGravityCenter()
	self.CalculatePadDimentions()

        pads = self.parameters["Pads"]
	name = self.parameters["FootprintName"]

        module_prefix = name["*Prefix"]
        pad_pitch = pads["Pitch"]
        pad_length = self.parameters["Pads"]["Pad length"]
        pad_width = self.parameters["Pads"]["Pad width"]

        v_pitch = pads["Vertical pitch"]
        h_pitch = pads["Horizontal pitch"]

        pads_per_row = pads["*n"] // 4

        row_len = (pads_per_row - 1) * pad_pitch

        pad_shape = pcbnew.PAD_SHAPE_OVAL if pads["*Oval"] else pcbnew.PAD_SHAPE_RECT

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

        lim_x = pads["Package width"] / 2
        lim_y = pads["Package height"] / 2
        inner = (row_len / 2) + pad_pitch

        self.draw.SetLayer(pcbnew.F_CrtYd)
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
