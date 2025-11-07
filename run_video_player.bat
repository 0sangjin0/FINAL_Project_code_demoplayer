@echo off
REM =================================================================
REM                  한글 깨짐 방지 코드 추가
chcp 65001 >nul
REM =================================================================
=================================================================
REM                  사용 전 아래 2개 경로를 수정하세요
REM =================================================================

REM (1) 본인의 "가상환경 폴더" 경로로 수정하세요. (예: C:\Users\sam76\Desktop\my_venv)
set VENV_PATH=C:\Users\sam76\Desktop\venv

REM (2) 실행할 "GUI 프로그램 파이썬 파일" 경로로 수정하세요.
set SCRIPT_PATH=C:\Users\sam76\Desktop\dual_video_player_with_tabs.py

REM =================================================================

echo.
echo [1] 가상환경을 활성화합니다...
call "%VENV_PATH%\Scripts\activate"

IF ERRORLEVEL 1 (
    echo.
    echo [오류] 가상환경 경로를 찾을 수 없습니다. VENV_PATH를 확인하세요.
    pause
    exit
)

echo.
echo [2] 필수 패키지를 설치합니다...
pip install --upgrade pip >nul
pip install pyqt5 opencv-python pandas numpy matplotlib openpyxl >nul

echo.
echo [3] 프로그램을 시작합니다!
python "%SCRIPT_PATH%"

echo.
echo 프로그램이 종료되었습니다.
pause

