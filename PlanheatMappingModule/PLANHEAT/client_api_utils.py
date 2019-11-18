import os
import time
from planheat.PlanheatMappingModule import master_mapping_config as mm_config
from planheatclient import PlanHeatClient
import json
from pyproj import Proj, transform
import time
from osgeo import ogr, osr
import sqlite3
import pickle


call_result_cache = dict()
mm_config.API_CACHE_TIMESTAMP = time.time()


def add_in_api_cache(key, val):
    """Add a value (that can be retrived with its key) in the cache dict. Cache timestamp is updated."""
    call_result_cache[key] = val
    mm_config.API_CACHE_TIMESTAMP = time.time()


def get_map(name=None, extent_coord_array=None, in_crs='31370', area_file=None):
    if name == "OSM buildings":
        return get_osm_buildings(name, area_file, in_crs)
    else:
        return get_map_by_name(name, extent_coord_array, in_crs)


def get_map_by_name(name=None, extent_coord_array=None, in_crs='31370'):
    from .io_utils import get_temp_folder_name
    """
    Get map from artelis planheat server.

    :param name: name of the map to get
    :param extent_coord_array: coordinates of the area to get
    :param in_crs: crs of the coordinates
    :return: geojson filepath, success boolean
    """
    #print(in_crs)
    c_envelope = convert(extent_coord_array, in_crs)
    if 'map_' + name + str(c_envelope) in call_result_cache:
        results = call_result_cache['map_' + name + str(c_envelope)]
        print('api cache hit, file loaded from cache: ', 'map_' + str(name) + str(c_envelope))
    else:
        t = time.time()
        try:
            #print("used call: ")
            print('PlanHeatClient("https://planheat.artelys.com").geo_query("' + name + '").intersect_envelope(' + str(c_envelope) + ',True)')
            request = PlanHeatClient("https://planheat.artelys.com").geo_query(name).intersect_envelope(c_envelope, True)
            #print(request.client.url + '/search/' + request.client.index, request.data)
            results = request.send()
            #print(results)
        except Exception as e:
            print('error from planheat api: ', e)

            return name + ' from planheat server', False
        print('planheatclient call duration: ', time.time() - t)
        if isinstance(results, str) and 'error' in results:
            print("ERROR in results", results)
            return name + ' from planheat server', False
        add_in_api_cache('map_' + name + str(c_envelope), results)
    if isinstance(results, (str, dict)):
        output_file = get_temp_folder_name() + r"/" + name + str(hash(str(c_envelope))) + '.json'
        with open(output_file, 'w') as file:
            json.dump(results, file)
    else:
        output_file = get_temp_folder_name() + r"/" + name + str(hash(str(c_envelope))) + '.tif'
        with open(output_file, 'wb') as file:
            file.write(results)

    return output_file, True


def get_osm_buildings(name='building', area_file=None, in_crs='31370'):
    from .io_utils import get_temp_folder_name
    """
    Get map from artelis planheat server.

    :param name: name of the map to get
    :param extent_coord_array: coordinates of the area to get
    :param in_crs: crs of the coordinates
    :return: geojson filepath, success boolean
    """

    #print(in_crs)
    input = ogr.Open(area_file)
    layer_in = input.GetLayer()
    sourceprj = layer_in.GetSpatialRef()
    targetprj = osr.SpatialReference()
    targetprj.SetFromUserInput("EPSG:4326")

    transform = osr.CoordinateTransformation(sourceprj, targetprj)
    layer_in.ResetReading()
    union = ogr.Geometry(3)
    for f in layer_in:
        transformed = f.GetGeometryRef()
        transformed.Transform(transform)
        geom = ogr.CreateGeometryFromWkb(transformed.ExportToWkb())
        union = union.Union(geom)
    extent_coord_array = union.GetEnvelope()
        #print(extent_coord_array)
    c_envelope = [[extent_coord_array[0],extent_coord_array[3]],[extent_coord_array[1],extent_coord_array[2]]]
    if 'map_' + name + str(c_envelope) in call_result_cache:
        results = call_result_cache['map_' + name + str(c_envelope)]
        print('api cache hit, file loaded from cache: ', 'map_' + str(name) + str(c_envelope))
    else:
        t = time.time()
        try:
            #print("used call: ")
            print('PlanHeatClient().osm_query("building").within_bounding_box(north='
                  + str(c_envelope[0][1]) + ', south=' + str(c_envelope[1][1]) + ', east=' + str(c_envelope[0][0]) + ', west=' + str(c_envelope[1][0]) + ')')

            results = PlanHeatClient().osm_query("building")\
                .within_bounding_box(north=c_envelope[0][1], south=c_envelope[1][1], east=c_envelope[0][0], west=c_envelope[1][0])

            #print(results)
        except Exception as e:
            print('error from planheat api: ', e)

            return name + ' from planheat server', False
        print('planheatclient call duration: ', time.time() - t)
        add_in_api_cache('map_' + name + str(c_envelope), results)

    output_file = get_temp_folder_name() + r"/" + name + str(hash(str(c_envelope))) + '.json'
    with open(output_file, 'w') as file:
        file.write(results)
    return output_file, True


def get_crop_yield(country=None, crop_type=None):
    """
    Get data from artelis planheat server.

    :param country: name of the country to get
    :param crop_type: name of the crop_type to get
    :return: array, success boolean
    """

    mapping_dict = {11: 'Cereals', 15: 'Wheat', 14: 'Barley', 13: 'Maize', 16: 'Rape seeds'}
    name = 'agriculture-acs-yield'
    if 'table_' + name + country + str(crop_type) in call_result_cache:
        results = call_result_cache['table_' + name + country + str(crop_type)]
        print('api cache hit, file loaded from cache: ', 'table_' + str(name) + country + str(crop_type))
    else:
        t = time.time()
        try:
            #print("used call: ")
            print(
                'PlanHeatClient("https://planheat.artelys.com").data_query("' + name + '").filter("country_ID","' + country + '").filter("Fuel","' + mapping_dict[crop_type] + '")')
            request = PlanHeatClient("https://planheat.artelys.com").data_query(name).filter('country_ID', country).filter("Fuel", mapping_dict[crop_type])
            print(request.client.url + '/search/' + request.client.index, request.data)
            results = request.send()
            #print(results)
        except Exception as e:
            print('error from planheat api: ', e)
            return name + ' from planheat server', False
        print('planheatclient call duration: ', time.time() - t)
        if 'error' in results:
            print("ERROR in results", results)
            return name + ' from planheat server', False
        add_in_api_cache('table_' + name + country + str(crop_type), results)
    result = round(float(results['Yield'][0]), 6)
    return result, True


def get_available_maps():
    """
    Get all available maps from artelis planheat server

    :return: list of maps
    """
    try:
        result = []
        all_items = PlanHeatClient("https://planheat.artelys.com").list()
        for item in all_items:
            if 'fields_' + item in call_result_cache:
                response = call_result_cache['fields_' + item]
                print('field api cache hit')
            else:
                response = PlanHeatClient("https://planheat.artelys.com").describe(item)
                add_in_api_cache('fields_' + item, response)
            if 'geometry' in response[item]["mappings"]["Features"]["properties"] or 'data' in response[item]["mappings"]["Features"]["properties"]:
                result.append(item)
        return result
    except:
        return []


def get_available_fields(index):
    """
    Get available fields for the map name
    :param index: map name
    :return: list of fields
    """
    try:
        if 'fields_' + index in call_result_cache:
            result = call_result_cache['fields_' + index]
            print('field api cache hit')
        else:
            result = PlanHeatClient("https://planheat.artelys.com").describe(index)
            add_in_api_cache('fields_' + index, result)
        return result[index]["mappings"]["Features"]["properties"]["properties"]["properties"].keys()
    except:
        return []


def convert(coords_input, in_crs='31370'):
    """
    convert coordinates to supported crs (4326)
    :param coords_input: list of coordinates
    :param in_crs: crs number
    :return: list of coordinates pairs
    """
    if in_crs == '' or in_crs is None:
        in_crs = '31370'
    in_proj = Proj(init='epsg:' + in_crs)
    out_proj = Proj(init='epsg:4326')
    converted_coords_array = []
    x1, y1 = transform(in_proj, out_proj, coords_input[0], coords_input[3])
    converted_coords_array.append([x1, y1])
    x2, y2 = transform(in_proj, out_proj, coords_input[1], coords_input[2])
    converted_coords_array.append([x2, y2])
    return converted_coords_array

def setup_triggers_on_db(db):
    """[To be used only by developpers]. Sets up the database to create trigger on the TREES table."""
    # Create the timestamps table
    c = db.cursor()
    c.execute("CREATE TABLE TABLE_TIMESTAMPS (table_name TEXT NOT NULL PRIMARY KEY,"
              "changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    # insert a first value
    c.execute("INSERT INTO TABLE_TIMESTAMPS (table_name) VALUES ('TREES')")
    # Add triggers on insert, update, delete operations
    update_ts_query = "UPDATE TABLE_TIMESTAMPS SET changed_at = CURRENT_TIMESTAMP WHERE table_name = 'TREES';"
    c.execute("CREATE TRIGGER IF NOT EXISTS trees_table_insert AFTER INSERT ON TREES "
              " BEGIN " + update_ts_query + " END;")
    c.execute("CREATE TRIGGER IF NOT EXISTS trees_table_update AFTER UPDATE ON TREES"
              " BEGIN " + update_ts_query + " END;")
    c.execute("CREATE TRIGGER IF NOT EXISTS trees_table_delete AFTER DELETE ON TREES"
              " BEGIN " + update_ts_query + " END;")
    # Validate the modifications
    db.commit()

def get_latest_trees_table_modification_date():
    """Return the latest 'TREES' modification date by reading its value in the 'TABLE_TIMESTAMPS' table. Return
    None if an error occurs.
    Latest modification date is stored in GMT system in the database, is converted to local time when requested here."""
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    try:
        c = db.cursor()
        c.execute("SELECT datetime(%s, 'localtime') FROM %s WHERE %s='%s'" % (mm_config.TABLE_TIMESTAMPS_CHANGED_AT_COLUMN_NAME,
                                                                              mm_config.TABLE_TIMESTAMPS_NAME,
                                                                              mm_config.TABLE_TIMESTAMPS_TABLE_COLUMN_NAME,
                                                                              mm_config.TABLE_TREES_NAME))
        t = None
        for row in c.fetchall():
            t = row[0]
            break
        if t is None:  # No row in the table
            print("Clearing cache: no row in the 'TABLE_TIMESTAMPS' table")
            return None
        print("t=%s" % str(t))
        timepoint = time.mktime(time.strptime(t, mm_config.SQL_DATE_FORMAT))
        return timepoint
    except sqlite3.OperationalError:  # Table doesn't exist, or else
        print("Clearing cache: of sqlite error")
        return None
    except ValueError:  # Incorrect date parsing
        print("Clearing cache: incorrect date parsing")
        return None


def api_cache_is_invalidated():
    """
    Return true if the api result cache is not valid anymore. The cache is invalidated if one of the following
    conditions is satisfied:
        * One of the input file has a modification date older than the cache timestamp
        * Modification date of the 'TREES' table in the database is older than cache timestamp
    """
    # Check for no cache time stamp
    print("API_CACHE_TIMESTAMP=%s" % str(mm_config.API_CACHE_TIMESTAMP))
    if mm_config.API_CACHE_TIMESTAMP is None:
        return True
    input_folder = os.path.join(mm_config.CURRENT_MAPPING_DIRECTORY,
                                mm_config.INPUT_FOLDER)
    # Checking input files dates
    for p, ds, fs in os.walk(input_folder):
        for f in fs:
            # Taking maximum between creation date and modification date if the file has been replaced.
            # Warning: getctime is platform specific (On windows, it returns the creation date of the path, on Unix it
            # returns the last modification of the path metadata
            latest_modification_date = max(os.path.getmtime(os.path.join(p, f)), os.path.getctime(os.path.join(p, f)))
            if latest_modification_date >= mm_config.API_CACHE_TIMESTAMP:
                print("Clearing cache because of recent input file modification")
                return True
    # Checking database modification dates
    timepoint = get_latest_trees_table_modification_date()
    if timepoint is None:
        return True
    if timepoint >= mm_config.API_CACHE_TIMESTAMP:
        print("Clearing cache: 'TREES' table modification")
        return True
    # Cache is valid:
    return False


def clear_api_cache():
    """
    clear internal api result cache
    :return:
    """
    if len(call_result_cache) > 0:
        if api_cache_is_invalidated():
            print("Clearing api cache")
            call_result_cache.clear()


class APICacheSerializer:
    """Wrapper to be able to serialize the api cache dict with its timestamp."""
    def __init__(self):
        global call_result_cache
        self.call_result_cache = call_result_cache
        self.API_CACHE_TIMESTAMP = mm_config.API_CACHE_TIMESTAMP

    @staticmethod
    def serialize():
        """Dump the object to the given file path."""
        api_cs = APICacheSerializer()
        if len(api_cs.call_result_cache) > 0:
            print("Serializing api cache to project directory")
            file_path = os.path.join(mm_config.CURRENT_MAPPING_DIRECTORY,
                                     mm_config.API_CACHE_PICKLE_FILE_NAME)
            with open(file_path, "wb") as f:
                pickle.dump(api_cs, f)
        else:
            print("Serializing api cache: empty cache")

    @staticmethod
    def deserialize():
        """Deserialize the written date and sets the global variables."""
        global call_result_cache
        file_path = os.path.join(mm_config.CURRENT_MAPPING_DIRECTORY,
                                 mm_config.API_CACHE_PICKLE_FILE_NAME)
        if os.path.exists(file_path):
            print("Deserializing api cache: reading file")
            with open(file_path, "rb") as f:
                api_cs = pickle.load(f)
            call_result_cache = api_cs.call_result_cache
            mm_config.API_CACHE_TIMESTAMP = api_cs.API_CACHE_TIMESTAMP
        else:
            print("Deserializing api cache: no file found")
