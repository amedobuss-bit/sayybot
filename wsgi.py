# -*- coding: utf-8 -*-
"""
WSGI configuration for RailBot on PythonAnywhere
This file is required for PythonAnywhere to run the Flask app
"""

import sys
import os

# إضافة مسار المشروع إلى Python path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

# استيراد تطبيق Flask
from main import flask_app

# تعيين متغير البيئة
os.environ['FLASK_ENV'] = 'production'

# تطبيق Flask للتشغيل على PythonAnywhere
application = flask_app

if __name__ == "__main__":
    flask_app.run()
