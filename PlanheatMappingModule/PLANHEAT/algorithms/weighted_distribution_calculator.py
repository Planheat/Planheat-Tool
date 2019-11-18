import numpy as np


def compute_weight_sum(zone_count, weights_map, zone_map):
    # result = [0] * zone_count
    # for z in range(zone_count):
    #     result[z] = np.sum(weights_map[zone_map == z])

    value_array_nonan = np.where(np.isnan(weights_map), 0, weights_map)
    values = np.round(np.bincount(zone_map.astype(int).ravel(), value_array_nonan.ravel()), 2)
    # if ~(np.alltrue(np.isclose(values.tolist(), result))):
    #     print(values.tolist(), result)
    return values


def compute_weighted_distribution(nodata, weights_map, zone_map, zone_value):
    shape = zone_map.shape
    zone_map = np.where(np.isfinite(zone_map), zone_map.astype(int), -9999)
    weights_map = np.where(np.isfinite(weights_map), weights_map, 0)
    weights_map = np.where(weights_map > -9999, weights_map, 0)
    weight_sum = compute_weight_sum(len(zone_value), weights_map, zone_map)

    if np.max(zone_map) >= len(zone_value) or np.max(zone_map) >= len(weight_sum):
        raise RuntimeError(
            "B zone out of range in weighted distribution. zone max: " + str(np.max(zone_map)) + " | zone_value length: " + str(len(zone_value)) + " | weight sum lenght: " + str(
                len(weight_sum)))

    result = calc(nodata, weight_sum, weights_map, zone_map, zone_value)
    return np.array(result).reshape(shape)


def calc(nodata, weight_sum, weights_map, zone_map, zone_value):
    # result2 = [
    #     zone_value[z] * w / (weight_sum[z])
    #     if z >= 0 and w > 0
    #     else nodata
    #     for (z, w) in zip(zone_map.ravel(), weights_map.ravel())
    # ]

    value = np.take(zone_value, zone_map) * weights_map / np.take(weight_sum, zone_map)
    valid_values = np.logical_and(zone_map >= 0, weights_map > 0)
    result = np.where(valid_values, value, nodata)

    return result
