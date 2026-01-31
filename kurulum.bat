@echo off
chcp 65001 >nul
echo Sistem kontrol ediliyor...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ========================================================
    echo HATA: Python bulunamadı!
    echo ========================================================
    echo.
    echo Lütfen Python'u kurun ve kurulum sırasında "Add to PATH"
    echo seçeneğini işaretlediğinizden emin olun.
    pause
    exit
)

echo Python bulundu. Gerekli kütüphaneler yükleniyor...
echo.
:: Explicitly use the python executable to run pip
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ========================================================
    echo HATA: Yükleme başarısız oldu.
    echo İnternet bağlantınızı kontrol edin.
    echo ========================================================
    pause
    exit
)

echo.
echo ========================================================
echo TEBRİKLER! Kurulum başarıyla tamamlandı.
echo Artık 'baslat.bat' dosyasına tıklayarak programı açabilirsiniz.
echo ========================================================
pause
