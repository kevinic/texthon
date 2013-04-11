import texthon.base as base

class Indent:
	""" Utility class for controlling text indentation.

		:param columns: the number of columns per indent level
		:param use_tab: whether to use tab characters for formatting
	"""

	def __init__(self, columns = 4, use_tab = True):
		self.cols = columns
		self.use_tab = use_tab

	def get_column(self, line):
		""" returns the number of columns the line has for indent """
		col = 0

		for c in line:
			if c == ' ':
				col += 1
			elif c == '\t':
				col += self.cols
			else:
				break

		return col

	def set_column(self, line, col):
		""" returns the line with indent to the specified column """
		prefix = ""
		if self.use_tab:
			prefix = int(col / self.cols) * "\t" + (col % self.cols) * " "
		else:
			prefix = col * " "
		out = prefix + line.lstrip(" \t")
		return out

	def normalize(self, block):
		""" returns a new block where each line is normalized with proper
		tabs or spaces, preserving the indent column
		"""
		in_stream = base.StringIO(block)
		out_stream = base.StringIO()

		for line in in_stream:
			out_stream.write(self.set_column(line, self.get_column(line)))
		
		return out_stream.getvalue()


	def indent(self, block, level = 1):
		""" returns a new block where each line has additional indent of the
		specified level
		"""
		in_stream = base.StringIO(block)
		out_stream = base.StringIO()

		for line in in_stream:
			col = self.get_column(line) + level * self.cols
			out_stream.write(self.set_column(line, col))
		
		return out_stream.getvalue()

	def deindent(self, block, level = 1):
		""" returns a new block where each line has the specified level of
		indent removed
		"""
		in_stream = base.StringIO(block)
		out_stream = base.StringIO()

		for line in in_stream:
			col = self.get_column(line)
			dec = min(col, level * self.cols)
			out_stream.write(self.set_column(line, col - dec))
		
		return out_stream.getvalue()

