from distutils.core import setup

setup(
    name='htmlr',
    version='0.1.0',
    author='Scott Hamilton',
    author_email='mcleopold@gmail.com',
    packages=['htmlr',
              'skills.testsuite'
    ],
    url='http://github.com/McLeopold/PythonHtmlr/',
    license="BSD",
    description='DSL to generate HTML with Python',
    long_description=open('README.rst').read(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
