@echo off
echo.
echo ============================================================
echo     BuildLedger: AI Construction Cost Management
echo ============================================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Model training...
echo Please ensure your dataset is at: ../dataset/Construction_Data_PM_Tasks_All_Projects.csv
echo.
echo Open model_training.ipynb in Jupyter and run all cells to train the model.
echo.
pause

echo.
echo Step 3: Starting Flask Backend API...
echo API will be available at: http://localhost:5000
echo.
python app.py

if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to start API server
    pause
    exit /b 1
)

pause
