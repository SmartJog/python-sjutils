#! /usr/bin/python

##
## Login : <lcorbes@smartjog.com>
## Started on  Tue Nov  7 14:24:30 2006 Laurent Corbes
##
## $Rev::                                           $:  Revision of last commit
## $Author::                                        $:  Author of last commit
## $Date::                                          $:  Date of last commit

from distutils.core import setup


setup (
    name='python-sjutils',
    version='1.11.0~dev',
    description='SmartJog sjutils',
    long_description='several Python utils for SmartJog tools',

    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='',

    author='Romain DEGEZ and contributors',
    author_email='romain.degez@smartjog.com',

    url='http://www.smartjog.com/',
    license='Proprietary',

    packages=['sjutils'],
)
