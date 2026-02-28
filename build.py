#!/usr/bin/env python
"""
Virtual Pet Game - PGS4A Build Script
======================================
Build script for creating Android APK using Pygame Subset for Android (PGS4A).

Usage:
    python build.py

Requirements:
    - PGS4A (pip install pgsc4a or from https://github.com/renpytom/pgs4a)
    - Android SDK
    - Java JDK

For more information on PGS4A, visit:
    https://pygame.github.io/pgs4a/
"""

import os
import sys
import subprocess
import shutil

# Project configuration
PROJECT_NAME = "VirtualPetGame"
PACKAGE_NAME = "com.virtualpet.game"
VERSION = "1.0.0"

# Source files to include
SOURCE_DIRS = [
    ".",
]

# Assets to include
ASSETS_DIRS = [
    "assets",
]

# Required permissions for Android
PERMISSIONS = [
    "android.permission.INTERNET",
    "android.permission.ACCESS_NETWORK_STATE",
]


def check_pgs4a():
    """Check if PGS4A is installed."""
    try:
        import android
        return True
    except ImportError:
        return False


def init_pgs4a():
    """Initialize PGS4A if not already done."""
    if not check_pgs4a():
        print("PGS4A not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pgsa"])
        except:
            print("Failed to install PGS4A automatically.")
            print("Please install PGS4A manually:")
            print("  pip install pgsa4a")
            return False
    return True


def create_android_project():
    """Create Android project structure for PGS4A."""
    # PGS4A typically uses:
    # - project.properties
    # - local.properties
    # - AndroidManifest.xml
    # - build.py (this file)
    
    print("Creating Android project structure...")
    
    # Create AndroidManifest.xml
    manifest_content = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{PACKAGE_NAME}"
    android:versionCode="1"
    android:versionName="{VERSION}">
    
    <uses-sdk
        android:minSdkVersion="8"
        android:targetSdkVersion="15" />
    
    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    
    <!-- Features -->
    <uses-feature android:name="android.hardware.touchscreen" android:required="false" />
    <uses-feature android:name="android.hardware.touchscreen.multitouch" android:required="false" />
    
    <application
        android:label="{PROJECT_NAME}"
        android:icon="@drawable/icon"
        android:allowBackup="true"
        android:debuggable="true">
        
        <activity
            android:name="org.pgs4a.PGS4ALauncher"
            android:label="{PROJECT_NAME}"
            android:screenOrientation="portrait"
            android:configChanges="keyboard|keyboardHidden|orientation|screenLayout|uiMode">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
    </application>
    
</manifest>
"""
    
    with open("AndroidManifest.xml", "w") as f:
        f.write(manifest_content)
    
    print("AndroidManifest.xml created.")
    
    # Create project.properties
    project_props = """# Project target.
target=android-15
"""
    
    with open("project.properties", "w") as f:
        f.write(project_props)
    
    print("project.properties created.")


def build_apk():
    """Build the Android APK using PGS4A."""
    print("\n" + "="*50)
    print("Building Android APK...")
    print("="*50)
    
    # Check for PGS4A
    if not check_pgs4a():
        print("\nPGS4A is required but not installed.")
        print("\nAlternative: Use python-for-android instead:")
        print("  pip install python-for-android")
        print("  python -m buildozer init")
        print("  python -m buildozer apk")
        return False
    
    try:
        # Run PGS4A build
        # The actual command depends on PGS4A version
        import android.build
        
        print("Running PGS4A build...")
        android.build.build()
        
        print("\n" + "="*50)
        print("Build complete!")
        print("="*50)
        print(f"APK should be in: bin/{PACKAGE_NAME}-{VERSION}.apk")
        
        return True
        
    except Exception as e:
        print(f"Build failed: {e}")
        return False


def create_buildozer_spec():
    """Create buildozer.spec for python-for-android as an alternative."""
    spec_content = """[app]
# (str) Title of your application
title = Virtual Pet Game

# (str) Package name
package.name = virtualpetgame

# (str) Package domain (needed for android/ios packages)
package.domain = com.virtualpet

# (str) Version of application
version = 1.0.0

# (list) Application requirements
requirements = pygame,pygame-sdl2,requests

# (android specific) 
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (str) Presplash filename (200x200 PNG / RGB)
android.presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon filename
android.icon.filename = %(source.dir)s/data/icon.png

# (bool) Android landscape mode
android.landscape = False

# (bool) Android portrait mode
android.portrait = True
"""
    
    with open("buildozer.spec", "w") as f:
        f.write(spec_content)
    
    print("buildozer.spec created for python-for-android build.")


def main():
    """Main build function."""
    print("="*50)
    print("Virtual Pet Game - Android Build")
    print("="*50)
    
    # Check for --init flag to create project
    if "--init" in sys.argv:
        create_android_project()
        create_buildozer_spec()
        print("\nProject initialized!")
        print("To build, run: python build.py")
        return
    
    # Check for --buildozer flag
    if "--buildozer" in sys.argv:
        print("Using python-for-android (buildozer)...")
        try:
            subprocess.check_call([sys.executable, "-m", "buildozer", "android", "debug"])
            print("\nBuild complete!")
        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}")
        return
    
    # Default: try PGS4A build
    print("\nNote: PGS4A is older and may have issues.")
    print("Consider using python-for-android for better results:")
    print("  python build.py --buildozer")
    print()
    
    build_apk()


if __name__ == "__main__":
    main()
