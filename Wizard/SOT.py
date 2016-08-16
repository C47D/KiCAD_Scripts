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
        self.AddParam("Pads", "Big Pad width", self.uMM, 0.9)
        self.AddParam("Pads", "Big Pad length", self.uMM, 0.9)
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

    def CheckNoPins(_noPins):
		''' Making sure that the wizard will build footprints
		with more than 3 pins and no more than 8 pins'''

		if _noPins not in range(3,9):
			return _noPins = 3
		else:
			return _noPins

	def DrawPinOneMark(_pin1mark):
		pass

    def CalculatePadDimentions(_density, _family):

		if _family in ['SOTFL', 'SOT89']:

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
		return [_toe, _heel, _side, _roundOff, _courtyard]

    def BuildThisFootprint(self):

		pads = self.parameters["Pads"]
		name = self.parameters["FootprintName"]
		ipc = self.parameters["IPC"]

		_module_prefix = name["*Prefix"]
		_pad_pitch = pads["Pitch"]
		_pad_length = pads["Pad length"]
		_pad_width = pads["Pad width"]
		_v_pitch = pads["Vertical pitch"]
		_h_pitch = pads["Horizontal pitch"]
		_family = pads["*Family: SOT23, SOT89, SOT143, SOT223, SOTFL"]
		_density = ipc["*Density, M(Most), N(Nominal), L(Least)"]
		_pin1mark = ipc["Pin 1 mark, c(circle), l(line)"]

		self.DrawOriginGravityCenter()
		self.DrawPinOneMark(_pin1mark)
		self.CheckNoPins()
		_padDimentions = self.CalculatePadDimentions(_density, _family)

		_toePos = 0
		_heelPos = 1
		_sidePos = 2
		_roundOffPos = 3
		_courtyardPos = 4

		# Get the number of pins
		_pinsNo = self.CheckNoPins(self.parameters["Pads"]["*n"])

		if _pinsNo % 2 == 0: # even number of pins
			_pads_left_row = _pinsNo // 2
			_pads_right_row = _pinsNo // 2
			# Calculate the length of both sides of the IC
			_left_row_len = (_pads_left_row - 1) * _pad_pitch
			_right_row_len = _left_row_len
		else: # odd number of pins
			_pads_left_row = pads["*n"] - 1
			_pads_right_row = 1
			# Calculate the length of both sides of the IC
			_left_row_len = (_pads_left_row - 1) * _pad_pitch
			_right_row_len = 1


		# Oval pad shape is IPC recommended
		left_pad = PA.PadMaker(self.module).SMDPad(_pad_width, _pad_length, shape = pcbnew.PAD_SHAPE_OVAL)
		right_pad = PA.PadMaker(self.module).SMDPad(_pad_width, _pad_length, shape = pcbnew.PAD_SHAPE_OVAL)

		###############################################################################################
		#left row
		_pin1Pos = pcbnew.wxPoint(- _h_pitch / 2, 0)
		_array = PA.PadLineArray(_h_pad, _pads_per_row, _pad_pitch, True,
			                        _pin1Pos)
		_array.SetFirstPadInArray(1)
		_array.AddPadsToModule(self.draw)

	    #right row
		_pin1Pos = pcbnew.wxPoint(_h_pitch / 2, 0)
	    _array = PA.PadLineArray(_h_pad, _pads_per_row, - _pad_pitch, True,
		                            _pin1Pos)
	    _array.SetFirstPadInArray(2 * _pads_per_row + 1)
	    _array.AddPadsToModule(self.draw)

	    _lim_x = pads["Package width"] / 2
	    _lim_y = pads["Package height"] / 2
	    _inner = (_row_len / 2) + _pad_pitch

		##############################################################################################
		
		# Draw couryard
	    self.draw.SetLayer(pcbnew.F_CrtYd)
	    #top left - diagonal
	    self.draw.Line(-_lim_x, -_inner, -_inner, -_lim_y)
	    # top right
	    self.draw.Polyline([(_inner, -_lim_y), (_lim_x, -_lim_y), (_lim_x, -_inner)])
	    # bottom left
	    self.draw.Polyline([(-_inner, _lim_y), (-_lim_x, _lim_y), (-_lim_x, _inner)])
	    # bottom right
	    self.draw.Polyline([(_inner, _lim_y), (_lim_x, _lim_y), (_lim_x, _inner)])

		# Draw silkscreen
	    self.draw.SetLayer(pcbnew.F_SilkS)
	    #top left - diagonal
	    self.draw.Line(-_lim_x, -_inner, -_inner, -_lim_y)
	    # top right
	    self.draw.Polyline([(_inner, -_lim_y), (_lim_x, -_lim_y), (_lim_x, -_inner)])
	    # bottom left
	    self.draw.Polyline([(-_inner, _lim_y), (-_lim_x, _lim_y), (-_lim_x, _inner)])
	    # bottom right
	    self.draw.Polyline([(_inner, _lim_y), (_lim_x, _lim_y), (_lim_x, _inner)])

	    # Reference and value
		if _density == 'L': # Least material condition
			_text_size = pcbnew.FromMM(1.2)
		elif _density == 'N': # Nominal material condition
			_text_size = pcbnew.FromMM(1.2)
		else: # Most material condition
			_text_size = pcbnew.FromMM(1.2)

	    _text_offset = _v_pitch / 2 + _text_size + _pad_length / 2

	    self.draw.Value(0, -_text_offset, _text_size)
	    self.draw.Reference(0, _text_offset, _text_size)

SOT_Wizard().register()
