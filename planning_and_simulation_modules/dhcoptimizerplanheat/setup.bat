REM ===================================================================
REM Initial setting
REM ===================================================================

REM ============================== Set current QGIS directory ==================================
REM Set QGIS installation real path
SET QGIS_DIR=%QGIS_DIR%
pushd %QGIS_DIR%
set QGIS_DIR=%cd%
popd
echo "QGIS Directory=%QGIS_DIR%"

REM Add QGISBIN to PATH variable
SET "QGISBIN=%QGIS_DIR%\bin"
SET "PATH=%QGISBIN%;%PATH%"

REM Set plugin dependencies directory real path
SET PLUGIN_DEPS_DIR=%~dp0\deps
pushd %PLUGIN_DEPS_DIR%
set PLUGIN_DEPS_DIR=%cd%
popd
echo "PLUGIN_DEPS_DIR=%PLUGIN_DEPS_DIR%"

SET "PYTHON_DIR=%QGIS_DIR%\apps\Python36"
pushd %PYTHON_DIR%
set PYTHON_DIR=%cd%
popd
SET "PYTHONPATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PYTHON_DIR%\Lib"



REM =================================== Julia set up ===========================================
SET "JULIA_HOME=%~dp0\deps\Julia-0.6.2\bin"
SET "JULIA_PKGDIR=%~dp0\deps\.julia"

SET "PATH=%JULIA_HOME%;%PATH%"



REM ============================== Setting julia packages ======================================
"%JULIA_HOME%\julia.exe" -e "ENV[\"PYTHON\"]=raw\"%PYTHON_DIR%\python.exe\";Pkg.build(\"PyCall\")"
"%JULIA_HOME%\julia.exe" -e "using JuMP"
"%JULIA_HOME%\julia.exe" -e "Pkg.build(\"Clp\");using Clp"
"%JULIA_HOME%\julia.exe" -e "using PyCall"
"%JULIA_HOME%\julia.exe" -e "using CSV"
"%JULIA_HOME%\julia.exe" -e "using Ipopt"
"%JULIA_HOME%\julia.exe" -e "include(raw\"%~dp0\optimizer\automatic_design\DSSP.jl\"); using DSSP"



REM ==================================================================
set /p user_input="Installation end. Check errors and press enter to exit."
REM ==================================================================
