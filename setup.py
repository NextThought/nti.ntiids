import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
    'console_scripts': [
    ],
}

TESTS_REQUIRE = [
    'nose',
    'nose-timer',
    'nose-pudb',
    'nose-progressive',
    'nose2[coverage_plugin]',
    'pyhamcrest',
    'nti.testing'
]

setup(
    name='nti.ntiids',
    version=VERSION,
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI ntiids",
    long_description=codecs.open('README.rst', encoding='utf-8').read(),
    license='Proprietary',
    keywords='NTIIDs',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	namespace_packages=['nti'],
    tests_require=TESTS_REQUIRE,
	install_requires=[
		'setuptools',
        'dolmen.builtins',
        'six',
        'zope.component',
        'zope.interface',
        'zope.i18nmessageid',
        'zope.security',
        'nti.common',
        'nti.nose_traceback_info',
        'nti.schema',
	],
    extras_require={
        'test': TESTS_REQUIRE,
    },
    dependency_links=[
        'git+https://github.com/NextThought/nti.schema.git#egg=nti.schema',
        'git+https://github.com/NextThought/nti.nose_traceback_info.git#egg=nti.nose_traceback_info'
    ],
	entry_points=entry_points
)
