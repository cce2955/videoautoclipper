@echo off
SET VENV=.venv

REM Check if virtual environment exists
if not exist %VENV%\Scripts\activate.bat (
    echo Creating virtual environment...
    python -m venv %VENV%
)

REM Activate the virtual environment
call %VENV%\Scripts\activate.bat

REM Check if requirements are satisfied
python -m pip freeze > temp.txt
fc temp.txt requirements.txt > nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
)

del temp.txt

REM Run the program
echo Running the program...
python sub.py

REM Deactivate the virtual environment
call deactivate

REM Delete temporary files
del audio.wav
del video.webm
if exist output\merged_output.mp4 (
    move output\merged_output.mp4 sub\merged_output.mp4
)
if exist sub (
    rmdir /S /Q sub
)

echo Done.
