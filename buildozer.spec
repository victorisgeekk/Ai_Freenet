# This repository primarily targets a Textual terminal UI.
# Kivy / buildozer packaging files are kept for reference under the sample/ directory.
# To build an Android APK, copy sample/buildozer.spec into your build directory and adapt as needed.

# ORIGINAL (moved to sample/buildozer.spec):
[app]
title = Autonomous Network Suite
package.name = networksuite
package.domain = org.autonomous
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 2.0
requirements = python3,kivy,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
android.api = 33
android.minapi = 21
android.sdk = 30
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
