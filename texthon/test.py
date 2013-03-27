import unittest
import os.path
from texthon.parser import Parser
from texthon.engine import Engine

class Test_Templates(unittest.TestCase):
	def do_test(self, template_file, param_file = None, out_file = None, includes = []):
		engine = Engine()
		directory = "tests/"

		(template_path, param_path, out_path) = map(
			lambda x : os.path.join(directory, x),
			(template_file, param_file, out_file))

		includes = list(map(lambda x : os.path.join(directory, x), includes))

		engine.add_includes(includes)
		path = engine.load_file(template_path).path
		engine.make()
		params = {}

		if param_file and os.path.exists(param_path):
			f = open(param_path)
			params = eval(f.read())
			f.close()

		output = engine.modules[path].main(**params)

		if out_file and os.path.exists(out_path):
			f = open(out_path)
			expected = f.read()
			self.assertEqual(expected, output)
			f.close()
		else:
			print("wrote output to file {}".format(out_path))
			f = open(out_path, "w")
			f.write(output)
			f.close()

		print("template {} generated output:\n".format(template_path))
		print(output)

	def test_hello(self):
		self.do_test("hello.tmpl.txt", "hello.tmpl.pyd", "hello.txt")

	def test_basic(self):
		self.do_test("basic.tmpl.txt", "basic.tmpl.pyd", "basic.txt")

	def test_html(self):
		#include directories
		includes = ["html", "html/sections"]
		self.do_test("doc.tmpl.txt", "doc.tmpl.pyd", "doc.html", includes)

