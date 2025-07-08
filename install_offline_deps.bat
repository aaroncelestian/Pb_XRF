@echo off
REM Offline install of Python dependencies for XRF_Pb project

REM Activate your Anaconda environment if needed
REM call conda activate xrf_pb

REM Install all dependencies from the offline_wheels folder
pip install --no-index --find-links=offline_wheels -r requirements.txt

echo.
echo All dependencies installed from offline_wheels!
pause 