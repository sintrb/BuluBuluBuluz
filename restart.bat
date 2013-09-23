%~d0
cd %~d0%~p0
taskkill /f /im python.exe
cls
python webpy.py 0.0.0.0:9011
pause