import geonetworkx as gnx
import pickle
import os
from zipfile import ZipFile
from ..exception_utils import DHCOptimizerException


class NetworkSerializer:
    """This objects provides a set of methods for exporting/importing an existing network."""

    PICKLE_DUMP_FILE_NAME = "existing_network_dump.pkl"

    def __init__(self, network: gnx.GeoGraph, old_network_streets: set, old_network_buildings: set):
        self.network = network
        self.old_network_streets = old_network_streets
        self.old_network_buildings = old_network_buildings

    def serialize(self, path: str, working_dir: str):
        """Writes current network in a zip file.

        :param path: Path to the zip file
        :param working_dir: Working directory for temporary file writing.
        """
        file_name, file_ext = os.path.splitext(path)
        if file_ext != ".zip":
            path += ".zip"
        pickle_file_name = os.path.join(working_dir, self.PICKLE_DUMP_FILE_NAME)
        # Pickle dump
        with open(pickle_file_name, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)
        # Zipping
        with ZipFile(path, 'w') as f:
            f.write(pickle_file_name, arcname=self.PICKLE_DUMP_FILE_NAME)
        os.remove(pickle_file_name)

    @classmethod
    def deserialize(cls, path: str, working_dir: str):
        """Reads a .zip file to extract a NetworkSerializer.

        :param path: Zip file path
        :param working_dir: Working directory for temporary file writing.
        :return A ``NetworkSerializer`` instance.
        """
        # Unzipping
        with ZipFile(path, 'r') as f:
            zipped_files = f.namelist()
            if cls.PICKLE_DUMP_FILE_NAME not in zipped_files:
                raise DHCOptimizerException("Inconsistent zip file: "
                                            "impossible to retrieve a network from the given file: %s" % str(path))
            f.extract(cls.PICKLE_DUMP_FILE_NAME, working_dir)
        # Pickle load
        pickle_file_name = os.path.join(working_dir, cls.PICKLE_DUMP_FILE_NAME)
        with open(pickle_file_name, 'rb') as f:
            ns = pickle.load(f)
        os.remove(pickle_file_name)
        return ns
