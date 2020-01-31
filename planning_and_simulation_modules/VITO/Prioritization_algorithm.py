import pandas
import os

tb_rows = 10
tb_columns = 8
vito_criteria = 16
offset_x = 1
offset_y = 59
delta_x = 11
delta_y = 16


def prioritization_algorithm(weights=(10, 0, 10, 2, 5, 7, 0, 5, 4, 0, 3, 0, 0, 0, 0, 0)):
    output_vito = {"Space heating high temperature": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   "Space heating medium temperature": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   "Space heating low temperature": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   "Domestic hot water": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   "Space cooling": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                   }
    if weights is None or not len(weights) == vito_criteria:
        print("Prioritization_algorithm.prioritization_algorithm(): input weights not conform: ", weights)
        return output_vito

    input_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              "D2.8 Algorithms source ranking potential final draft.xlsm")
    data = pandas.read_excel(input_file)
    vito_keys = [key for key in output_vito.keys()]
    for key in range(len(vito_keys)):
        for criteria in range(vito_criteria):
            column = offset_x + key*delta_x
            row = offset_y + criteria*delta_y
            if key == 0 and criteria == 0:
                debug = True
            else:
                debug = False
            tb = single_table_calculation(data, [row, column], weights[criteria], debug)
            for i in range(len(tb)):
                output_vito[vito_keys[key]][i] = output_vito[vito_keys[key]][i] + tb[i]
    return output_vito


def single_table_calculation(data, start_cell, weight, debug):
    output = []
    for i in range(tb_rows):
        output.append(0)
        if debug:
            pass
        for x in data.values[start_cell[0] + i][start_cell[1]:start_cell[1] + tb_columns]:
            try:
                value = float(x)
                if value*weight > output[i]:
                    output[i] = round(value*weight)
            except ValueError:
                pass
    return output
