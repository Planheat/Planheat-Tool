class CharacterizationUIutils:
    
    Inclinazione = 1
    Temp = 1
    Efficiency = 1
    coeff1 = 1
    coeff2 = 1
    P_max = 1
    P_min = 1
    cb_CHP = 1
    TechMin = 1
    RampUpDown = 1
    FixedCost = 1
    FuelCost = 1
    VariableCost = 1
    Tes_size = 1
    socMin = 1
    tesStartEnd = 1
    tes_discharge = 1
    Cop_absorption = 1
    elSale = 1

    network_area = 1

    @staticmethod
    def reset_cooling_input(ui):
        CharacterizationUIutils.reset_input(ui.coolingInclinazione, CharacterizationUIutils.Inclinazione)
        CharacterizationUIutils.reset_input(ui.coolingTemp, CharacterizationUIutils.Temp)
        CharacterizationUIutils.reset_input(ui.coolingEfficiency, CharacterizationUIutils.Efficiency)
        CharacterizationUIutils.reset_input(ui.cooling1coeff, CharacterizationUIutils.coeff1)
        CharacterizationUIutils.reset_input(ui.cooling2coeff, CharacterizationUIutils.coeff2)
        CharacterizationUIutils.reset_input(ui.P_max_cooling, CharacterizationUIutils.P_max)
        CharacterizationUIutils.reset_input(ui.P_min_cooling, CharacterizationUIutils.P_min)
        CharacterizationUIutils.reset_input(ui.cb_CHP_cooling, CharacterizationUIutils.cb_CHP)
        CharacterizationUIutils.reset_input(ui.coolingTechMin, CharacterizationUIutils.TechMin)
        CharacterizationUIutils.reset_input(ui.coolingRampUpDown, CharacterizationUIutils.RampUpDown)
        CharacterizationUIutils.reset_input(ui.coolingFixedCost, CharacterizationUIutils.FixedCost)
        CharacterizationUIutils.reset_input(ui.coolingFuelCost, CharacterizationUIutils.FuelCost)
        CharacterizationUIutils.reset_input(ui.coolingVariableCost, CharacterizationUIutils.VariableCost)
        CharacterizationUIutils.reset_input(ui.Tes_size_cooling, CharacterizationUIutils.Tes_size)
        CharacterizationUIutils.reset_input(ui.cooling_socMin, CharacterizationUIutils.socMin)
        CharacterizationUIutils.reset_input(ui.cooling_tesStartEnd, CharacterizationUIutils.tesStartEnd)
        CharacterizationUIutils.reset_input(ui.tes_discharge_cooling, CharacterizationUIutils.tes_discharge)
        CharacterizationUIutils.reset_input(ui.Cop_absorption_cooling, CharacterizationUIutils.Cop_absorption)

    @staticmethod
    def reset_heating_input(ui):
        CharacterizationUIutils.reset_input(ui.heatingElsale, CharacterizationUIutils.elSale)
        CharacterizationUIutils.reset_input(ui.heatingInclinazione, CharacterizationUIutils.Inclinazione)
        CharacterizationUIutils.reset_input(ui.heatingTemp, CharacterizationUIutils.Temp)
        CharacterizationUIutils.reset_input(ui.heatingEfficiency, CharacterizationUIutils.Efficiency)
        CharacterizationUIutils.reset_input(ui.heating1coeff, CharacterizationUIutils.coeff1)
        CharacterizationUIutils.reset_input(ui.heating2coeff, CharacterizationUIutils.coeff2)
        CharacterizationUIutils.reset_input(ui.P_max_heating, CharacterizationUIutils.P_max)
        CharacterizationUIutils.reset_input(ui.P_min_heating, CharacterizationUIutils.P_min)
        CharacterizationUIutils.reset_input(ui.cb_CHP_heating, CharacterizationUIutils.cb_CHP)
        CharacterizationUIutils.reset_input(ui.heatingTechMin, CharacterizationUIutils.TechMin)
        CharacterizationUIutils.reset_input(ui.heatingRampUpDown, CharacterizationUIutils.RampUpDown)
        CharacterizationUIutils.reset_input(ui.heatingFixedCost, CharacterizationUIutils.FixedCost)
        CharacterizationUIutils.reset_input(ui.heatingFuelCost, CharacterizationUIutils.FuelCost)
        CharacterizationUIutils.reset_input(ui.heatingVariableCost, CharacterizationUIutils.VariableCost)
        CharacterizationUIutils.reset_input(ui.Tes_size_heating, CharacterizationUIutils.Tes_size)
        CharacterizationUIutils.reset_input(ui.Soc_min_heating, CharacterizationUIutils.socMin)
        CharacterizationUIutils.reset_input(ui.tes_startEnd_heating, CharacterizationUIutils.tesStartEnd)
        CharacterizationUIutils.reset_input(ui.tes_discharge_heating, CharacterizationUIutils.tes_discharge)
        CharacterizationUIutils.reset_input(ui.COP_heating, CharacterizationUIutils.Cop_absorption)
            
    @staticmethod
    def reset_dhw_input(ui):
        CharacterizationUIutils.reset_input(ui.dhwElsale, CharacterizationUIutils.elSale)
        CharacterizationUIutils.reset_input(ui.dhwInclinazione, CharacterizationUIutils.Inclinazione)
        CharacterizationUIutils.reset_input(ui.dhwTemp, CharacterizationUIutils.Temp)
        CharacterizationUIutils.reset_input(ui.dhwEfficiency, CharacterizationUIutils.Efficiency)
        CharacterizationUIutils.reset_input(ui.dhw1coeff, CharacterizationUIutils.coeff1)
        CharacterizationUIutils.reset_input(ui.dhw2coeff, CharacterizationUIutils.coeff2)
        CharacterizationUIutils.reset_input(ui.dhwP_max, CharacterizationUIutils.P_max)
        CharacterizationUIutils.reset_input(ui.dhwP_min, CharacterizationUIutils.P_min)
        CharacterizationUIutils.reset_input(ui.dhwCb_CHP, CharacterizationUIutils.cb_CHP)
        CharacterizationUIutils.reset_input(ui.dhwTechMin, CharacterizationUIutils.TechMin)
        CharacterizationUIutils.reset_input(ui.dhwRampUpDown, CharacterizationUIutils.RampUpDown)
        CharacterizationUIutils.reset_input(ui.dhwFixedCost, CharacterizationUIutils.FixedCost)
        CharacterizationUIutils.reset_input(ui.dhwFuelCost, CharacterizationUIutils.FuelCost)
        CharacterizationUIutils.reset_input(ui.dhwVariableCost, CharacterizationUIutils.VariableCost)
        CharacterizationUIutils.reset_input(ui.dhwTes_size, CharacterizationUIutils.Tes_size)
        CharacterizationUIutils.reset_input(ui.dhwSoc_min, CharacterizationUIutils.socMin)
        CharacterizationUIutils.reset_input(ui.dhwTes_startEnd, CharacterizationUIutils.tesStartEnd)
        CharacterizationUIutils.reset_input(ui.dhwTes_discharge, CharacterizationUIutils.tes_discharge)
        CharacterizationUIutils.reset_input(ui.dhwCop, CharacterizationUIutils.Cop_absorption)
            
    @staticmethod
    def reset_network_input(ui):
        CharacterizationUIutils.reset_input(ui.networkarea, CharacterizationUIutils.network_area)
        CharacterizationUIutils.reset_input(ui.networkTemp, CharacterizationUIutils.Temp)
        CharacterizationUIutils.reset_input(ui.networkEta, CharacterizationUIutils.Efficiency)
        CharacterizationUIutils.reset_input(ui.network1coeff, CharacterizationUIutils.coeff1)
        CharacterizationUIutils.reset_input(ui.network2coeff, CharacterizationUIutils.coeff2)
        CharacterizationUIutils.reset_input(ui.networkP_min, CharacterizationUIutils.P_min)
        CharacterizationUIutils.reset_input(ui.networkcb_CHP, CharacterizationUIutils.cb_CHP)
        CharacterizationUIutils.reset_input(ui.networkTechMin, CharacterizationUIutils.TechMin)
        CharacterizationUIutils.reset_input(ui.networkRampUpDown, CharacterizationUIutils.RampUpDown)
        CharacterizationUIutils.reset_input(ui.networkVariableCost, CharacterizationUIutils.VariableCost)
        CharacterizationUIutils.reset_input(ui.networkFixedCost, CharacterizationUIutils.FixedCost)
        CharacterizationUIutils.reset_input(ui.networkFuelCost, CharacterizationUIutils.FuelCost)
        CharacterizationUIutils.reset_input(ui.networkTes_size, CharacterizationUIutils.Tes_size)
        CharacterizationUIutils.reset_input(ui.networkSocMin, CharacterizationUIutils.socMin)
        CharacterizationUIutils.reset_input(ui.networkTesStartEnd, CharacterizationUIutils.tesStartEnd)
        CharacterizationUIutils.reset_input(ui.networkTes_discharge, CharacterizationUIutils.tes_discharge)
        CharacterizationUIutils.reset_input(ui.networkCop_absorption, CharacterizationUIutils.Cop_absorption)
        CharacterizationUIutils.reset_input(ui.network_el_sale, CharacterizationUIutils.elSale)


    @staticmethod
    def reset_input(spin_box, value):
        try:
            spin_box.setValue(value)
        except (AttributeError, ValueError):
            pass
