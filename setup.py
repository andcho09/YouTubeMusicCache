from setuptools import setup

setup(
	name='youtubemusiccache',
	version='0.1.0',
	author='Andrew Cho',
	author_email='andcho09@gmail.com',
	packages=['youtubemusiccache'],
	#scripts=['bin/script1','bin/script2'],
	#url='',
	#license='LICENSE.txt',
	description='Cache and helper functions for ytmusicapi',
	long_description=open('README.md').read(),
	install_requires=[
		"fuzzywuzzy",
		"ytmusicapi",
	]
)