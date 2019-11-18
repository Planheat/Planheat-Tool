from enum import IntEnum


class TypeEnum(IntEnum):
    DEMAND = 0
    SUPPLY = 1


class ProjectTypeEnum(IntEnum):
    DEMAND_CURRENT = 0
    DEMAND_FUTURE = 1
    SUPPLY = 2


class AlgorithmEnum(IntEnum):
    NONE = 1
    SUM = 2
    DASYMAP = 3
    W_DIST = 4
    W_DIST2 = 5
    MULTI_FACT = 6
    SPREAD = 7
    SOLAR = 8
    PROVIDED = 9
    BIO_FORESTERY = 10
    CEREALS = 11
    # GREEN_MAIZE = 12
    GRAIN_MAIZE = 13
    BARLEY = 14
    WHEAT = 15
    RAPE_SEEDS = 16
    BASIC_AGRICULTURE = 17
    SEWER_SYSTEM = 18
    RIVERS_HEAT = 19
    RIVERS_COLD = 20
    RIVERS_FREE_COLD = 21
    LAKES_HEAT = 22
    LAKES_COLD = 23
    SHALLOW_GEOTHERMAL = 24
    DEEP_GEOTHERMAL = 25
