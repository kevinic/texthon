from distutils.core import setup

with open('README.rst') as file:
	long_description = file.read()

setup(name='Texthon',
	version='0.8',
	description='Simple template engine - half text, half Python',
	long_description = long_description,
	author='Kevin Lin',
	author_email='kevin@chipsforbrain.org',
	packages=['texthon'],
	scripts=['scripts/texthon', 'scripts/texthon.cmd'],
	url='http://texthon.chipsforbrain.org',
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: Apache Software License",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.3",
		"Topic :: Software Development :: Code Generators",
		"Topic :: Text Processing",
		]
	)
