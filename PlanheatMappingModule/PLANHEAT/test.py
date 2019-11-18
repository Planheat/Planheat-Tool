import numpy as np
import time

def fill_values(zone_array, value_array, zone_ids):

    value_array_nonan = np.where(np.isnan(value_array), 0, value_array)
    bincount = np.round(np.bincount(zone_array.astype(int).ravel(), value_array_nonan.ravel()), 2)
    # assert (np.alltrue(np.isclose(values.tolist(), values2)))
    values = bincount[zone_ids]
    return values


def run():
    # 300 different zones
    zone_ids = range(300)
    # zone map with 300 zones
    zone_array = (np.random.rand(2000, 2000) * 300).astype(int)
    # value map from which we want the sum of values per zone (real map can have NaN values)
    value_array = (np.random.rand(2000, 2000) * 10.)
    value_array[5, 5] = np.NAN
    t = time.time()
    fill_values(zone_array, value_array, zone_ids)
    print(time.time() - t)

if __name__ == '__main__':
    run()
