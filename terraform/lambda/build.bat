@echo off
REM Build Lambda deployment package (Windows)

echo Building Lambda deployment package...

REM Create temp directory
if exist package rmdir /s /q package
mkdir package
cd package

REM Install dependencies
pip install -r ..\requirements.txt --target .

REM Add Lambda function
copy ..\processor.py .

REM Create zip file (requires PowerShell)
powershell -Command "Compress-Archive -Path * -DestinationPath ..\gpu_processor.zip -Force"

REM Cleanup
cd ..
rmdir /s /q package

echo ✅ Lambda package created: gpu_processor.zip
dir gpu_processor.zip

pause
