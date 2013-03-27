.. title:: Documentation

Documentation
**********************************

.. contents::

Overview
===================================

Texthon compiles a template file into a template module.  Each template
module contains one or more template functions.

During the parsing stage, a template file is processed line by line, where each
line may be a directive or text.  Text lines may contain placeholders that will
be replaced by evaluated Python expressions.

Once compiled, a template function may be called with corresponding parameters.
The result of the call is a Python string. 

This snippet demonstrates all the stages::

    import texthon
    engine = texthon.Engine()

    # parse and store the parsed module
    module = engine.load_file("template.txt")

    # Store the path so we can find the compiled module later.  
    path = module.path

    # compile all modules
    engine.make() 

    # call the template function named 'main'
    print(engine.modules[path].main())

.. _cmd_script:

Command Line Script
=====================

A command line script is available to evaluate template files without having
to write your own Python code.

Invoke ``texthon --help`` for documentation on the script parameters.

.. _test_samples:

Samples
===========

The tests directory contains sample templates.  They are:

    * `helloworld <http://todo>`_ - a minimal example
    * `basic <http://todo>`_ - shows basic directive use and template module loads
    * `html <http://todo>`_ - shows the use of template mixins and parser parameters

Directives
============

.. highlight:: none

.. productionlist::
    directive: dir_prefix dir_command dir_statement
    dir_command: "`* <comment_directive>`" | "!" | "{" | "}" | dir_keyword
    dir_keyword: "load" | "import" | "attribute" | "template" | "end"

Directives are Texthon control commands and do not affect the output text
directly. A directive is issued on its own line, beginning with the directive
prefix token. The rest of the documentation assumes '#' is the prefix.

Prepend '\' to escape the token.  Escapes are only processed at the beginning
of the line.

Directives operate either in the module scope or the function scope.  Only
function scope directives should be issued between #template and #end template
lines.

.. tip::

    There may be arbitrary amount of whitespace between the prefix and the command.
    In addition, the parser allows for extra characters after the directive for
    most of the commands, so you can do::

        <!--# template name -->

    In the example above, the prefix is "<!--#", and anything after "name" is
    ignored, so you can close out the line with an xml comment end.

    Since the parser does not handle execution statements itself, remember to add a
    '#' if you want to do the same trick::

        <!--#! print("foo") #-->

.. _comment_directive:

Comment
-----------

Module and function scope::

    #* <comment>

Comments are ignored at the module scope, and emitted as Python #
comments at the function scope to aid debugging.

Example::

    #* just a comment left by the author

.. _import_directive:

Import
-----------

Module scope::

    #import <module> as <alias>

Import a Python module under <alias>.  The alias is required.  Once imported,
the alias will be available for all definitions in the module.

Example::

    #import string as str
    #import os.path as path

.. _load_directive:

Load
------------

Module scope::

    #load <path> as <alias> [(attributes)]

Load another template module in the file specified by <alias>.  <path> is
resolved relative to the directory of the current file and the list of
include paths added by ``engine.add_includes``.

The attributes indicate how the parser will load and process the file.  The
following attributes are available:
	
    * ``abs`` - do not use the path of the current file to resolve <path>.  Off
      by default.
    * ``directive_token = <token>`` - load the file with <token> as the
      directive token.  Same as the current file by default.
    * ``placeholder = <char>`` - use <char> as the character prefix for
      placeholders.  Same as the current file by default.

Example::

    #load "lib/file.tmpl" as lib
    #load "lib/file.tmpl.html" as html_lib (directive_token = <!--)
    #load "lib/file.tmpl" as lib (abs)

.. _attribute_directive:

Attribute
----------------

Module scope::

    #attribute <name> <expression>

Declare a module level variable <name> and assign the result of <expression>.

Within the same module, an attribute can be read by a template function without
any qualification. To assign a new value, however, you must go through the
builtin variable ``_module``::

    #! temp_name = name # ok, if name has been defined as an attribute
    #! _module.name = "new name" # assignment requires _module access

:ref:`More details <template_execution>`.

Example::

    #attribute author = "anonymous"

.. _template_directive:

Template Function
------------------

Module scope::

    #template <name>[(parameters)]
    #end template

Define a template function within the current module.  Anything between
``#template`` and ``#end template`` are evaluated in function scope.

An optional list of identifiers can be provided as parameters.  Without the
parameter list, the template is considered to be a variable argument function.
The arguments will then be available as builtins ``_args`` and ``_kwargs``.
:ref:`More details <template_execution>`.

Example::

    #template join_tokens
    joined: ${", ".join(args)}
    #end template

    #template header(author, title)
    $title by author $author
    #end template

.. _single_exec_directive:

Single Statement
-----------------

Function scope::

    #! <python_statement>

The entire <python_statement> is copied over to the generated template function
code (with indentation stripped).  Write the statement as if it were inside a
normal Python function.

Example::

    #! temp = "temporary value"
    #! break
    #! continue
    #! _output.write(another_template())

For builtin variables available to the execution statement, refer
:ref:`here <template_execution>`.

.. _compound_exec_directive:

Compound Statement
-------------------

Function scope::

    #{ <python_compound_statement>
    #}

Compound statements are useful for Python control logic such as ``if``, 
``for``, and ``while``.  Text lines and other execution statements between
``#{`` and ``#}`` are considered part of the compound block.

Example::

    #{ for i in range(0, 5):
    line $i
    #}

    #{  if setting:
    setting is true!
    #}
    #{  else:
    setting is false!
    #}

Text Line
====================

Text lines are appended to the evaluation output after placeholder
substitution is performed.  All placeholders begin with the placeholder
character (by default '$').  Placeholders can be escaped by repeating the
character twice ("$$").

.. tip::

    Text lines are ignored at the module scope.  Take advantage of that to
    'trick' editors into highlighting your template file correctly.

    For example, consider this c++ template file, with "//#" as the directive
    prefix, and '%' as the placeholder:

     .. code-block:: c
        
        void initialize(int* values)
        {
        //# template set_values(count)
        //#     {for i in (0, count):
            values[%i] = %i
        //#     }
        //# end template
        }

    In the template above, only value assignment is part of the generated text.
    The function signature and brackets are ignored, but they tell your editor
    how to highlight the entire file, and give context to your template.


Identifier Placeholder
-----------------------

::

    $<identifier>

For simple identifier substitution, just prepend the placeholder character to
the name.

Example::

    $author is responsible for this document

Expression Placeholder
-----------------------

::

    ${<python_expression>}
    
For complex substituion, surround a Python expression with brackets.
<python_expression> will be evaluated using Python ``eval``, and the result
is used for the substitution.

'\' can be used within the expression to escape the ending bracket '}',

Example::

    the sum of the values is ${a + b}
    lookup result: ${values[key]}

Slurp Placeholder
---------------------

::

    $<

A special place holder, ``$<``, is used to slurp whatever text that comes
between it and the next line.  It's useful for eating up extraneous newlines.

For instance::

	this is the end of the file
	#end template
    
will generate a newline after "file" since it's considered part of the
textline, whereas::

    this is the end of the file$<
    #end template

will ensure that no newline occurrs at the end of the output.

.. _template_execution:

Template Execution
====================

When a template function executes, it has a set of variables defined on entry.
Here they are in definition order:

    * :ref:`python import <import_directive>` aliases
    * :ref:`template load <load_directive>` aliases
    * module :ref:`attributes <attribute_directive>`
    * other :ref:`template function <template_directive>` names within the same module
    * parameters to the :ref:`template function <template_directive>`
    * builtin locals

The builtin locals are:
    * ``_module`` - the module containing the executing function
    * ``_output`` - an output stream that goes directly towards the generated
      string.  Write anything you like to the stream and it'll be added to the
      function's return.
    * ``_args`` - positional arguments for variable argument functions. Use like Python \*args.
    * ``_kwargs`` - keyword arguments for variable argument functions. Use like Python \**kwargs.
    * ``_textdb`` - reserved for Texthon

.. _template_modules:

Template Modules
===================

Template functions in the same file are grouped into a template module.  After
a :ref:`load <load_directive>`, you can access a module's functions through the
alias::

	#load "lib/lib.tmpl" as lib
	${lib.template_func()}

All paths that resolve to the same file share the same module.  If you modify a
module attribute, it'll affect all template code that has the same module
loaded.

.. _module_mixins:

Modules can be combined to form new modules.  This usage is called mixins,
which is Texthon's solution to template polymorphism::

	#load "mod1.tmpl" as mod1
	#load "mod2.tmpl" as mod2
	#load "mod2.tmpl" as mod3
	#!new_module = mod1(mod2, mod3)
	${new_module.attr}

The example above creates a new module that contains all definitions and
aliases within ``mod1``, ``mod2``, and ``mod3``.  ``new_module`` is formed by
first cloning ``mod1`` with a shallow copy, and then inserting ``mod2`` and
``mod3`` as mixins. The final lookup for "attr" is valid as long as "attr" is
available in any of the three modules.


See the :ref:`html sample <test_samples>` for example usage.

