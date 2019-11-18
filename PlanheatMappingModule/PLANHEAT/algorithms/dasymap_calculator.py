# -*- coding: utf-8 -*-
import numpy as np


def compute_gkz(class_map, class_weight, zone_map, zone_weight):
    # akz: a( = area) -> number of cells with class c and zone z

    class_weight_length = len(class_weight)
    zone_weight_length = len(zone_weight)

    az = [0] * zone_weight_length
    akz = [0] * class_weight_length * zone_weight_length
    ak = [0] * class_weight_length

    c_values, c_counts = np.unique(class_map, return_counts=1)

    for value, count in zip(c_values, c_counts):
        if 0 <= value < class_weight_length:
            ak[value] = count
        elif value >= class_weight_length:
            raise RuntimeError("class out of range in dasymatrix mapping " + str(value))

    z_values, z_counts = np.unique(zone_map, return_counts=1)
    for value, count in zip(z_values, z_counts):
        if 0 <= value < zone_weight_length:
            az[value] = count
        elif value >= zone_weight_length:
            raise RuntimeError("zone out of range in dasymatrix mapping " + str(value))

    for class_map_value, zone_map_value in zip(class_map, zone_map):
        if class_map_value >= 0 and zone_map_value >= 0:
            akz[(class_map_value * zone_weight_length) + zone_map_value] += 1

    a = np.sum(zone_weight)

    gkz = [0] * class_weight_length * zone_weight_length
    ckz = [0] * class_weight_length * zone_weight_length
    cz = [0] * zone_weight_length
    for z in range(zone_weight_length):
        for c in range(class_weight_length):
            kz = c * zone_weight_length + z
            ckz[kz] = class_weight[c] * (akz[kz] / (az[z])) / (ak[c] / a) if az[z] > 0 and a > 0 and ak[c] > 0 else 0
            cz[z] += ckz[kz]
    for z in range(zone_weight_length):
        if cz[z] > 0:
            for c in range(class_weight_length):
                kz = c * zone_weight_length + z
                gkz[kz] = (ckz[kz] / cz[z]) / akz[kz] if akz[kz] > 0 else 0
        else:
            for c in range(class_weight_length):
                kz = c * zone_weight_length + z
                gkz[kz] = 1.0 / akz[kz] if akz[kz] > 0 else 0

    return gkz


def calculate(no_data, class_map, class_weight, zone_map, zone_value):
    result = np.zeros_like(zone_map).astype('float32')
    gkz_cols = len(zone_value)
    zone_map = np.where(np.isfinite(zone_map), zone_map.astype(int), -9999)
    class_map = np.where(np.isfinite(class_map), class_map.astype(int), -9999)

    # gkz is  result[r][c] = zone_value(r, c) * gkz[kz(r, c)]
    class_map_ravel = class_map.ravel()
    class_weight_ravel = class_weight.ravel()
    zone_map_ravel = zone_map.ravel()
    zone_value_ravel = zone_value.ravel()
    gkz = compute_gkz(class_map_ravel, class_weight_ravel, zone_map_ravel, zone_value_ravel)

    result_ravel = result.ravel()
    for_each_raster_cell(class_map_ravel, zone_map_ravel, zone_value_ravel, result_ravel, gkz, gkz_cols, no_data)

    return result


def for_each_raster_cell(class_map, zone_map, zone_value, result, gkz, gkz_cols, no_data):
    [func(index, class_map, zone_map, zone_value, result, gkz, gkz_cols, no_data) for index in range(len(zone_map))]


def func(index, class_map, zone_map, zone_value, result, gkz, gkz_cols, no_data):
    class_map_value = class_map[index]
    zone_map_value = zone_map[index]
    if class_map_value >= 0 and zone_map_value >= 0:
        result[index] = zone_value[zone_map_value] * gkz[(class_map_value * gkz_cols) + zone_map_value]
    elif zone_map_value < 0:
        result[index] = no_data
