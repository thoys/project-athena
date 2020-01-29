import hifi_utils
import hifi_android
import hashlib
import os
import platform
import re
import shutil
import tempfile
import json
import xml.etree.ElementTree as ET
import functools

print = functools.partial(print, flush=True)

# Encapsulates the vcpkg system 
class QtDownloader:
    CMAKE_TEMPLATE = """
# this file auto-generated by hifi_qt.py
get_filename_component(QT_CMAKE_PREFIX_PATH "{}" ABSOLUTE CACHE)
get_filename_component(QT_CMAKE_PREFIX_PATH_UNCACHED "{}" ABSOLUTE)

# If the cached cmake toolchain path is different from the computed one, exit
if(NOT (QT_CMAKE_PREFIX_PATH_UNCACHED STREQUAL QT_CMAKE_PREFIX_PATH))
    message(FATAL_ERROR "QT_CMAKE_PREFIX_PATH has changed, please wipe the build directory and rerun cmake")
endif()
"""
    def __init__(self, args):
        self.args = args
        self.configFilePath = os.path.join(args.build_root, 'qt.cmake')
        self.version = '5.12.3'

        self.assets_url = self.readVar('EXTERNAL_BUILD_ASSETS')

        defaultBasePath = os.path.expanduser('~/hifi/qt')
        self.basePath = os.getenv('HIFI_QT_BASE', defaultBasePath)
        if (not os.path.isdir(self.basePath)):
            os.makedirs(self.basePath)
        self.path = os.path.join(self.basePath, self.version)
        self.fullPath = os.path.join(self.path, 'qt5-install')
        self.cmakePath = os.path.join(self.fullPath, 'lib/cmake')

        print("Using qt path {}".format(self.path))
        lockDir, lockName = os.path.split(self.path)
        lockName += '.lock'
        if not os.path.isdir(lockDir):
            os.makedirs(lockDir)

        self.lockFile = os.path.join(lockDir, lockName)

        # OS dependent information
        system = platform.system()

        if 'Windows' == system:
            self.qtUrl = self.assets_url + '/dependencies/vcpkg/qt5-install-5.12.3-windows3.tar.gz%3FversionId=5ADqP0M0j5ZfimUHrx4zJld6vYceHEsI'
        elif 'Darwin' == system:
            self.qtUrl = self.assets_url + '/dependencies/vcpkg/qt5-install-5.12.3-macos.tar.gz%3FversionId=bLAgnoJ8IMKpqv8NFDcAu8hsyQy3Rwwz'
        elif 'Linux' == system:
            if platform.linux_distribution()[1][:3] == '16.':
                self.qtUrl = self.assets_url + '/dependencies/vcpkg/qt5-install-5.12.3-ubuntu-16.04-with-symbols.tar.gz'
            elif platform.linux_distribution()[1][:3] == '18.':
                self.qtUrl = self.assets_url + '/dependencies/vcpkg/qt5-install-5.12.3-ubuntu-18.04.tar.gz'
            else:
                raise Exception('UNKNOWN LINUX VERSION!!!')
        else:
            raise Exception('UNKNOWN OPERATING SYSTEM!!!')

    def readVar(self, var):
        with open(os.path.join(self.args.build_root, '_env', var + ".txt")) as fp:
            return fp.read()

    def writeConfig(self):
        print("Writing cmake config to {}".format(self.configFilePath))
        # Write out the configuration for use by CMake
        cmakeConfig = QtDownloader.CMAKE_TEMPLATE.format(self.cmakePath, self.cmakePath).replace('\\', '/')
        with open(self.configFilePath, 'w') as f:
            f.write(cmakeConfig)

    def installQt(self):
        if not os.path.isdir(self.fullPath):
            print ('Downloading Qt from AWS')
            print('Extracting ' + self.qtUrl + ' to ' + self.path)
            hifi_utils.downloadAndExtract(self.qtUrl, self.path)
        else:
            print ('Qt has already been downloaded')
