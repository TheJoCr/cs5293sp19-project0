from setuptools import setup, find_packages

setup(
	name='project0',
	version='1.0',
	author='Jordan Crawford',
	authour_email='jordan.crawford@ou.edu',
	packages=find_packages(exclude=('tests', 'docs')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)
