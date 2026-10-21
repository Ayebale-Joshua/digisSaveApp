[app]

# (str) Title of your application
title = DigiSave

# (str) Package name
package.name = digisave

# (str) Package domain (needed for android packaging)
package.domain = org.jcorelabs

# (str) Source directory where your source files live
source.dir = .

# (str) Application version
version = 0.1

# (str) Source files to include (let it include py, kv, and database files)
source.include_exts = py,png,jpg,kv,sql,db

# (list) Application requirements
# Add any other pure python packages your app uses here
requirements = python3,kivy,sqlite3

# (str) Supported orientations (landscape is best for your tablet workflow)
orientation = landscape

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (str) Supported android architectures
android.archs = arm64-v8a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21