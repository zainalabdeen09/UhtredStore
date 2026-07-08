@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ====================================
echo   Uhtred Store APK Builder
echo ====================================
echo.

if not defined JAVA_HOME (
    echo [!] JAVA_HOME is not set.
    echo Attempting to locate Java...
    for /f "tokens=*" %%a in ('where java 2^>nul') do (
        set "JAVA_PATH=%%a"
        goto :found_java
    )
    echo [ERROR] Java not found. Please install JDK 17+ and set JAVA_HOME.
    pause
    exit /b 1
)

:found_java
if defined JAVA_PATH (
    for %%i in ("%JAVA_PATH%") do set "JAVA_HOME=%%~dpi.."
    echo [INFO] Using Java at: %JAVA_HOME%
) else (
    echo [INFO] Using JAVA_HOME: %JAVA_HOME%
)
echo.

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

if not exist "gradlew.bat" (
    echo [*] Generating Gradle wrapper...
    call gradle wrapper --gradle-version 8.5 >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to generate Gradle wrapper.
        echo Make sure Gradle is installed or download it from https://gradle.org/
        pause
        exit /b 1
    )
)

echo [*] Cleaning old builds...
if exist "app\build\outputs\apk" rmdir /s /q "app\build\outputs\apk" >nul 2>&1

echo [*] Building debug APK...
echo.
echo This may take several minutes on first build
echo (Chaquopy needs to download and compile Python).
echo.

call gradlew.bat assembleDebug

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Check the output above for details.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Build completed!

set "APK_SRC=%SCRIPT_DIR%app\build\outputs\apk\debug"
set "DESKTOP=%USERPROFILE%\Desktop"

if exist "%APK_SRC%\app-debug.apk" (
    copy /y "%APK_SRC%\app-debug.apk" "%DESKTOP%\UhtredStore.apk" >nul
    echo [*] APK copied to Desktop: %DESKTOP%\UhtredStore.apk
) else (
    echo [WARNING] APK not found at expected location.
    echo Check: %APK_SRC%
    dir /s /b "%SCRIPT_DIR%app\build\outputs\*.apk" 2>nul
)

echo.
echo ====================================
echo   Build Complete!
echo ====================================
popd
pause
