"""
This file provides a single interface to the julia module
"""
import os
import sys
import julia
import logging

class JuliaQgisInterface:
    """This object provides an interface between Planheat embedded julia and QGIS python with the help of the
    python "julia" package. Here is an example of how to use it:

    with JuliaQgisInterface() as j:
        print("sin(3) =", j.sind(3.0))

    This should be always use within a "with .. as" block.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.old_working_directory = None
        self.old_env = None

    def __enter__(self):
        """Get a julia instance with a 'with' operator."""
        self.old_working_directory = os.getcwd()
        self.old_env = os.environ.copy()
        self.set_julia_environment_variables()
        self.set_julia_working_directory()
        j = julia.Julia()
        if "include" not in dir(j):
            j.add_module_functions("Base")
        if "include" not in dir(j):
            raise RuntimeError("Unable to setup julia interface.")
        return j

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset the state of the execution as before."""
        os.environ = self.old_env.copy()
        os.chdir(self.old_working_directory)


    def set_julia_environment_variables(self):
        """Set working environment variables so that pyjulia finds julia"""
        file_directory = os.path.dirname(os.path.realpath(__file__))
        qgis_directory = os.path.normpath(os.path.join(file_directory, "../../../../../.."))
        self.logger.info("\tqgis_directory=%s" % str(qgis_directory))
        # Setting executable path
        python_path = os.path.normpath(os.path.join(qgis_directory,
                                                    "apps/Python3%d/python.exe" % sys.version_info.minor))
        sys.executable = python_path
        self.logger.info("\tpython_path=%s" % str(python_path))
        file_directory = os.path.dirname(os.path.realpath(__file__))
        dhcoptimizer_directory = os.path.join(file_directory, "dhcoptimizerplanheat")
        plugin_deps_path = os.path.normpath(os.path.join(dhcoptimizer_directory, "deps"))
        self.logger.info("\tplugin_deps_path=%s" % str(plugin_deps_path))
        # Setting julia environment variable
        os.environ["JULIA_HOME"] = os.path.join(plugin_deps_path, "Julia-0.6.2/bin")
        julia_package_directory = os.path.join(plugin_deps_path, ".julia")
        os.environ["JULIA_PKGDIR"] = julia_package_directory
        self.logger.info("\tos.environ[\"JULIA_HOME\"]=%s" % str(os.environ["JULIA_HOME"]))
        self.logger.info("\tos.environ[\"JULIA_PKGDIR\"]=%s" % str(os.environ["JULIA_PKGDIR"]))
        # Adding variables to the environment path
        qgis_bin = os.path.join(qgis_directory, "bin")
        os.environ["PATH"] = os.environ["JULIA_HOME"] + ";" + qgis_bin + ";" + os.environ["PATH"]
        self.logger.info("\tos.environ[\"PATH\"]=%s" % str(os.environ["PATH"]))
        # Modify the libpython path for Pycall
        if sys.version_info.minor == 7:
            pycall_deps_file = os.path.join(julia_package_directory, "v0.6/PyCall/deps/deps.jl")
            self.set_pycall_python_dll_path(pycall_deps_file)

    @staticmethod
    def set_pycall_python_dll_path(file_path: str):
        """Set the pycall python dll path to the one in the QGIS 'bin' directory. Just the dll name is enough because
        QGIS 'bin' directory is the 'PATH' environment variable when calling julia. (not to be reused in later versions)
        """
        lib_python_line = 'const libpython = "python3%d"\n' % sys.version_info.minor
        with open(file_path, "r") as f:
            lines = f.readlines()
        new_lines = lines.copy()
        for l, line in enumerate(lines):
            if "const libpython =" in line:
                if lib_python_line == line:
                    return
                new_lines[l] = lib_python_line
                break
        with open(file_path, "w") as f:
            f.write("".join(new_lines))

    @staticmethod
    def set_julia_working_directory():
        """Set working directory to the julia bin directory."""
        if "JULIA_HOME" in os.environ:
            julia_dir = os.environ["JULIA_HOME"]
        else:
            raise RuntimeError(
                "Unable to find Julia directory in environment variable as 'JULIA_HOME'.")
        julia_dir = os.path.realpath(julia_dir)
        if "bin" not in julia_dir.split("\\")[-1]:
            julia_bin_dir = os.path.join(julia_dir, "bin\\")
            if os.path.exists(julia_bin_dir):
                julia_dir = julia_bin_dir
        os.chdir(julia_dir)


