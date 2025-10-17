@echo off
REM Install Terraform on Windows
REM This script downloads and installs Terraform

echo Installing Terraform...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as administrator. Installation may fail.
    echo Please run this script as Administrator or use chocolatey/winget.
    echo.
)

REM Check if chocolatey is available
where choco >nul 2>&1
if %errorLevel% == 0 (
    echo Found Chocolatey. Installing Terraform via Chocolatey...
    choco install terraform -y
    goto :end
)

REM Check if winget is available
where winget >nul 2>&1
if %errorLevel% == 0 (
    echo Found winget. Installing Terraform via winget...
    winget install -e --id Hashicorp.Terraform
    goto :end
)

REM Manual installation
echo Chocolatey and winget not found. Manual installation required.
echo.
echo Please install Terraform manually:
echo.
echo Option 1 - Chocolatey (recommended):
echo   1. Install Chocolatey from https://chocolatey.org/install
echo   2. Run: choco install terraform
echo.
echo Option 2 - winget:
echo   Run: winget install Hashicorp.Terraform
echo.
echo Option 3 - Manual download:
echo   1. Download from https://www.terraform.io/downloads
echo   2. Extract to C:\Program Files\Terraform
echo   3. Add to PATH
echo.
pause
exit /b 1

:end
echo.
echo Terraform installation complete!
echo Please restart your terminal/PowerShell and run: terraform version
echo.
pause
