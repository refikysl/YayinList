@echo off
chcp 65001 >nul
echo Uygulama başlatılıyor...
echo Tarayıcınızda açılmasını bekleyin.
echo Uygulamayı kapatmak için bu pencereyi kapatabilirsiniz.
echo.
python -m streamlit run app.py
pause
