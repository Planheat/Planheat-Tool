REM ===================================================================
REM Initial setting
REM ===================================================================

REM ============================== Set current QGIS directory ==================================
REM Set QGIS installation real path  (install->planheat->plugins->python->qgis->apps->QGIS 3.*)
SET QGIS_DIR=%~dp0\..\..\..\..\..\..
pushd %QGIS_DIR%
set QGIS_DIR=%cd%
popd
echo "QGIS Directory=%QGIS_DIR%"

REM Add QGISBIN to PATH variable
SET "QGISBIN=%QGIS_DIR%\bin"
SET "PATH=%QGISBIN%;%PATH%"

REM Set plugin dependencies directory real path
SET PLUGIN_DIR=%~dp0\..
pushd %PLUGIN_DIR%
set PLUGIN_DIR=%cd%
popd

echo "PLUGIN_DIR=%PLUGIN_DIR%"
SET "PLUGIN_DEPS_DIR=%PLUGIN_DIR%\deps"
echo "PLUGIN_DEPS_DIR=%PLUGIN_DEPS_DIR%"



REM ============================== Install python packages =====================================
REM Set python executable real directory
SET "QGIS_PYTHON_VERSION=Python36"
SET "PYTHON_DIR=%QGIS_DIR%\apps\Python36\"
IF NOT EXIST "%PYTHON_DIR%" (
	SET "QGIS_PYTHON_VERSION=Python37"
	SET "PYTHON_DIR=%QGIS_DIR%\apps\Python37\"
)
IF NOT EXIST "%PYTHON_DIR%" (
	set /p user_input="Error: Impossible to find right version for python. Press enter to quit."
	EXIT /b 
)
pushd %PYTHON_DIR%
set PYTHON_DIR=%cd%
SET "PYTHONPATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PYTHON_DIR%\Lib"


REM Install necessary packages
IF "%QGIS_PYTHON_VERSION%" == "Python36" (
	"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\GDAL-2.3.3-cp36-cp36m-win_amd64.whl"
) ELSE (
	"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\GDAL-2.4.1-cp37-cp37m-win_amd64.whl"
)
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\munch-2.3.2-py2.py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\attrs-19.1.0-py2.py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\Click-7.0-py2.py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\click_plugins-1.0.4-py2.py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\cligj-0.5.0-py3-none-any.whl"
IF "%QGIS_PYTHON_VERSION%" == "Python36" (
	"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\Fiona-1.8.4-cp36-cp36m-win_amd64.whl"
	"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\Rtree-0.8.3-cp36-cp36m-win_amd64.whl"
	"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\pandas-0.24.1-cp36-cp36m-win_amd64.whl"
) ELSE (
	"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\Fiona-1.8.6-cp37-cp37m-win_amd64.whl"
	"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\Rtree-0.8.3-cp37-cp37m-win_amd64.whl"
	"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\pandas-0.24.2-cp37-cp37m-win_amd64.whl"
)
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\geopandas-0.4.0-py2.py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\decorator-4.3.2-py2.py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\networkx-2.2-py2.py3-none-any.whl"
IF "%QGIS_PYTHON_VERSION%" == "Python36" (
	"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\pyproj-2.0.1-cp36-cp36m-win_amd64.whl"
) ELSE (
	"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\pyproj-2.1.3-cp37-cp37m-win_amd64.whl"
)
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\geographiclib-1.49-py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\geopy-1.18.1-py2.py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\geonetworkx-0.2-py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\descartes-1.1.0-py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\osmnx_Planheat-0.10.1-py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\julia-0.1.5-py2.py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\SRTM.py-0.3.4-py3-none-any.whl"
"%PYTHON_DIR%\python.exe" -m pip install --ignore-installed --no-deps  "%PLUGIN_DEPS_DIR%\python_libs\planheatclient-2.1-py3-none-any.whl"


REM =================================== Julia set up ===========================================
SET "JULIA_HOME=%PLUGIN_DIR%\planning_and_simulation_modules\dhcoptimizerplanheat\deps\Julia-0.6.2\bin"
SET "JULIA_PKGDIR=%PLUGIN_DIR%\planning_and_simulation_modules\dhcoptimizerplanheat\deps\.julia"

SET "PATH=%JULIA_HOME%;%PATH%"


REM ============================== Setting julia packages ======================================
"%JULIA_HOME%\julia.exe" -e "ENV[\"PYTHON\"]=raw\"%PYTHON_DIR%\python.exe\";Pkg.build(\"PyCall\")"
"%JULIA_HOME%\julia.exe" -e "using JuMP"
"%JULIA_HOME%\julia.exe" -e "Pkg.build(\"Clp\");using Clp"
"%JULIA_HOME%\julia.exe" -e "using Cbc"
"%JULIA_HOME%\julia.exe" -e "using PyCall"
"%JULIA_HOME%\julia.exe" -e "using CSV"
"%JULIA_HOME%\julia.exe" -e "using Ipopt"
"%JULIA_HOME%\julia.exe" -e "include(raw\"%PLUGIN_DIR%\planning_and_simulation_modules\dhcoptimizerplanheat\optimizer\automatic_design\DSSP.jl\"); using DSSP"
"%JULIA_HOME%\julia.exe" -e "include(raw\"%PLUGIN_DIR%\planning_and_simulation_modules\dhcoptimizerplanheat\optimizer\automatic_design\NLP\NLP_variable_flows.jl\"); using NLP"
"%JULIA_HOME%\julia.exe" -e "include(raw\"%PLUGIN_DIR%\planning_and_simulation_modules\Tjulia\Absorption_heat_pump_district_heating.jl\"); using Absorption_heat_pump_district_heating"
"%JULIA_HOME%\julia.exe" -e "include(raw\"%PLUGIN_DIR%\planning_and_simulation_modules\Tjulia\district_cooling.jl\"); using district_cooling"
"%JULIA_HOME%\julia.exe" -e "include(raw\"%PLUGIN_DIR%\planning_and_simulation_modules\Tjulia\individual_heating_and_cooling.jl\"); using individual_heating_and_cooling"



REM ============================= Setting working directory ====================================
IF NOT EXIST "%LOCALAPPDATA%\QGIS" mkdir "%LOCALAPPDATA%\QGIS"
IF NOT EXIST "%LOCALAPPDATA%\QGIS\QGIS3" mkdir "%LOCALAPPDATA%\QGIS\QGIS3"
IF NOT EXIST "%LOCALAPPDATA%\QGIS\QGIS3\dhcoptimizer_data" mkdir "%LOCALAPPDATA%\QGIS\QGIS3\planheat_data"
IF NOT EXIST "%LOCALAPPDATA%\QGIS\QGIS3\dhcoptimizer_data\results" mkdir "%LOCALAPPDATA%\QGIS\QGIS3\planheat_data\temp"

REM ============================ Clear old version of plugins ===================================
SETLOCAL ENABLEDELAYEDEXPANSION 

IF EXIST "%APPDATA%\Python" ( 
	
	IF EXIST "%APPDATA%\Python\Python36" (
		
		IF EXIST "%APPDATA%\Python\Python36\site-packages" (
			IF EXIST "%APPDATA%\Python\Python36\site-packages\planheatclient" (
				RMDIR /s /q "%APPDATA%\Python\Python36\site-packages\planheatclient"
			)
			IF EXIST "%APPDATA%\Python\Python36\site-packages\osmnx" (
				RMDIR /s /q "%APPDATA%\Python\Python36\site-packages\osmnx"
			)
		)
		
		IF EXIST "%APPDATA%\Python\Python36\lib\site-packages" (
			IF EXIST "%APPDATA%\Python\Python36\lib\site-packages\planheatclient" (
				RMDIR /s /q "%APPDATA%\Python\Python36\lib\site-packages\planheatclient"
			)
			IF EXIST "%APPDATA%\Python\Python36\lib\site-packages\osmnx" (
				RMDIR /s /q "%APPDATA%\Python\Python36\lib\site-packages\osmnx"
			)
		)
		
		IF EXIST "%APPDATA%\Python\Python36\Lib\site-packages" (
			IF EXIST "%APPDATA%\Python\Python36\Lib\site-packages\planheatclient" (
				RMDIR /s /q "%APPDATA%\Python\Python36\Lib\site-packages\planheatclient"
			)
			IF EXIST "%APPDATA%\Python\Python36\Lib\site-packages\osmnx" (
				RMDIR /s /q "%APPDATA%\Python\Python36\Lib\site-packages\osmnx"
			)
		)
	)
	
	IF EXIST "%APPDATA%\Python\Python37" (
		
		IF EXIST "%APPDATA%\Python\Python37\site-packages" (
			IF EXIST "%APPDATA%\Python\Python37\site-packages\planheatclient" (
				RMDIR /s /q "%APPDATA%\Python\Python37\site-packages\planheatclient"
			)
			IF EXIST "%APPDATA%\Python\Python37\site-packages\osmnx" (
				RMDIR /s /q "%APPDATA%\Python\Python37\site-packages\osmnx"
			)
		)
		
		IF EXIST "%APPDATA%\Python\Python37\lib\site-packages" (
			IF EXIST "%APPDATA%\Python\Python37\lib\site-packages\planheatclient" (
				RMDIR /s /q "%APPDATA%\Python\Python37\lib\site-packages\planheatclient"
			)
			IF EXIST "%APPDATA%\Python\Python37\lib\site-packages\osmnx" (
				RMDIR /s /q "%APPDATA%\Python\Python37\lib\site-packages\osmnx"
			)
		)
		
		IF EXIST "%APPDATA%\Python\Python37\Lib\site-packages" (
			IF EXIST "%APPDATA%\Python\Python37\Lib\site-packages\planheatclient" (
				RMDIR /s /q "%APPDATA%\Python\Python37\Lib\site-packages\planheatclient"
			)
			IF EXIST "%APPDATA%\Python\Python37\Lib\site-packages\osmnx" (
				RMDIR /s /q "%APPDATA%\Python\Python37\Lib\site-packages\osmnx"
			)
		)
	)
)


REM =========================== Change plugin folder access rights==============================
icacls "%PLUGIN_DIR%" /grant *S-1-1-0:(OI)(CI)(F)


REM ==================================================================
set /p user_input="Installation end. Check errors and press enter to exit."
REM ==================================================================
