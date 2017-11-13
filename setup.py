from setuptools import setup, find_packages

version = '0.1'

setup(
	name='ckanext-googleanalytics',
	version=version,
	description="Add GA tracking and reporting to CKAN instance",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Seb Bacon',
	author_email='seb.bacon@gmail.com',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.googleanalytics'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[

	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	googleanalytics=ckanext.googleanalytics.plugin:GoogleAnalyticsPlugin

        [paste.paster_command]
        loadanalytics = ckanext.googleanalytics.commands:LoadAnalytics
        initdb = ckanext.googleanalytics.commands:InitDB
	""",
)
