@echo off
chcp 65001 >nul
title ĐỒNG BỘ VĂN BẢN PDF & BẢN ĐỒ TRI THỨC LÊN GITHUB
color 0B

echo =====================================================================
echo    HỆ THỐNG ĐỒNG BỘ TỰ ĐỘNG BẢN ĐỒ TRI THỨC VÀ FILE PDF LÊN GITHUB
echo =====================================================================
echo.
echo Thư mục hiện tại: %~dp0
echo.

cd /d "%~dp0"
python sync_pdf_to_github.py

echo.
echo =====================================================================
pause

