@echo off
cls
echo ==================================================
echo Bosch Preventive Maintenance Pipeline
echo ==================================================

REM -------------------------
REM Activate Anaconda environment (replace 'base' with your env if different)
REM -------------------------
CALL C:\Users\Admin\anaconda3\Scripts\activate.bat base
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR activating Anaconda environment
    pause
    exit /b
)
echo Conda environment activated

REM -------------------------
REM Step 1: Run EDA notebook
REM -------------------------
echo Running EDA.ipynb ...
jupyter nbconvert --to notebook --execute --inplace "C:\Users\Admin\Downloads\Internship\Bosch_PMP\scripts\EDA.ipynb"
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR running EDA.ipynb
    pause
    exit /b
)
echo EDA.ipynb completed successfully

REM -------------------------
REM Step 2: Run Feature Engineering notebook
REM -------------------------
echo Running Feature_Engineering.ipynb ...
jupyter nbconvert --to notebook --execute --inplace "C:\Users\Admin\Downloads\Internship\Bosch_PMP\scripts\Feature_Engineering.ipynb"
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR running Feature_Engineering.ipynb
    pause
    exit /b
)
echo Feature_Engineering.ipynb completed successfully

REM -------------------------
REM Step 3: Run Classification Model notebook
REM -------------------------
echo Running classification_model.ipynb ...
jupyter nbconvert --to notebook --execute --inplace "C:\Users\Admin\Downloads\Internship\Bosch_PMP\scripts\classification_model.ipynb"
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR running classification_model.ipynb
    pause
    exit /b
)
echo classification_model.ipynb completed successfully

REM -------------------------
REM Step 4: Load to SQL Server notebook
REM -------------------------
echo Running load_to_sqlserver.ipynb ...
jupyter nbconvert --to notebook --execute --inplace "C:\Users\Admin\Downloads\Internship\Bosch_PMP\scripts\load_to_sqlserver.ipynb"
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR running load_to_sqlserver.ipynb
    pause
    exit /b
)
echo load_to_sqlserver.ipynb completed successfully

REM -------------------------
REM Step 5: Git operations
REM -------------------------
echo Updating GitHub repository...
cd "C:\Users\Admin\Downloads\Internship\Bosch_PMP"
git pull
git add .
git commit -m "Auto: Pipeline run update"
git push
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR updating GitHub
    pause
    exit /b
)
echo Git update completed

REM -------------------------
REM Step 6: Open deployed Streamlit apps
REM -------------------------
echo Opening deployed Streamlit apps in browser...
start https://boschappanalysis.streamlit.app/
start https://boschappmodel.streamlit.app/


echo ==================================================
echo Pipeline Completed Successfully!
echo ==================================================
pause
