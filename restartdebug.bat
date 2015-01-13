%~d0
CHCP
cd %~d0%~p0
taskkill /f /im python.exe
python webpy.py 0.0.0.0:9999
pause