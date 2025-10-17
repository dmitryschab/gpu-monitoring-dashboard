@echo off
REM Setup Automated GPU Monitoring Pipeline
REM Run this as Administrator to set up Windows Task Scheduler

echo ========================================
echo GPU Monitoring Pipeline Setup
echo ========================================
echo.

REM Create scheduled task to run on startup
echo Creating Windows Task Scheduler task...

schtasks /Create /F /SC ONSTART /TN "GPU-Monitoring-Pipeline" /TR "python C:\Users\dmitr\Documents\projects\gpu-monitoring-dashboard\automated_pipeline.py" /RL HIGHEST /RU "%USERNAME%"

echo.
echo ✅ Task created successfully!
echo.
echo To start the pipeline now, run:
echo    python automated_pipeline.py
echo.
echo Or it will start automatically on next reboot.
echo.
pause
