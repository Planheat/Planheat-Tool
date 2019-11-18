# -*- coding: utf-8 -*-
"""This files defines configuration variables to manage the mapping module from the master plugin."""

from ..config import *

CURRENT_PROJECT_NAME = None
CURRENT_PROJECT_ID = None
CURRENT_MAPPING_DIRECTORY = None
CURRENT_DB_CMM_SMM_FILE_PATH = None

ALIAS_MAPPING_DIRECTORY = "[PROJECT_MAPPING_DIRECTORY]"

# Cache invalidation constants:
API_CACHE_TIMESTAMP = None  # floating point number
TABLE_TIMESTAMPS_NAME = "TABLE_TIMESTAMPS"
TABLE_TIMESTAMPS_TABLE_COLUMN_NAME = "table_name"
TABLE_TIMESTAMPS_CHANGED_AT_COLUMN_NAME = "changed_at"
TABLE_TREES_NAME = "TREES"
SQL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Cache serialization constants
API_CACHE_PICKLE_FILE_NAME = "api_cache.pickle"

CMM_WIZARD_RESULT_FILE_NAME = "results.csv"

# DMM serialization
SHAPE_FILE_EXTENSIONS = [".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx", ".fbn", ".fbx", ".ain", ".aih", ".ixs", ".mxs",
                         ".atx", ".cpg", ".qix"]
DMM_INPUT_SHAPE_FILE_NAME = "buildings_DMM"
INCREMENTAL_SERIALIZED_DMM_PICKLE_FILE = "incremental_serialized_dmm.pickle"
SERIALIZED_DMM_FILE = DMM_PREFIX + ".scn"



