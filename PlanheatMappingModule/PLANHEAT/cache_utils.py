raster_array_dict = dict()
raster_cache = dict()
variable_cache = dict()
import numpy as np

def clear_raster_cache():
    raster_array_dict.clear()
    raster_cache.clear()
    variable_cache.clear()


def read_as_array(raster):
    if raster not in raster_array_dict:
        nodata = raster.GetRasterBand(1).GetNoDataValue()
        #print("nodata  " + str(nodata))
        rast_arr = raster.ReadAsArray()
        rast_arr = rast_arr.astype(np.float32)
        rast_arr[rast_arr == nodata] = np.NaN
        raster_array_dict[raster] = rast_arr
    return raster_array_dict[raster]


def put_raster_in_cache(input_file, attribute, add, raster):
    raster_cache[input_file + str(attribute) + str(add)] = raster


def get_raster_from_cache(input_file, attribute, add):
    key = input_file + str(attribute) + str(add)
    #print(key)
    if key in raster_cache:
        #print("cache hit")
        return raster_cache[key]
    #print("cache miss")
    return None


def get_country():
    if "country" in variable_cache:
        return variable_cache["country"]
    return None


def set_country(country):
    if country:
        variable_cache["country"] = country
