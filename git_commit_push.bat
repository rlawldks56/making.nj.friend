@echo off
chcp 65001 >nul
cd /d "%~dp0"

set REMOTE_URL=https://github.com/rlawldks56/making.nj.friend.git

where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    if exist "C:\Program Files\Git\bin\git.exe" set "PATH=C:\Program Files\Git\bin;%PATH%"
    if exist "C:\Program Files (x86)\Git\bin\git.exe" set "PATH=C:\Program Files (x86)\Git\bin;%PATH%"
    where git >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [오류] Git을 찾을 수 없습니다.
        echo https://git-scm.com/download/win 에서 설치 후 다시 실행하세요.
        pause
        exit /b 1
    )
)

echo ========================================
echo   making.nj.friend -^> GitHub 푸시
echo   %REMOTE_URL%
echo ========================================
echo.

if not exist ".git" (
    echo [1/5] Git 저장소 초기화...
    git init
    echo.
)

git remote get-url origin >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [2/5] 원격 저장소 추가...
    git remote add origin %REMOTE_URL%
    echo origin = %REMOTE_URL%
    echo.
) else (
    echo [2/5] 원격 저장소 확인 (origin)
    git remote set-url origin %REMOTE_URL%
    echo.
)

echo [3/5] 변경 파일 추가...
git add .
git add -u
git status
echo.

echo [4/5] 커밋 생성...
git commit -m "feat: Streamlit 웹 버전 추가 및 웹 배포 안내 문서" 2>nul
if %ERRORLEVEL% equ 0 (
    echo 커밋 완료.
) else (
    echo 커밋할 변경사항이 없거나 이미 커밋됨.
)
echo.

echo [5/5] GitHub로 푸시...
git branch -M main 2>nul
git push -u origin main 2>nul
if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo   푸시 완료!
    echo   https://github.com/rlawldks56/making.nj.friend
    echo ========================================
) else (
    git push -u origin master 2>nul
    if %ERRORLEVEL% equ 0 (
        echo 푸시 완료! https://github.com/rlawldks56/making.nj.friend
    ) else (
        echo.
        echo [안내] 푸시 실패. GitHub 로그인/인증을 확인하세요.
        echo   https://github.com/rlawldks56/making.nj.friend
    )
)
echo.
pause
