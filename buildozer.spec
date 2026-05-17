```ini
[app]

# App identity
title = Scrble
package.name = scrble
package.domain = org.scrble
version = 1.0

# Source
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,gz
source.include_patterns = data/*.py,data/*.gz,game/*.py,screens/*.py

# Python requirements
requirements = python3,kivy==2.3.0

# Orientation
orientation = portrait

# Android settings
android.permissions = VIBRATE
android.api = 33
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

# Build mode
fullscreen = 0

# iOS
# ios.kivy_ios_url = https://github.com/kivy/kivy-ios

[buildozer]
log_level = 2
warn_on_root = 1
```
