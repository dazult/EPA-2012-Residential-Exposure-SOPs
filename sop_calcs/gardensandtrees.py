
fraction_of_transferable_ai = {'liquid':{},'solid':{}}
fraction_of_residue_dissipates_per_day = {'liquid':{},'solid':{}}
days_after_application = {'liquid':{},'solid':{}}

fraction_of_transferable_ai['liquid']['dermal'] = 0.25
fraction_of_transferable_ai['solid']['dermal'] = 0.25
fraction_of_residue_dissipates_per_day['liquid']['dermal'] = 0.1
fraction_of_residue_dissipates_per_day['solid']['dermal'] = 0.1
days_after_application['liquid']['dermal'] = 0
days_after_application['solid']['dermal'] = 0

mass_conversion_factor_ug_lb = 450000000 # not 453592370
mass_conversion_factor_mg_ug = 0.001
area_conversion_factor_acre_cm2 = 0.0000000247 # not 2.47105381e-8





hours_of_exposure = {'liquid':{},'solid':{}}
hours_of_exposure['liquid']['gardens'] = {}
hours_of_exposure['solid']['gardens'] = {}
hours_of_exposure['liquid']['gardens']['adult'] = 2.2
hours_of_exposure['solid']['gardens']['adult'] = 2.2
hours_of_exposure['liquid']['gardens']['6_to_11'] = 1.1
hours_of_exposure['solid']['gardens']['6_to_11'] = 1.1


hours_of_exposure['liquid']['trees and retail plants (if applicable)'] = {}
hours_of_exposure['solid']['trees and retail plants (if applicable)'] = {}
hours_of_exposure['liquid']['trees and retail plants (if applicable)']['adult'] = 1.
hours_of_exposure['solid']['trees and retail plants (if applicable)']['adult'] = 1.
hours_of_exposure['liquid']['trees and retail plants (if applicable)']['6_to_11'] = .5
hours_of_exposure['solid']['trees and retail plants (if applicable)']['6_to_11'] = .5

hours_of_exposure['liquid']['indoor plants'] = {}
hours_of_exposure['solid']['indoor plants'] = {}
hours_of_exposure['liquid']['indoor plants']['adult'] = 1.
hours_of_exposure['solid']['indoor plants']['adult'] = 1.
hours_of_exposure['liquid']['indoor plants']['6_to_11'] = .5
hours_of_exposure['solid']['indoor plants']['6_to_11'] = .5


hours_of_exposure['liquid']['pick your own farms (low crops)'] = {}
hours_of_exposure['solid']['pick your own farms (low crops)'] = {}
hours_of_exposure['liquid']['pick your own farms (low crops)']['adult'] = 5.
hours_of_exposure['solid']['pick your own farms (low crops)']['adult'] = 5.
hours_of_exposure['liquid']['pick your own farms (low crops)']['6_to_11'] = 1.9
hours_of_exposure['solid']['pick your own farms (low crops)']['6_to_11'] = 1.9

hours_of_exposure['liquid']['pick your own farms (tree crops)'] = {}
hours_of_exposure['solid']['pick your own farms (tree crops)'] = {}
hours_of_exposure['liquid']['pick your own farms (tree crops)']['adult'] = 5.
hours_of_exposure['solid']['pick your own farms (tree crops)']['adult'] = 5.
hours_of_exposure['liquid']['pick your own farms (tree crops)']['6_to_11'] = 1.9
hours_of_exposure['solid']['pick your own farms (tree crops)']['6_to_11'] = 1.9

transfer_coefficient = {'liquid':{},'solid':{}}
transfer_coefficient['liquid']['gardens'] = {}
transfer_coefficient['solid']['gardens'] = {}
transfer_coefficient['liquid']['gardens']['adult'] = 8400.
transfer_coefficient['solid']['gardens']['adult'] = 4600.
transfer_coefficient['liquid']['gardens']['6_to_11'] = 8400.
transfer_coefficient['solid']['gardens']['6_to_11'] = 4600.

transfer_coefficient['liquid']['trees and retail plants (if applicable)'] = {}
transfer_coefficient['solid']['trees and retail plants (if applicable)'] = {}
transfer_coefficient['liquid']['trees and retail plants (if applicable)']['adult'] = 1700.
transfer_coefficient['solid']['trees and retail plants (if applicable)']['adult'] = 1700.
transfer_coefficient['liquid']['trees and retail plants (if applicable)']['6_to_11'] = 930.
transfer_coefficient['solid']['trees and retail plants (if applicable)']['6_to_11'] = 930.


transfer_coefficient['liquid']['indoor plants'] = {}
transfer_coefficient['solid']['indoor plants'] = {}
transfer_coefficient['liquid']['indoor plants']['adult'] = 220.
transfer_coefficient['solid']['indoor plants']['adult'] = 220.
transfer_coefficient['liquid']['indoor plants']['6_to_11'] = 120.
transfer_coefficient['solid']['indoor plants']['6_to_11'] = 120.


transfer_coefficient['liquid']['pick your own farms (low crops)'] = {}
transfer_coefficient['solid']['pick your own farms (low crops)'] = {}
transfer_coefficient['liquid']['pick your own farms (low crops)']['adult'] = 8400.
transfer_coefficient['solid']['pick your own farms (low crops)']['adult'] = 8400.
transfer_coefficient['liquid']['pick your own farms (low crops)']['6_to_11'] = 4600.
transfer_coefficient['solid']['pick your own farms (low crops)']['6_to_11'] = 4600.

transfer_coefficient['liquid']['pick your own farms (tree crops)'] = {}
transfer_coefficient['solid']['pick your own farms (tree crops)'] = {}
transfer_coefficient['liquid']['pick your own farms (tree crops)']['adult'] = 1700.
transfer_coefficient['solid']['pick your own farms (tree crops)']['adult'] = 1700.
transfer_coefficient['liquid']['pick your own farms (tree crops)']['6_to_11'] = 930.
transfer_coefficient['solid']['pick your own farms (tree crops)']['6_to_11'] = 930.



from exposure_profile import ExposureProfile

def gardensandtrees(POD, LOC,  bodyweight, dermal_absorption, application_rate, dfr):
    exposure_profile = ExposureProfile(bodyweight, POD, LOC, dermal_absorption=dermal_absorption)  
    for formulation in transfer_coefficient:
        if dfr[formulation] == 0:
            dfr[formulation] = application_rate[formulation]  #(lb ai/acre)
            dfr[formulation] *= fraction_of_transferable_ai[formulation]['dermal']
            dfr[formulation] *= (1 - fraction_of_residue_dissipates_per_day[formulation]['dermal'])**(days_after_application[formulation]['dermal'])
            dfr[formulation] *= mass_conversion_factor_ug_lb*area_conversion_factor_acre_cm2
        for activity in transfer_coefficient[formulation]:
            for lifestage in transfer_coefficient[formulation][activity]:
                try:
                    exposure = dfr[formulation] *  mass_conversion_factor_mg_ug * transfer_coefficient[formulation][activity][lifestage] * hours_of_exposure[formulation][activity][lifestage] # mg/day
                except:
                    exposure = "Invalid"
                exposure_profile.update('dermal',formulation,activity,lifestage, exposure)
    return exposure_profile        

def test():
    POD = {}
    LOC = {}
    POD['dermal'] = 1
    LOC['dermal'] = 1
    dermal_absorption = 1
    body_weights_adults_options = [80, 69, 86] # kg
    bodyweight = {}
    bodyweight['adult'] = body_weights_adults_options[0]
    bodyweight['6_to_11'] = 32
    dfr = {'liquid':0, 'solid':0}
    application_rate = {'liquid':3,'solid':3} # lb ai / acre
    return gardensandtrees(POD, LOC, bodyweight, dermal_absorption, application_rate, dfr)
