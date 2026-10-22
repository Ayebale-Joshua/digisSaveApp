[app]

# (str) Title of your application
title = DigiSave

# (str) Package name
package.name = digisave

# (str) Package domain (needed for android packaging)
package.domain = org.jcorelabs

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let it include py, kv, database, and image files)
source.include_exts = py,png,jpg,kv,sql,db

# (str) Application versioning
version = 0.1

# (list) Application requirements
# Explicitly pin python3 and hostpython3 matching the build environment, along with your dependencies
requirements = python3,kivy,sqlite3

# (str) Supported orientations (landscape optimized for your tablet workflow)
orientation = landscape

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (bool) Automatically accept Android SDK license agreements to prevent headless build halts
android.accept_sdk_license = True

# (int) Target Android API, should be stable
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1