# Copyright 2013 Kevin Lin
# Licensed under the Apache License, Version 2.0

import sys
python_ver = sys.version_info[0]

if python_ver < 3:
	from StringIO import StringIO
else:
	from io import StringIO

class Simple_Enum:
	def __init__(self, *args):
		names = list(args)
		self.names = names
		index = 0
		for name in names:
			setattr(self, name, index)
			index += 1

