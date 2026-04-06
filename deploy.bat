@echo off
REM Deployment script for Flask PDF Q&A App to AWS Lambda via Zappa

echo === Deployment Script ===
echo.

REM Check prerequisites
echo Checking prerequisites...
where zappa >nul 2>nul || (
    echo Error: Zappa is not installed. Install with: pip install zappa
    pause
    exit /b 1
)
where python >nul 2>nul || (
    echo Error: Python is not installed
    pause
    exit /b 1
)
echo Prerequisites OK
echo.

REM Install dependencies
echo Installing dependencies...
call pip install -r requirements.txt
echo Dependencies installed
echo.

REM Verify template files exist
echo Verifying template files...
if not exist "templates\auth.html" (
    echo Error: templates\auth.html is missing!
    pause
    exit /b 1
)
if not exist "templates\index.html" (
    echo Error: templates\index.html is missing!
    pause
    exit /b 1
)
echo Templates found
echo.

REM Package the app
echo Creating deployment package...
zappa package prod
echo.

REM Ask for confirmation
set /p CONFIRM=Deploy to production? (yes/no):
if /i "%CONFIRM%" neq "yes" (
    echo Deployment cancelled
    pause
    exit /b 0
)

REM Deploy
echo.
echo Deploying to AWS Lambda...
zappa deploy prod
echo.

REM Show status
echo Getting deployment status...
zappa status prod
echo.

echo === Deployment Complete ===
echo.
echo Your app should be available at the URL shown above.
echo.
echo To update later, run: zappa update prod
echo To tail logs: zappa tail prod
echo To rollback: zappa rollback prod
pause
