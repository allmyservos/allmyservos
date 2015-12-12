#!/usr/bin/python
#######################################################################
# AllMyServos - Fun with PWM
# Copyright (C) 2015  Donate BTC:14rVTppdYQzLrqay5fp2FwP3AXvn3VSZxQ
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
# along with this program.  If not, see http://www.gnu.org/licenses/.
#######################################################################
import sys, os

contrib = os.path.join(os.getcwd(), 'contrib')
vendors = os.listdir(contrib)
vendors = [ x for x in vendors if os.path.isdir(os.path.join(contrib, x)) ]
for v in vendors:
	vpath = os.path.join(contrib, v)
	mods = os.listdir(vpath)
	mods = [ x for x in mods if os.path.isdir(os.path.join(vpath, x)) ]
	for m in mods:
		sys.path.append(os.path.join(vpath, m))