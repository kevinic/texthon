import texthon.base as base
import shlex
import io

class Template_Definition:
	def __init__(self):
		self.text = []
		self.code = ""
		self.definition_line = 0
		self.source_lines = []
		self.varags = False
		self.params = []

	def dump(self):
		print("code: ")
		print(self.code)
		print("text: ")
		print(self.text)

class Template_Load:
	def __init__(self):
		self.alias = ""
		self.path = ""
		self.abs = False
		self.directive_token = ""
		self.placeholder = ""

class Module_Definition:
	""" A parsed template module. """

	def __init__(self):
		self.path = None
		self.py_imports = {}
		self.template_loads = []
		self.templates = {}
		self.variables = {}

	def dump(self):
		""" Dump detailed module information including generated function code"""
		print("Module : {}".format(self.path))
		print("python imports: " + repr(self.py_imports))
		print("template loads: " + repr(self.template_loads))
		print("attributes: " + repr(self.variables))
		print()
		for key, value in self.templates.items():
			print("Template: " + key)
			print()
			value.dump()

class Parse_Exception(Exception):
	def __init__(self, context, reason):
		self.title = context.title
		self.line = context.line
		self.reason = reason

	def __str__(self):
		return "Parse exception at {0}:{1} {2}".format(self.title, str(self.line), self.reason)

# only 1 type for now
scope_types = base.Simple_Enum("template")

class Parse_Scope:
	def __init__(self, scope):
		self.scope = scope

class Parse_Context:
	def __init__(self, title, module):
		self.module = module
		self.template = None
		self.title = title
		self.line = 1
		self.indent = 0
		self.textIndex = 0
		self.stack = list()
		self.require_pass = False

class Parser:
	""" The parser used to process template files.

	:param directive_token: the prefix that indicates the start of a directive line.
	:param sub_ch: the character that indicates the start of a placeholder
	"""
	def __init__(self,
			directive_token = "#",
			sub_ch = "$",
			):
		self.directive_token = directive_token
		self.placeholder = sub_ch

		self.keywords = {
			"import" : self.parse_import,
			"load" : self.parse_load,
			"attribute" : self.parse_attribute,
			"template" : self.parse_template,
			"end" : self.parse_end,
			}

		self.verbose = False

	def _print(self, context, text):
		print("{0}({1}): {2}".format(context.title, context.line, text))

	def trace(self, context, text):
		if self.verbose:
			self._print(context, text)

	def warning(self, context, text):
		self._print(context, "warning: {0}".format(text))

	def process_module(self, input_stream, title):
		module = Module_Definition()
		context = Parse_Context(title, module)
		for line in input_stream:
			self.parse_line(context, line)
			context.line += 1

		if context.stack:
			scope = context.stack[-1]
			self.warning(context, "missing end directive for {0}".format(
				scope_types.names[scope.scope]))

		return module

	def parse_line(self, context, line):
		cursor = 0
		token = ""
		if line.startswith(self.directive_token):
			cursor += len(self.directive_token)
			self.parse_directive(context, line, cursor)
			processed = True
		else:
			cursor, prefix = self.parse_escapestart(context, line, cursor)
			self.parse_text_line(context, prefix + line[cursor:])

	def _check_ch(self, ch, ch_class):
		for c in ch_class:
			if c == ch:
				return True

		return False

	def _check_word_ch(self, ch):
		return ch.isalnum() or ch == '_'

	def parse_space(self, context, line, cursor):
		limit = len(line)
		space = base.StringIO()
		while cursor < limit and line[cursor].isspace():
			space.write(line[cursor])
			cursor += 1

		return cursor, space.getvalue()

	def parse_escapestart(self, context, line, cursor):
		# process escape sequences (only at the begining)
		limit = len(line)
		escaped = base.StringIO()
		while cursor < len(line) - 1:
			if line[cursor] == '\\':
				escaped.write(line[cursor + 1])
				cursor += 2
			else:
				break
		return cursor, escaped.getvalue()

	def parse_identifier(self, context, line, cursor):
		token = base.StringIO()
		limit = len(line)
		# digit is not allowed in the first character
		if cursor < limit and line[cursor].isdigit():
			return cursor, ""

		while cursor < limit and self._check_word_ch(line[cursor]):
			token.write(line[cursor])
			cursor += 1

		return cursor, token.getvalue()

	def parse_literal(self, context, literal, line, cursor):	
		count = len(literal)
		if line[cursor:cursor + count] == literal:
			return cursor + count, literal
		return cursor, None

	def parse_close_quote(self, context, quote_ch, escape, line, cursor):
		token = base.StringIO()
		limit = len(line)
		saved = cursor

		complete = False
		while cursor < limit:
			ch = line[cursor]
			if self._check_ch(ch, escape) and cursor < limit - 1:
				token.write(line[cursor + 1])
				cursor += 2
			elif ch == quote_ch:
				complete = True
				cursor += 1
				break
			else:
				token.write(ch)
				cursor += 1

		if complete:
			return cursor, token.getvalue()
		else:
			raise Parse_Exception(context, "could not find end delimiter {}".format(quote_ch))


	def parse_quoted(self, context, quote, escape, line, cursor):
		if cursor < len(line) and self._check_ch(line[cursor], quote):
			quote_ch = line[cursor]
			cursor += 1
			return self.parse_close_quote(context, quote_ch, escape, line, cursor)

		return cursor, None

	def parse_paren(self, context, escape, line, cursor):
		if cursor < len(line) and line[cursor] == '(':
			cursor += 1
			return self.parse_close_quote(context, ')', escape, line, cursor)

		return cursor, None

	def parse_bracket(self, context, escape, line, cursor):
		if cursor < len(line) and line[cursor] == '{':
			cursor += 1
			return self.parse_close_quote(context, '}', escape, line, cursor)

		return cursor, None

	def parse_module_name(self, context, line, cursor):
		token = base.StringIO()
		limit = len(line)
		saved = cursor
		while cursor < limit:
			ch = line[cursor]
			if self._check_word_ch(ch) or ch == '.':
				token.write(ch)
				cursor += 1
			else:
				break

		return cursor, token.getvalue()

	def parse_exec(self, context, line, cursor):
		if context.template:
			symbol = line[cursor]
			cursor += 1
			arguments = line[cursor:].strip()
			self.trace(context, "exec directive,{0} {1}".format(symbol, arguments))

			if symbol == "!":
				self.emit_code(context, arguments)
			elif symbol == '{':
				self.emit_code(context, arguments)
				context.indent += 1
				context.require_pass = True
			elif symbol == '}':
				if context.indent <= 0:
					raise Parse_Exception(context, "mismatched end bracket")
				if context.require_pass:
					self.emit_code(context, "pass")
				context.indent -= 1
				self.emit_code(context, arguments)
			else:
				raise Parse_Exception(context, "unknown execution symbol {}".format(symbol))
		else:
			raise Parse_Exception(context, "execution statement outside of template definition is not allowed")
		
	def parse_directive(self, context, line, cursor):
		# consume optional space
		cursor, _ = self.parse_space(context, line, cursor)
		exec_ch = "!{}"
		if cursor == len(line):
			raise Parse_Exception(context, "malformed directive: {}".format(line))
	
		ch = line[cursor]
		if self._check_ch(ch, exec_ch):
			self.parse_exec(context, line, cursor)
		elif ch == "*":
			cursor += 1
			self.emit_comment(context, line[cursor:])
		else:
			cursor, keyword = self.parse_identifier(context, line, cursor)
			if keyword:
				func = self.keywords.get(keyword, None)
				if func:
					func(context, line, cursor)
				else:
					raise Parse_Exception(context, "unknown directive keyword: {}".format(keyword))
			else:
				raise Parse_Exception(context, "malformed directive: {}".format(line))

	def parse_literal_req(self, context, literal, line, cursor):
		cursor, _ = self.parse_space(context, line, cursor)
		cursor, lit = self.parse_literal(context, literal, line, cursor)
		if not lit:
			raise Parse_Exception(context, "expected literal {}".format(literal))

		return cursor, lit

	def parse_identifier_req(self, context, line, cursor):
		cursor, _ = self.parse_space(context, line, cursor)
		cursor, ident = self.parse_identifier(context, line, cursor)
		if not ident:
			raise Parse_Exception(context, "expected identifier")

		return cursor, ident

	def parse_import(self, context, line, cursor):
		if context.template:
			self.warning(context, "import directives are not expected inside template definitions")

		cursor, _ = self.parse_space(context, line, cursor)
		cursor, module = self.parse_module_name(context, line, cursor)
		if not module:
			raise Parse_Exception(context, "expected import module")

		cursor, _ = self.parse_literal_req(context, "as", line, cursor)
		cursor, alias = self.parse_identifier_req(context, line, cursor)

		self.trace(context, "import directive: {0} as {1}".format(module, alias))
		context.module.py_imports[alias] = module

	def parse_load(self, context, line, cursor):
		if context.template:
			self.warning(context, "load directives are not expected inside template definitions")

		cursor, _ = self.parse_space(context, line, cursor)
		cursor, path = self.parse_quoted(context, "'\"", "", line, cursor)
		if not path:
			raise Parse_Exception(context, "expected load path")

		cursor, _ = self.parse_literal_req(context, "as", line, cursor)
		cursor, alias = self.parse_identifier_req(context, line, cursor)

		cursor, _ = self.parse_space(context, line, cursor)
		params = []
		cursor, params_text = self.parse_paren(context, "", line, cursor)

		param_map = {
			"path" : path,
			"abs" : False,
			"directive_token" : self.directive_token,
			"placeholder" : self.placeholder
		}

		if params_text:
			# split by comma, preserve quotes
			comma_lex = shlex.shlex(params_text)
			comma_lex.whitespace_split = True
			comma_lex.whitespace = ","
			comma_lex.commenters = ""

			for param in comma_lex:
				# split by eq, strip quotes
				eq_lex = shlex.shlex(param, posix = True)
				eq_lex.whitespace_split = True
				eq_lex.whitespace += "="
				eq_lex.commenters = ""
				pair = list(eq_lex)
				key = pair[0].strip()
				value = True

				if len(pair) > 1:
					value = pair[1].strip()

				param_map[key] = value

		load = Template_Load()
		load.alias = alias
		load.path = param_map["path"]
		load.abs = param_map["abs"]
		load.directive_token = param_map["directive_token"]
		load.placeholder = param_map["placeholder"]

		self.trace(context,
			"load directive: {} as {}, abs({}), directive_token({}), placeholder({})".format(
			load.path, alias, load.abs, load.directive_token, load.placeholder))

		context.module.template_loads.append(load)

	def parse_attribute(self, context, line, cursor):
		if context.template:
			self.warning(context, "attribute directives are not expected inside template definitions")

		cursor, alias = self.parse_identifier_req(context, line, cursor)
		cursor, _ = self.parse_literal_req(context, "=", line, cursor)
		
		cursor, _ = self.parse_space(context, line, cursor)
		exp = line[cursor:]

		self.trace(context, "attribute directive: {0} = {1}".format(alias, exp))
		context.module.variables[alias] = exp

	def parse_template(self, context, line, cursor):
		if context.template:
			raise Parse_Exception(context, "can't nest template declarations")

		cursor, template_name = self.parse_identifier_req(context, line, cursor)

		cursor, _ = self.parse_space(context, line, cursor)
		params = []
		cusor, params_text = self.parse_paren(context, "", line, cursor)

		varargs = False

		if params_text:
			params = list(map(lambda s : s.strip(), params_text.split(',')))
		else:
			varargs = True

		# validate prameter list
		for param in params:
			matched, _ = self.parse_identifier(context, param, 0)
			if matched != len(param):
				raise Parse_Exception(context, "invalid parameter identifier {}".format(param))
			
		if getattr(context.module, template_name, None):
			raise Parse_Exception(context, "template {0} already defined".format(template_name))

		context.stack.append(Parse_Scope(scope_types.template))
		context.indent = 0
		context.textIndex = 0

		self.trace(context, "template directive: {0}".format(template_name))
		context.template = Template_Definition()
		context.template.varargs = varargs
		context.template.params = params
		# store debug information, assume we don't have code that spans lines
		context.template.definition_line = context.line
		context.module.templates[template_name] = context.template

	def parse_end(self, context, line, cursor):
		cursor, end_name = self.parse_identifier_req(context, line, cursor)

		if not context.stack:
			raise Parse_Exception(context, "end directive without matching opening")
		
		self.trace(context, "end directive: {0}".format(end_name))

		scope = context.stack[-1]
		expected_name = scope_types.names[scope.scope]

		if expected_name != end_name:
			raise Parse_Exception(context, "mismatched end directive, expected:{0}, actual:{1}".format(expected_name, end_name))

		if scope.scope == scope_types.template:
			if context.indent != 0:
				raise Parse_Exception(context, "missing end bracket")
			context.template = None

		context.stack.pop()

	def parse_text_line(self, context, line):
		#ignored while outside of template definition
		if not context.template:
			return

		cursor = 0
		limit = len(line)


		literal = base.StringIO()
		placeholder = None

		def flush():
			text = literal.getvalue()
			if text:
				self.emit_literal(context, text)
				literal.seek(0)
				literal.truncate()

		# do a first pass to search for line begin slurps
		temp = cursor
		while temp < limit:
			if self._check_ch(line[temp], self.placeholder):
				temp += 1
				if temp < limit and line[temp] == '<':
					cursor = temp + 1
					break
			temp += 1

		while cursor < limit:
			ch = line[cursor]
			if placeholder:
				if ch == placeholder:
					self.trace(context, "detected placeholder escape")
					literal.write(placeholder)
					cursor += 1
				elif ch == ">":
					self.trace(context, "detected line slurp")
					break;
				else:
					exp = None
					ident = None

					flush()
					cursor, exp = self.parse_bracket(context, "\\", line, cursor)

					if exp:
						self.emit_placeholder_exp(context, exp)
					else:
						cursor, ident = self.parse_identifier(context, line, cursor)

					if ident:
						self.emit_placeholder_exp(context, ident)

				placeholder = None
			else:
				if self._check_ch(ch, self.placeholder):
					placeholder = ch
				else:
					literal.write(ch)

				cursor += 1

		flush()

	def emit_comment(self, context, arguments):
		self.trace(context, "comment directive " + arguments)
		if context.template:
			self.emit_code(context, "#" + arguments.rstrip())
		else:
			# emit nothing, ignore the comment
			pass

	def emit_placeholder_exp(self, context, ident):
		self.trace(context, "detected placeholder ident {0}".format(ident))
		self.emit_code(context, "_output.write(str({0}))".format(ident))

	def emit_literal(self, context, text):
		context.template.text.append(text)
		self.emit_code(context, "_output.write(_textdb[" + str(context.textIndex) + "])")
		context.textIndex += 1 

	def emit_code(self, context, code):
		context.template.code += "\t" * context.indent
		context.template.code += code
		context.template.code += "\n"
		# store debug information, assume we don't have code that spans lines
		context.template.source_lines.append(context.line)
		context.require_pass = False

