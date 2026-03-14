[app]

# (str) Title of your application
title = Sprint Runner

# (str) Package name
package.name = sprintrunner

# (str) Package domain (needed for android/ios packaging)
package.domain = org.sasi

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*.mp3,assets/*.wav

# (list) List of directories to exclude
source.exclude_dirs = tests, bin, venv, .buildozer

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.2.1,sdl2,pillow

# (list) Supported orientations
orientation = portrait

#
# Android specific
#

# (bool) Fullscreen
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,VIBRATE,WAKE_LOCK

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) NDK version - pinned for reproducible builds
android.ndk = 25b

# (int) NDK API - matches minapi
android.ndk_api = 21

# (bool) Auto accept SDK license for CI
android.accept_sdk_license = True

# (list) Single arch for faster CI builds
android.archs = arm64-v8a

# (bool) Auto backup
android.allow_backup = True

#
# Python for android (p4a)
#
p4a.branch = master

[buildozer]

log_level = 2
warn_on_root = 1