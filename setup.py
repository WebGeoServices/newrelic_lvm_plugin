"""
Newrelic LVM Plugin
-------------
Plugin to monitor LVM Disk space left on NewRelic
"""
from setuptools import setup

setup(
    name='nr_lvm_plugin',
    version='0.1.2',
    url='https://github.com/WebGeoServices/newrelic_lvm_plugin',
    license='MIT',
    author='WebGeoServices',
    author_email='operation@webgeoservices.com',
    description='Plugin to monitor LVM Disk space left on NewRelic',
    long_description=__doc__,
    scripts = ["nrlvmd.py"],
    install_requires=[
        'daemonize<=2.4.7',
        'requests<=2.13.0'
    ],
    download_url = 'https://github.com/WebGeoServices/newrelic_lvm_plugin/tarball/0.1',
    keywords = ['newrelic', 'LVM', 'Thinpool'],
    classifiers = [],
)