#! /usr/bin/env python
# coding=utf-8
# filename=build_runtime.py

import os
import re
import sys
import shutil
import platform
import subprocess

if platform.system() == 'Windows':
    import _winreg


def checkParams():
    """Custom and check param list.
    """
    from optparse import OptionParser
    # set the parser to parse input params
    # the correspond variable name of "-x, --xxx" is parser.xxx

    if platform.system() == "Darwin":
        parser = OptionParser(
            usage="Usage: %prog -p <android|ios|mac>\n\
            Sample: %prog -p ios"
        )
        parser.add_option(
            "-p",
            "--platform",
            metavar="PLATFORM",
            type="choice",
            choices=["android", "ios", "mac"],
            help="Set build runtime's platform"
        )
    elif platform.system() == "Windows":
        parser = OptionParser(
            usage="Usage: %prog -p <win32|android>\n\
            Sample: %prog -p win32"
        )
        parser.add_option(
            "-p",
            "--platform",
            metavar="PLATFORM",
            type="choice",
            choices=["win32", "android"],
            help="Set build runtime's platform"
        )

    parser.add_option(
        "-u",
        "--pure",
        dest="pure",
        action="store_true",
        help="parameter for copy resource"
    )

    parser.add_option(
        "-d",
        "--dest",
        metavar="PROJECT_PATH",
        help="Set project path"
    )

    #android's parameter
    parser.add_option(
        "-v",
        "--version",
        metavar="SDK_VERSION",
        help="Set android sdk version"
    )

    #ios's parameter
    parser.add_option(
        "-t",
        "--target",
        metavar="TARGET",
        help="Set target"
    )

    # parse the params
    (opts, args) = parser.parse_args()

    if not opts.platform:
        parser.error("-p or --platform is not specified")

    if opts.platform == "android":
        if not opts.version:
            parser.error("-v or --version is not specified")
        return opts

    if opts.platform == "ios":
        if not opts.target:
            parser.error("-t or --target is not specified")
        return opts

    #return opts.platform, opts.pure


class BuildRuntime:
    
    def __init__(self, parameters):
        self.projectPath = parameters.dest
        self.projectName = None
        self.runtimePlatform = parameters.platform
        self.pure = parameters.pure

        scriptPath = os.path.abspath(os.path.dirname(__file__))
        if self.runtimePlatform == 'win32':
            self.projectPath = os.path.join(scriptPath, "proj.win32")
        elif self.runtimePlatform == 'android':
            self.version = parameters.version
            if "android-" in self.version:
                self.version = self.version[self.version.find('-')+1:]
            if self.projectPath is None:
                self.projectPath = os.path.join(scriptPath, "proj.android")
        elif self.runtimePlatform == 'ios':
            self.target = parameters.target
            if self.projectPath is None:
                self.projectPath = os.path.join(scriptPath, "proj.ios_mac")
        elif self.runtimePlatform == 'mac':
            self.target = parameters.target
            if self.projectPath is None:
                self.projectPath = os.path.join(scriptPath, "proj.ios_mac")

    def buildRuntime(self):
        if self.runtimePlatform == 'win32':
            self.win32Runtime()
        elif self.runtimePlatform == 'android':
            self.androidRuntime()
        if self.runtimePlatform == 'ios':
            self.iosRuntime()
        if self.runtimePlatform == 'mac':
            self.macRuntime()
            
    def macRuntime(self):
        commands = [
            "xcodebuild",
            "-version"
        ]
        child = subprocess.Popen(commands, stdout=subprocess.PIPE)

        xcode = None
        version = None
        for line in child.stdout:
            if 'Xcode' in line:
                xcode, version = str.split(line, ' ')

        child.wait()

        if xcode is None:
            print ("Xcode wasn't installed")
            return False

        if version <= '5':
            print ("Update xcode please")
            return False

        res = self.checkFileByExtention(".xcodeproj")
        if not res:
            print ("Can't find the \".xcodeproj\" file")
            return False

        projectPath = os.path.join(self.projectPath, self.projectName)
        pbxprojectPath = os.path.join(projectPath, "project.pbxproj")
        print(pbxprojectPath)

        f = file(pbxprojectPath)
        contents = f.read()

        section = re.search(
            r"Begin PBXProject section.*End PBXProject section",
            contents,
            re.S
        )

        if section is None:
            print ("Can't find Mac target")
            return False

        targets = re.search(r"targets = (.*);", section.group(), re.S)
        if targets is None:
            print ("Can't find Mac target")
            return False

        targetName = None
        names = re.split("\*", targets.group())
        for name in names:
            if "Mac" in name:
                targetName = str.strip(name)

        if targetName is None:
            print ("Can't find Mac target")
            return False

        name, ext = os.path.splitext(self.projectName)
        macFolder = os.path.join(self.projectPath, "..", "..", "runtime", name, "mac")
        if os.path.isdir(macFolder):
            shutil.rmtree(macFolder)

        commands = [
            "xcodebuild",
            "-project",
            projectPath,
            "-configuration",
            "Debug",
            "-target",
            targetName,
            "CONFIGURATION_BUILD_DIR=%s" % (macFolder)
        ]
        child = subprocess.Popen(commands, stdout=subprocess.PIPE)
        for line in child.stdout:
            print (line)

        child.wait()

        filelist = os.listdir(macFolder)
        for filename in filelist:
            name, extention = os.path.splitext(filename)
            if extention == '.a':
                filename = os.path.join(macFolder, filename)
                os.remove(filename)
            if extention == '.app':
                filename = os.path.join(macFolder, filename)
                if ' ' in name:
                    newname = os.path.join(macFolder, name[:name.find(' ')]+extention)
                    os.rename(filename, newname)
    
    def iosRuntime(self):
        commands = [
            "xcodebuild",
            "-version"
        ]
        child = subprocess.Popen(commands, stdout=subprocess.PIPE)

        xcode = None
        version = None
        for line in child.stdout:
            if 'Xcode' in line:
                xcode, version = str.split(line, ' ')

        child.wait()

        if xcode is None:
            print ("Xcode wasn't installed")
            return False

        if version <= '5':
            print ("Update xcode please")
            return False

        res = self.checkFileByExtention(".xcodeproj")
        if not res:
            print ("Can't find the \".xcodeproj\" file")
            return False

        projectPath = os.path.join(self.projectPath, self.projectName)
        pbxprojectPath = os.path.join(projectPath, "project.pbxproj")
        print(pbxprojectPath)

        f = file(pbxprojectPath)
        contents = f.read()

        section = re.search(r"Begin PBXProject section.*End PBXProject section", contents, re.S)

        if section is None:
            print ("Can't find iOS target")
            return False

        targets = re.search(r"targets = (.*);", section.group(), re.S)
        if targets is None:
            print ("Can't find iOS target")
            return False

        targetName = None
        names = re.split("\*", targets.group())
        for name in names:
            if "iOS" in name:
                targetName = str.strip(name)

        if targetName is None:
            print ("Can't find iOS target")
            return False

        name, ext = os.path.splitext(self.projectName)
        iosFolder = os.path.join(self.projectPath, "..", "..", "runtime", name, "ios")
        if os.path.isdir(iosFolder):
            filelist = os.listdir(iosFolder)
            for filename in filelist:
                if ".app" in filename:
                    f = os.path.join(iosFolder, filename)
                    shutil.rmtree(f)

        commands = [
            "xcodebuild",
            "-project",
            projectPath,
            "-configuration",
            "Debug",
            "-target",
            targetName,
            "-sdk",
            "iphonesimulator",
            "CONFIGURATION_BUILD_DIR=%s" % (iosFolder)
        ]
        child = subprocess.Popen(commands, stdout=subprocess.PIPE)
        for line in child.stdout:
            print (line)

        child.wait()

        filelist = os.listdir(iosFolder)

        for filename in filelist:
            name, extention = os.path.splitext(filename)
            if extention == '.a':
                filename = os.path.join(iosFolder, filename)
                os.remove(filename)
            if extention == '.app':
                filename = os.path.join(iosFolder, filename)
                newname = os.path.join(iosFolder, name[:name.find(' ')]+extention)
                os.rename(filename, newname)

    def androidRuntime(self):
        try:
            SDK_ROOT = os.environ['ANDROID_SDK_ROOT']
        except Exception:
            print ("ANDROID_SDK_ROOT not defined.\
             Please define ANDROID_SDK_ROOT in your environment")
            return False
        try:
            NDK_ROOT = os.environ['NDK_ROOT']
        except Exception:
            print ("NDK_ROOT not defined.\
             Please define NDK_ROOT in your environment")
            return False
        platformsPath = os.path.join(SDK_ROOT,"platforms")
        if not os.path.isdir(platformsPath):
            print ("Can't find android platforms")
            return False
        platforms = os.listdir(platformsPath)
        versions = []
        exsit = False
        for p in platforms:
            if "android-" in p:
                if self.version in p:
                    exsit = True
                ver = p[p.find('-')+1:]
                versions.append(ver)
        if not exsit:
            print ("Unable to find the sdk version.")
            return False
        if float(self.version) <= 10.0:
            print ("The android sdk version you designated is too old.\
             Please upgrade to the latest version or designate a new android sdk version")
            
        maxVersion = max(map(float, versions))
        if maxVersion <= 10.0:
            print ("Update android sdk")
            return False
        
        buildNative = os.path.join(self.projectPath, "build_native.py")
        if not os.path.isdir(self.projectPath) or not os.path.isfile(buildNative):
            print ("Can't find the build_native.py")
            return False

        sys.path.append(self.projectPath)
        from build_native import build
        build(None, self.version, None, self.pure)
        
    def win32Runtime(self):
        try:
            vs = _winreg.OpenKey(
                _winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\VisualStudio"
            )

            msbuild = _winreg.OpenKey(
                _winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\MSBuild\ToolsVersions"
            )

        except WindowsError:
            print ("Visual Studio wasn't installed")
            return False

        vsPath = None
        i = 0
        try:
            while True:
                version = _winreg.EnumKey(vs, i)
                try:
                    if float(version) >= 11.0:
                        key = _winreg.OpenKey(vs, r"SxS\VS7")
                        vsPath,type = _winreg.QueryValueEx(key, version)
                except:
                    pass
                i += 1
        except WindowsError:
            pass

        if vsPath is None:
            print("Can't find the Visual Studio's path in the regedit")
            return False

        msbuildPath = None
        i = 0
        try:
            while True:
                version = _winreg.EnumKey(msbuild,i)
                try:
                    if float(version) >= 4.0:
                        key = _winreg.OpenKey(msbuild, version)
                        msbuildPath, type = _winreg.QueryValueEx(
                            key, 
                            "MSBuildToolsPath"
                        )
                except:
                    pass
                i += 1
        except WindowsError:
            pass

        if msbuildPath is None:
            print ("Can't find the MSBuildTools' path in the regedit")
            return False

        res = self.checkFileByExtention(".sln")
        if not res:
            print ("Can't find the \".sln\" file")
            return False

        msbuildPath = os.path.join(msbuildPath, "MSBuild.exe")
        projectPath = os.path.join(self.projectPath, self.projectName)
        commands = [
            msbuildPath,
            projectPath,
            "/maxcpucount:4",
            "/t:build",
            "/p:configuration=Debug"
        ]

        child = subprocess.Popen(commands, stdout=subprocess.PIPE)
        for line in child.stdout:
            print (line)

        child.wait()

        return True
        
    def checkFileByExtention(self, ext, path=None):
        filelist = ""
        if path is None:
            filelist = os.listdir(self.projectPath)
        else:
            filelist = os.listdir(path)

        for file in filelist:
            name, extention = os.path.splitext(file)
            if extention == ext:
                self.projectName = file
                return True
        return False
                
if __name__ == '__main__':
    parameters = checkParams();
    buildRuntime = BuildRuntime(parameters)
    buildRuntime.buildRuntime()
