@echo off
echo ?? Setting up React Frontend for E-commerce Data Automation Dashboard
echo ==================================================================

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ? Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo ? Node.js version:
node --version
echo ? NPM version:
npm --version

REM Install dependencies
echo ?? Installing dependencies...
npm install

if %errorlevel% equ 0 (
    echo.
    echo ? Dependencies installed successfully!
    echo.
    echo ?? Setup Complete! Next steps:
    echo 1. Make sure your Flask backend is running on http://localhost:5000
    echo 2. Start the React development server:
    echo    npm run dev
    echo.
    echo 3. Open your browser to the URL shown by Vite (usually http://localhost:3000)
    echo.
    echo ?? Available commands:
    echo    npm run dev     - Start development server
    echo    npm run build   - Build for production
    echo    npm run preview - Preview production build
    echo.
    echo Happy coding! ???
) else (
    echo ? Installation failed. Please check your internet connection and try again.
    pause
    exit /b 1
)

pause