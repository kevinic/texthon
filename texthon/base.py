class Simple_Enum:
	def __init__(self, *args):
		names = list(args)
		self.names = names
		index = 0
		for name in names:
			setattr(self, name, index)
			index += 1

