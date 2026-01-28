@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   다음 단계: Streamlit Cloud 배포
echo ========================================
echo.
echo 브라우저에서 아래 주소가 열립니다.
echo   https://share.streamlit.io
echo.
echo 거기서:
echo   1. GitHub 로그인
echo   2. New app 클릭
echo   3. Repository: rlawldks56/making.nj.friend
echo   4. Main file path: streamlit_app.py
echo   5. Deploy! 클릭
echo.
echo 그러면 https://xxxx.streamlit.app 주소가 생깁니다.
echo.
start https://share.streamlit.io
pause
