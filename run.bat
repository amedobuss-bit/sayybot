@echo off
echo ========================================
echo        RailBot - بوت القصائد الآمن
echo ========================================
echo.

echo جاري التحقق من تثبيت Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطأ: Python غير مثبت أو غير موجود في PATH
    echo يرجى تثبيت Python 3.8+ من python.org
    pause
    exit /b 1
)

echo ✅ Python مثبت بنجاح
echo.

echo جاري التحقق من تثبيت التبعيات...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ❌ خطأ: فشل في تثبيت التبعيات
    pause
    exit /b 1
)

echo ✅ التبعيات مثبتة بنجاح
echo.

echo جاري تشغيل البوت...
echo.
python main.py

pause
