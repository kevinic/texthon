# Copyright 2013 Kevin Lin
# Licensed under the Apache License, Version 2.0

from texthon.parser import Parser
import texthon.base as base
import texthon.utils
import io
import os
import sys
import importlib
import traceback
import copy
import collections
import linecache

class Exec_Exception(Exception):
	def __init__(self, func, msg):
		self.path = func.path
		self.name = func.name
		self.line = func.definition_line
		self.msg = msg

	def __str__(self):
		return "{}:{}({}) has thrown an exception: {}".format(
			self.path, self.name, self.line, self.msg)

class Template_Function:
	""" Compiled template function object.  Returns a string that's the result
	of the template evaluation
	
	The callable object takes a variable number of arguments, but it will
	perform additional checks against the declared parameters of the
	template function definition.
	"""

	def __init__(self):
		self.name = ""
		self.text = []
		self.code = None
		self.varargs = False
		self.params = []
		self.module = None
		self.definition_line = 0
		self.path = ""
		self.source_lines = []

	def _print_exception(self, e):
		exc_type, exc_value, exc_traceback = sys.exc_info()

		def trans(frame):
			path = self.path
			if frame[0] == path:
				line = self.source_lines[frame[1] - 1]
				return path, line, "template", linecache.getline(path, line)
			else:
				return frame
			return frame

		# skip the exec frame
		tb = map(trans, traceback.extract_tb(exc_traceback)[1:])

		sys.stderr.write("Traceback with template source lines:\n")
		msg = traceback.format_list(tb)
		sys.stderr.write("".join(msg))

		sys.stderr.write("------\n")

		msg = traceback.format_exception_only(type(e), e)
		sys.stderr.write("".join(msg))

		sys.stderr.write("\n")

	def rebind(self, module):
		result = copy.copy(self)
		result.module = module
		return result

	def __call__(self, *args, **kwargs):
		output = base.StringIO()

		local_vars = {
			"_module" : self.module,
			"_textdb" : self.text,
			"_output" : output,
		}
			
		# bind arguments
		if not self.varargs:
			arg_count = len(args)
			arg_index = 0
			for param in self.params:
				if arg_index < arg_count:
					local_vars[param] = args[arg_index]
					arg_index += 1
					if param in kwargs:
						raise Exec_Exception(self, "template param {} already bound".format(param))
				else:
					if param in kwargs:
						local_vars[param] = kwargs[param]
					else:
						raise Exec_Exception(self, "unbound template param {}".format(param))

			if arg_index < arg_count:
				raise Exec_Exception(self, "too many arguments in template call")
		else:
			local_vars["_args"] = args
			local_vars["_kwargs"] = kwargs

		exception = None

		try:
			exec(self.code, self.module.__dict__, local_vars)
		except Exception as e:
			self._print_exception(e)
			exception = e

		if exception:
			raise Exec_Exception(self, "execution aborted")

		return output.getvalue()

class Template_Module:
	""" Provides access to template functions as attributes.  It's also a
	callable object that returns a shallow copy of itself on return.

	Call this object with a list of modules to create mixins.
	"""
	def __init__(self):
		self._base = []

	def __call__(self, *args):
		instance = copy.copy(self)
		instance._base.extend(args)

		# rebind all template functions
		functions = {}
		for name, attr in instance.__dict__.items():
			if isinstance(attr, Template_Function):
				functions[name] = attr.rebind(instance)

		instance.__dict__.update(functions)
		return instance

	def __getattr__(self, name):
		if "_base" not in self.__dict__:
			raise AttributeError("")

		visit = collections.deque(self._base)
		count = 0
		while visit:
			current = visit.popleft()
			visit.extendleft(current._base)
			if name in current.__dict__:
				return current.__dict__[name]

			count += 1
			# sanity check for loops in the hierarchy
			if count > 100:
				msg = "Failed to lookup attribute {} in template module: possible loop in base chain".format(
					name)
				raise AttributeError(msg)

		msg = "Attribute {} not found in template module".format(name)
		raise AttributeError(msg)

class Engine:
	""" Primary entrance for the Texthon library.  This provides methods
	to load, compile, and evaluate templates.

	Use the ``modules`` attribute (dict) to locate compiled or parsed modules.
	"""
	def __init__(self):
		self.modules = {}
		self.paths = []
		self.verbose = False

	def trace(self, text):
		if self.verbose:
			print(text)

	def add_includes(self, includes):
		""" Add a list of include paths to resolve load directives with. """
		self.paths.extend(includes)

	def set_verbose(self, verbose):
		""" Set to true for additional debug output. """
		self.verbose = verbose

	# current is the 'current' directory.  first choice to resolve
	# relative paths
	def _resolve_path(self, path, current):
		resolved_path = path

		if not os.path.isabs(path):
			paths = []
			if current:
				paths.append(current)
			paths.extend(self.paths)
			
			for prefix in paths:
				joined = os.path.join(prefix, path)
				if os.path.exists(joined):
					resolved_path = joined
					break
	
		return resolved_path

	def load_text(self, text, name, current = "", parser = Parser()):
		""" load_text(self, text, name, parser = Parser())
		Loads a template module defined in a string.

		:param text: the definition string
		:param name: path identifier for the module
		:param current: the current directory (used to resolve load directives)
		:param parser: the template parser to use

		:rtype: the module definition
		"""
		return self.load_module(base.StringIO(text), name, current, parser)

	def load_file(self, path, parser = Parser()):
		""" load_file(self, path, parser = Parser())
		Loads a template module defined in a file.

		:param path: path to the file
		:param parser: the template parser to use

		:rtype: the module definition
		"""
		path = os.path.abspath(path) #normalize the path
		tpl = open(path)
		module = self.load_module(tpl, path, os.path.dirname(path), parser)
		tpl.close()
		return module

	def load_module(self, input_stream, path, current, parser):
		""" load_module(self, text, name, parser = Parser())
		Loads a template module defined from an input stream

		:param input_stream: the stream to read from
		:param path: path identifier for the module
		:param current: the current directory (used to resolve load directives)
		:param parser: the template parser to use

		:rtype: the module definition
		"""
		module = self.modules.get(path, None)
		if module:
			self.trace("Modules {} is already loaded", path)
			return module

		self.trace("Loading module {}".format(path))

		module = parser.process_module(input_stream, path)
		module.path = path
		self.modules[path] = module

		fixed_loads = []

		# also load any module that this module refers to
		for load in module.template_loads:
			load_current = current
			if load.abs:
				load_current = ""

			load_parser = Parser(load.directive_token, load.placeholder)
			path = self._resolve_path(load.path, load_current)
			imported = self.load_file(path, load_parser)

			#update with canonical path
			fixed = copy.copy(load)
			fixed.path = imported.path

			fixed_loads.append(fixed)

		module.template_loads = fixed_loads
		return module

	def make(self):
		""" Compile all loaded modules.

		After the function is called, the entire ``modules`` dictionary is
		replaced with callable modules.
		"""
		runtime_modules = {}

		# create runtime modules
		for key, mod_definition in self.modules.items():
			module = Template_Module()
			runtime_modules[key] = module

		for key, mod_definition in self.modules.items():
			module = runtime_modules[key]
			#auto-import texthon utilities
			setattr(module, "_utils", texthon.utils)

			for alias, py_module in mod_definition.py_imports.items():
				setattr(module, alias, importlib.import_module(py_module))

			for load in mod_definition.template_loads:
				ref = runtime_modules[load.path]
				setattr(module, load.alias, ref)

			for name, exp in mod_definition.variables.items():
				exp_eval = eval(exp, module.__dict__, {})
				setattr(module, name, exp_eval)

			for name, func_definition in mod_definition.templates.items():
				func = Template_Function()
				func.name = name
				func.text = func_definition.text
				func.varargs = func_definition.varargs
				func.params = func_definition.params
				func.module = module
				func.definition_line = func_definition.definition_line
				func.path = mod_definition.path
				func.source_lines = func_definition.source_lines

				# compile with error translation
				try:
					func.code = compile(func_definition.code, func.path, "exec")
				except SyntaxError as e:
					e.lineno = func.source_lines[e.lineno - 1]
					raise e

				setattr(module, name, func)


		self.modules = runtime_modules


