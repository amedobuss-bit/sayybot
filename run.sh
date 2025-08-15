#!/bin/bash

echo "========================================"
echo "        RailBot - بوت القصائد الآمن"
echo "========================================"
echo

echo "جاري التحقق من تثبيت Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ خطأ: Python3 غير مثبت"
    echo "يرجى تثبيت Python 3.8+"
    exit 1
fi

echo "✅ Python3 مثبت بنجاح"
echo

echo "جاري التحقق من تثبيت التبعيات..."
pip3 install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ خطأ: فشل في تثبيت التبعيات"
    exit 1
fi

echo "✅ التبعيات مثبتة بنجاح"
echo

echo "جاري تشغيل البوت..."
echo
python3 main.py
