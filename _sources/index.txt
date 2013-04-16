.. title:: Home

Introduction
********************

Texthon is a library that processes templates written in a mix of text and
Python.

.. toctree::
   :maxdepth: 1

   Documentation <documentation>
   API <api>

Getting Texthon
===================================

| `GitHub project page <https://github.com/kevinic/texthon/>`_
| `Python Package Index <https://pypi.python.org/pypi/Texthon>`_
| `Source tar.gz <https://github.com/kevinic/texthon/tarball/master>`_
| `Source zip <https://github.com/kevinic/texthon/zipball/master>`_

No prerequisites aside from `Python <http://www.python.org/>`_.  Texthon is
primarily developed using Python 3.3, but it's 2.7 compatible as well.

Installation
===================================

Run ``setup.py install`` to install the library and the command line
:ref:`script <cmd_script>` into your Python installation.  The scripts will be
placed under the "Scripts" subdirectory.

If only the library is desired, just copy the texthon subdirectory (where all
the py sources live) to a path under PYTHONPATH.

Design Philosophy
===================================
There are a lot of Python template engines, why did I make this one?

* **Texthon lets you embed Python code directly.**

  Unlike libraries that sandbox template execution, Texthon does as little
  interpretation as possible of control logic, preferring instead to pass
  statements straight to the Python interpreter.

  To ease the debugging of templates, Texthon translates tracebacks to their
  original template source lines.  The command line script can also dump
  generated Python code for inspection.

* **Texthon's implementation is small and portable.**

  No reliance on non-standard libraries.  The core implementation is just a
  couple of files that the user can copy and deploy at will. Texthon runs under
  both Python 2 and 3.

* **Texthon compiles templates into Python-like functions and organizes them into
  Python-like modules.**

  A template definition transforms into a callable function: it takes some
  parameters and returns a string.  Templates in a file are grouped together
  and accessed much like a Python module.

  One important feature is the support of :ref:`mixins <module_mixins>`.
  Users can mix template modules together to form a new module.  This allows
  the user to setup chains that's almost like template inheritance.

The syntax of Texthon is inspired by `Cheetah
<http://www.cheetahtemplate.org/>`_, which saved me from the unspeakable
agony of having to rely on C preprocessors for game object serialization code.
If only it wouldn't bug me about that stupid Namemapper extension all the time.

Example
===================================
Here's a simple template file, ``hello.tmpl.txt`` ::

    #template main(who, count)
    $who says: 
    #{for i in range(0, count):
        hello world!
    #}
    #end template

using the script ``texthon`` with the following parameters::

    texthon hello.tmpl.txt -P who=someone -P count=2

the following output is generated::

    someone says: 
        hello world!
        hello world!


For an example that's closer to a real-world scenario, `these templates <http://github.com/kevinic/texthon/tree/master/tests/cpp>`_
demonstrate the use of Texthon to write C++ object reflection code: a task that
would normally require tedious copy-and-pasting and/or C++ template/macro black
magic.
