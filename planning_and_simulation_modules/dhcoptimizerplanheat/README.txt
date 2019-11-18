# Installation procedure

To set up the dhcoptimizer plugin, all the following instructions have to be executed in the given order.

## Environment variables:
  1. PYTHON_DIR = `%QGIS_DIR%\apps\Python36`
  2. QGIS_BIN = `%QGIS_DIR%\bin`
  3. PYTHON = `%PYTHON_DIR%\python`
  3. Add to the Path variable the following elements in this order:
	*  `%PYTHON_DIR%`
	*  `%PYTHON_DIR%\Lib`
	*  `%PYTHON_DIR%\Scripts`
	*  `%QGIS_BIN%`

  When launching python through a shell, the python found has to be the one in PYTHON_DIR. QGIS_DIR is the directory where QGIS is installed (by default: `C:\Program Files\QGIS 3.*`).


## Julia :
  1. Install julia (v0.6.4) from windows .exe file
  2. Set JULIA_HOME to the "bin" folder of julia, and add it to the Path environment variable
  3. Add packages :
	* Pycall : `Pkg.add("PyCall")`
	* JuMP : `Pkg.add("JuMP")`
	* Cbc : `Pkg.add("Cbc")`
	* Clp : `Pkg.add("Clp")`
  4. Precompile all packages. Run in julia :
    `using PyCall, JuMP, Cbc, Clp`

## Python packages :
  1. Update pip if necessary
  2. `Shapely` :
	* uninstall shapely `python -m pip uninstall shapely`
	* install shapely with no binary option : `python -m pip install shapely --no-binary shapely`
  3. `Rtree` : use pre-compiled binary .whl file
  4. `Fiona` : use pre-compiled binary .whl file
  5. `Pyproj` : use pre-compiled binary .whl file
  6. `geopandas` : `python -m pip install geopandas`
  7. `geopy` : `python -m pip install geopy`
  8. `osmnx` : `python -m pip install osmnx`
  9. `numpy-mkl` : use pre-compiled binary .whl file
  10. `julia` : `python -m pip install julia`

## Working Directories :
Create the working directories in the AppData folder :

    C:/Users/UserName/AppData/Local/QGIS/QGIS3/dhcoptimizer_data/
    C:/Users/UserName/AppData/Local/QGIS/QGIS3/dhcoptimizer_data/tmp/
    C:/Users/UserName/AppData/Local/QGIS/QGIS3/dhcoptimizer_data/results/

Plugin Builder Results

Your plugin DHCOptimizerPlanheat was created in:
    D:/software/OSGeo4W64/apps/qgis-dev/python/plugins\dhcoptimizerplanheat

Your QGIS plugin directory is located at:
    C:/Users/mdufour/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins

What's Next:

  * Copy the entire directory containing your new plugin to the QGIS plugin
    directory

  * Compile the resources file using pyrcc5

  * Run the tests (``make test``)

  * Test the plugin by enabling it in the QGIS plugin manager

  * Customize it by editing the implementation file: ``dhcoptimizer_planheat.py``

  * Create your own custom icon, replacing the default icon.png

  * Modify your user interface by opening DHCOptimizerPlanheat.ui in Qt Designer

  * You can use the Makefile to compile your Ui and resource files when
    you make changes. This requires GNU make (gmake)

For more information, see the PyQGIS Developer Cookbook at:
http://www.qgis.org/pyqgis-cookbook/index.html

(C) 2011-2018 GeoApt LLC - geoapt.com
