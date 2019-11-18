# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Configuration file
 The PlanHeat tool was implemented as part of the PLANHEAT project.
 This file contains several global variables used inside the different sub-modules.
                              -------------------
        begin                : 2019-04-25
        git sha              : $Format:%H$
        copyright            : (C) 2019 by PlanHeat consortium
        email                : stefano.barberis@rina.org
 ***************************************************************************/
"""


### Files and directories
WORKING_DIRECTORY_NAME = "planheat_data"
TEMP_WORKING_DIRECTORY_NAME = "temp"
MAPPING_DIRECTORY_NAME = "mapping"
PLANNING_DIRECTORY_NAME = "planning"
PROJECT_INFO_JSON_NAME = "info.json"
# Mapping files
MAPPING_CMM_SMM_DB_FILE_NAME = "planheat.db"
DMM_FOLDER = "DMM"
DMM_PREFIX = "DMM_result"
DMM_FUTURE_SUFFIX = "_future"
DMM_HOURLY_SUFFIX = "_hourly"
DMM_FUTURE_HOURLY_SUFFIX = "_future_hourly"
SMM_FOLDER = "SMM"
CMM_BASELINE_FOLDER = "CMMB"
CMM_FUTURE_FOLDER = "CMMF"
INPUT_FOLDER = "input_files"
# Planning District files
DISTRICT_FOLDER = "District"
BASELINE_FOLDER = "Baseline"
FUTURE_FOLDER = "Future"
TOOLS_FOLDER = "Tools"
KPIS_FOLDER = "KPIs"
STREETS_FOLDER = "Streets"
BUILDING_SHAPE = "Building_shape"
# Planning City files
CITY_FOLDER = "City"
CMM_WIZARD_FOLDER = "Wizard"

# Clean files for master plugins
PROJECTS_CLEAN_DATA_DIR = "project_init_data"
ANTWERP_TEST_CASE_FILE_NAME = "antwerp_scenario_clean.zip"


# Objects constants names
PROJECT_NAME_KEY = "Name"
PROJECT_DESCRIPTION_KEY = "Description"
PROJECT_CREATION_DATE_KEY = "Creation date"
PROJECT_ID_KEY = "Id"
KEYS_TO_SHOW = [PROJECT_NAME_KEY, PROJECT_CREATION_DATE_KEY, PROJECT_DESCRIPTION_KEY]
DATE_FMT = "%Y-%m-%d %H:%M"

PROJECT_NAME_DEFAULT = "Unamed project"