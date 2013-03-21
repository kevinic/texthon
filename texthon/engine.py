from texthon.parser import Parser
import texthon.base as base
import io
import os
import sys
import importlib
import traceback

class Exec_Exception(Exception):
	def __init__(self, str):
		Exception.__init__(self, str)
		pass

class Template_Function:
	def __init__(self):
		self.text = []
		self.code = None
		self.params = []
		self.module = None
		self.source_lines = []

	def print_exception(self, e):
		exc_type, exc_value, exc_traceback = sys.exc_info()

		def trans(frame):
			if frame[0] == "<string>":
				line = self.source_lines[frame[1] - 1]
				return self.module._path, line, "template", frame[3]
			else:
				return frame

		# skip the exec frame
		tb = map(trans, traceback.extract_tb(exc_traceback)[1:])

		sys.stderr.write("Traceback with template source lines:\n", file=sys.stderr)
		msg = traceback.format_list(tb)
		sys.stderr.write("".join(msg))

		msg = traceback.format_exception_only(type(e), e)
		sys.stderr.write("".join(msg))

		sys.stderr.write("\n")


	def execute(self, *args, **kwargs):
		output = base.StringIO()

		local_vars = {
			"_module" : self.module,
			"_params" : kwargs,
			"_textdb" : self.text,
			"_output" : output
		}

		# bind arguments
		arg_count = len(args)
		arg_index = 0
		for param in self.params:
			if arg_index < arg_count:
				local_vars[param] = args[arg_index]
				arg_index += 1
				if param in kwargs:
					raise Exec_Exception("template param {} already bound".format(param))
			else:
				if param in kwargs:
					local_vars[param] = kwargs[param]
				else:
					raise Exec_Exception("unbound template param {}".format(param))

		if arg_index < arg_count:
			raise Exec_Exception("too many arguments in template call")

		exception = None

		try:
			exec(self.code, self.module.__dict__, local_vars)
		except Exception as e:
			self.print_exception(e)
			exception = e

		if exception:
			raise Exec_Exception("execution aborted")

		return output.getvalue()

class Template_Module:
	def __init__(self, path):
		self._path = path
	pass

class Engine:
	def __init__(self):
		self.modules = {}
		self.paths = []
		self.verbose = False
		self.parser = Parser()

	def trace(self, text):
		if self.verbose:
			print(text)

	def add_includes(self, includes):
		self.paths.extend(includes)

	def set_verbose(self, verbose):
		self.verbose = verbose
		self.parser.verbose = verbose

	# current is the 'current' directory.  first choice to resolve
	# relative paths
	def fix_path(self, path, current):
		final_path = path

		if not os.path.isabs(path):
			paths = [current]
			paths.extend(self.paths)
			
			for prefix in paths:
				joined = os.path.join(prefix, path)
				if os.path.exists(joined):
					final_path = joined
					break
	
		return os.path.abspath(final_path)

	def load_text(self, text, name):
		return self.load_module(base.StringIO(text), name, "")

	def load_file(self, path, current = ""):
		path = self.fix_path(path, current)
		return self.load_module(open(path), path, os.path.dirname(path))

	def load_module(self, input_stream, path, current):
		module = self.modules.get(path, None)
		if module:
			self.trace("Modules {} is already loaded", path)
			return module

		self.trace("Loading module {}".format(path))

		module = self.parser.process_module(input_stream, path)
		module.path = path
		self.modules[path] = module

		fixed_imports = {}

		# also load any module that this module refers to
		for key, path in module.template_imports.items():
			imported = self.load_file(path, current)
			fixed_imports[key] = imported.path

		module.template_imports = fixed_imports
		return module

	def make(self):
		runtime_modules = {}

		# create runtime modules
		for key, mod_definition in self.modules.items():
			module = Template_Module(mod_definition.path)
			runtime_modules[key] = module

		for key, mod_definition in self.modules.items():
			module = runtime_modules[key]
			for alias, py_module in mod_definition.py_imports.items():
				setattr(module, alias, importlib.import_module(py_module))

			for name, template_import in mod_definition.template_imports.items():
				setattr(module, name, runtime_modules[template_import])

			for name, exp in mod_definition.variables.items():
				exp_eval = eval(exp, module.__dict__, {})
				setattr(module, name, exp_eval)

			for name, func_definition in mod_definition.templates.items():
				func  = Template_Function()
				func.text = func_definition.text
				func.code = compile(func_definition.code, "<string>", "exec")
				func.params = func_definition.params
				func.module = module
				func.source_lines = func_definition.source_lines
				setattr(module, name, func)


		self.modules = runtime_modules


