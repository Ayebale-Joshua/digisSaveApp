[app]

title = DigiSave
package.name = digisave
package.domain = org.jcorelabs
source.dir = .
source.include_exts = py,png,jpg,kv,sql,db
version = 0.1

requirements = python3,kivy

orientation = landscape
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1