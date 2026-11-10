@echo off
chcp 65001 >nul
title Mở Bản Đồ Tri Thức PDF 3D
cd /d "%~dp0"

echo ========================================================
echo   DANG CAP NHAT DU LIEU TU KHO VAN BAN PDF...
echo ========================================================
python "generate_pdf_knowledge_graph.py"

echo.
echo ========================================================
echo   DANG MO BAN DO TRI THUC PDF 3D TREN TRINH DUYET...
echo ========================================================
start "" "Ban_Do_Tri_Thuc_Van_Ban_PDF.html"

echo Hoan tat! Trinh duyet da duoc khoi dong.
timeout /t 3 >nul
