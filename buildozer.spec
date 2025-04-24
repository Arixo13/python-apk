[app]

# عنوان التطبيق
title = قفل التطبيقات

# معلومات الحزمة
package.name = applocker
package.domain = com.example

# إصدار التطبيق
version = 1.0.0

# المصادر
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json

# الملف الرئيسي
main.py

# الأيقونة
icon.filename = %(source.dir)s/assets/app_icon.png

# المتطلبات
requirements = python3==3.9.6,kivy==2.1.0,jnius,pyjnius,android

# صلاحيات أندرويد
android.permissions = PACKAGE_USAGE_STATS, QUERY_ALL_PACKAGES
android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 33
android.ndk_path = 
android.sdk_path = 

# خيارات البناء
android.arch = armeabi-v7a
p4a.branch = master
android.meta_data = 
android.intent_filters = 
android.allow_backup = True
android.fast_deploy = True
android.debug = True

# خيارات التطبيق
fullscreen = 0
orientation = portrait
log_level = 2
presplash.filename = %(source.dir)s/assets/splash.png
presplash.color = #121212
window.softinput_mode = resize

# إعدادات التوقيع (للبحث فقط)
android.release_artifact = .apk
android.signing.keystore = 
android.signing.storepass = 
android.signing.keypass = 
android.signing.keyalias = 

# إعدادات التطبيق الإضافية
android.manifest.intent = 
android.add_src = 
android.add_resources = 
android.add_assets = assets/

# استثناءات
android.blacklist_src = 
android.blacklist_so = 
android.whitelist_src = 
android.whitelist_so = 

# مكتبات NDK المطلوبة
android.ndk_libs = 

# خيارات Python
python.major = 3
python.minor = 9
python.patch = 6

# خيارات OpenGL
android.opengl_version = 2

# خيارات أخرى
android.extra_manifest_xml = 
android.extra_manifest_application_arguments = 
android.entry_point = 
android.apptheme = 
android.usesplashscreen = 
