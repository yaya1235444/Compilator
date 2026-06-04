@echo off

chcp 65001 >nul
title NebuJS Automatic Compiler Installer v1.0.1
cls

:LANG_CHOICE
echo =======================================================
echo  [1] Français (French)
echo  [2] English (Anglais)
echo =======================================================
set /p lang="Choose your language / Choisissez votre langue (1-2) : "

if "%lang%"=="1" goto LANG_FR
if "%lang%"=="2" goto LANG_EN
goto LANG_CHOICE

:LANG_FR
set "m_welcome==== LANCEMENT DE LA CONFIGURATION AUTOMATIQUE ==="
set "m_py_check=[Étape 1/4] Vérification de Python..."
set "m_py_ok=[SUCCÈS] Python est déjà installé."
set "m_py_install=[ACTION] Python introuvable. Téléchargement et installation en cours..."
set "m_py_reboot=[IMPORTANT] Python vient d'être installé. Relancez ce fichier .bat pour continuer."
set "m_nuitka=[Étape 2/4] Installation et mise à jour de Nuitka..."
set "m_nuitka_ok=[SUCCÈS] Nuitka et ses composants sont prêts."
set "m_compile=[Étape 3/4] Compilation de NebuJS en cours (Patientez 1 à 2 minutes)..."
set "m_comp_err=[ERREUR] 'nebujs.py' est introuvable dans ce dossier !"
set "m_comp_ok=[SUCCÈS] Binaire créé avec succès dans dist\nebujs.exe"
set "m_path=[Étape 4/4] Configuration du PATH Windows..."
set "m_path_ok=[SUCCÈS] Dossier dist ajouté au PATH utilisateur avec succès !"
set "m_path_exist=[INFO] Le dossier est déjà présent dans le PATH."
set "m_finish==== TOUT EST PRÊT ! Baguette. ==="
goto START_PROCESS

:LANG_EN
set "m_welcome==== STARTING AUTOMATIC CONFIGURATION ==="
set "m_py_check=[Step 1/4] Checking Python..."
set "m_py_ok=[SUCCESS] Python is already installed."
set "m_py_install=[ACTION] Python not found. Downloading and installing..."
set "m_py_reboot=[IMPORTANT] Python has been installed. Please restart this .bat file to continue."
set "m_nuitka=[Step 2/4] Installing and updating Nuitka..."
set "m_nuitka_ok=[SUCCESS] Nuitka and dependencies are ready."
set "m_compile=[Step 3/4] Compiling NebuJS (Please wait 1 to 2 minutes)..."
set "m_comp_err=[ERROR] 'nebujs.py' was not found in this directory!"
set "m_comp_ok=[SUCCESS] Binary successfully created in dist\nebujs.exe"
set "m_path=[Step 4/4] Configuring Windows PATH..."
set "m_path_ok=[SUCCESS] dist folder successfully added to user PATH!"
set "m_path_exist=[INFO] Folder is already in PATH."
set "m_finish==== EVERYTHING IS READY! ==="
goto START_PROCESS

:START_PROCESS
cls
echo %m_welcome%
echo.


echo %m_py_check%
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %m_py_install%
    :: Télécharge l'installateur officiel silencieux de Python 3.11 x64
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    :: Installe en arrière-plan et l'ajoute au PATH système
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python_installer.exe
    echo.
    echo %m_py_reboot%
    pause
    exit
) else (
    echo %m_py_ok%
)
echo.


echo %m_nuitka%
python -m pip install --upgrade pip >nul 2>&1
python -m pip install ordered-set nuitka >nul 2>&1
echo %m_nuitka_ok%
echo.


echo %m_compile%
if not exist "nebujs.py" (
    echo %m_comp_err%
    pause
    exit
)
python -m nuitka --standalone --onefile --output-dir=dist nebujs.py >nul 2>&1
if %errorlevel% equ 0 (
    echo %m_comp_ok%
) else (
    :: Si Nuitka échoue à cause de GCC manquant, il va s'auto-télécharger au second essai en mode visible
    python -m nuitka --standalone --onefile --output-dir=dist nebujs.py
)
echo.


echo %m_path%
set "TARGET_DIR=%~dp0dist"
for /f "tokens=2*" %%A in ('reg query HKCU\Environment /v PATH 2^>nul') do set "OLD_PATH=%%B"

echo %OLD_PATH% | find /i "%TARGET_DIR%" >nul
if %errorlevel% neq 0 (
    if "%OLD_PATH%"=="" (
        reg add HKCU\Environment /v PATH /t REG_EXPAND_SZ /d "%TARGET_DIR%" /f >nul
    ) else (
        reg add HKCU\Environment /v PATH /t REG_EXPAND_SZ /d "%OLD_PATH%;%TARGET_DIR%" /f >nul
    )
    setx PATH "%PATH%" >nul 2>&1
    echo %m_path_ok%
) else (
    echo %m_path_exist%
)

echo.
echo =======================================================
echo %m_finish%
echo =======================================================
pause
exit
