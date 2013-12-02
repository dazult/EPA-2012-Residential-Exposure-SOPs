#Lawns/Turf SOP

## User inputs 
# Active ingredient
# Exposure Duration (Short, Medium, Long)
# Incidental Oral POD (mg/kg/day) LOC
# Dietary Acute POD (mg/kg/day) LOC
# Dermal POD (mg/kg/day), POD source/study (Route-specific, Orald), Absoption (0-1), Absorption source/study (Human study, Animal study, Estimated by POD pr LOAEL/NOAEL comparison, in vitro study, other), LOC

# Body weights: Adults (Dermal) (80,69,86)
# Children : 11-16 years 57; 6-11 years 32; 1-2years 11

# Dermal without TTR
# Application Rate: Liquid (lb ai/acre) + solid (lb ai/acre)

# TTR concs (liquid + solid) (ug/cm^2)

# OtM without TTR
# Application Rate: Liquid (lb ai/acre) + solid (lb ai/acre)

# Incidental Oral
# Application Rate: Liquid (lb ai/acre) + solid (lb ai/acre)

# Granule Ingestion:
# % active ingredient in product

fraction_of_transferable_ai = {'liquid':{},'solid':{}}
fraction_of_residue_dissipates_per_day = {'liquid':{},'solid':{}}
days_after_application = {'liquid':{},'solid':{}}

fraction_of_transferable_ai['liquid']['dermal'] = 0.01
fraction_of_transferable_ai['solid']['dermal'] = 0.002
fraction_of_residue_dissipates_per_day['liquid']['dermal'] = 0.1
fraction_of_residue_dissipates_per_day['solid']['dermal'] = 0.1
days_after_application['liquid']['dermal'] = 0
days_after_application['solid']['dermal'] = 0

mass_conversion_factor_ug_lb = 450000000 # not 453592370
mass_conversion_factor_mg_ug = 0.001
mass_conversion_factor_mg_g = 1000.
mass_conversion_factor_g_ug = 0.000001
area_conversion_factor_acre_cm2 = 0.0000000247 # not 2.47105381e-8



hours_of_exposure = {'liquid':{},'solid':{}}
hours_of_exposure['liquid']['high_contact_lawn_activities'] = {}
hours_of_exposure['solid']['high_contact_lawn_activities'] = {}
hours_of_exposure['liquid']['high_contact_lawn_activities']['adult'] = 1.5
hours_of_exposure['solid']['high_contact_lawn_activities']['adult'] = 1.5
hours_of_exposure['liquid']['high_contact_lawn_activities']['1_to_2'] = 1.5
hours_of_exposure['solid']['high_contact_lawn_activities']['1_to_2'] = 1.5

hours_of_exposure['liquid']['mowing_turf'] = {}
hours_of_exposure['solid']['mowing_turf'] = {}
hours_of_exposure['liquid']['mowing_turf']['adult'] = 1.
hours_of_exposure['solid']['mowing_turf']['adult'] = 1.
hours_of_exposure['liquid']['mowing_turf']['11_to_16'] = 1.
hours_of_exposure['solid']['mowing_turf']['11_to_16'] = 1.

hours_of_exposure['liquid']['golfing'] = {}
hours_of_exposure['solid']['golfing'] = {}
hours_of_exposure['liquid']['golfing']['adult'] = 1.
hours_of_exposure['solid']['golfing']['adult'] = 1.
hours_of_exposure['liquid']['golfing']['11_to_16'] = 4.
hours_of_exposure['solid']['golfing']['11_to_16'] = 4.
hours_of_exposure['liquid']['golfing']['6_to_11'] = 4.
hours_of_exposure['solid']['golfing']['6_to_11'] = 4.

transfer_coefficient = {'liquid':{},'solid':{}}
transfer_coefficient['liquid']['high_contact_lawn_activities'] = {}
transfer_coefficient['solid']['high_contact_lawn_activities'] = {}
transfer_coefficient['liquid']['high_contact_lawn_activities']['adult'] = 180000.
transfer_coefficient['solid']['high_contact_lawn_activities']['adult'] = 200000.
transfer_coefficient['liquid']['high_contact_lawn_activities']['1_to_2'] = 49000.
transfer_coefficient['solid']['high_contact_lawn_activities']['1_to_2'] = 54000.

transfer_coefficient['liquid']['mowing_turf'] = {}
transfer_coefficient['solid']['mowing_turf'] = {}
transfer_coefficient['liquid']['mowing_turf']['adult'] = 5500.
transfer_coefficient['solid']['mowing_turf']['adult'] = 5500.
transfer_coefficient['liquid']['mowing_turf']['11_to_16'] = 4500.
transfer_coefficient['solid']['mowing_turf']['11_to_16'] = 4500.

transfer_coefficient['liquid']['golfing'] = {}
transfer_coefficient['solid']['golfing'] = {}
transfer_coefficient['liquid']['golfing']['adult'] = 5300.
transfer_coefficient['solid']['golfing']['adult'] = 5300.
transfer_coefficient['liquid']['golfing']['11_to_16'] = 4400.
transfer_coefficient['solid']['golfing']['11_to_16'] = 4400.
transfer_coefficient['liquid']['golfing']['6_to_11'] = 2900.
transfer_coefficient['solid']['golfing']['6_to_11'] = 2900.


def test ():
    body_weights_adults_options = [80, 69, 86] # kg
    bodyweight = {}
    bodyweight['adult'] = body_weights_adults_options[0]
    bodyweight['11_to_16'] = 57
    bodyweight['6_to_11'] = 32
    bodyweight['1_to_2'] = 11
    POD = {}
    LOC = {}
    RI = {}
    dermal_absorption = 1
    POD['dermal'] = 1
    LOC['dermal'] = 1
    POD['oral'] = 1
    LOC['oral'] = 1
    POD['dietary'] = 1
    LOC['dietary'] = 1
    application_rate = {'liquid':3,'solid':3} # lb ai / acre
    ttr = {'liquid':0, 'solid':0}
    fraction_active_ingredient = 0.01
    print lawnturfsop(POD, LOC,  bodyweight, dermal_absorption, application_rate, ttr, fraction_active_ingredient)


from exposure_profile import ExposureProfile

def lawnturfsop(POD, LOC,  bodyweight, dermal_absorption, application_rate, ttr, fraction_active_ingredient):
    object_residue = {'liquid':ttr['liquid'], 'solid':ttr['solid']} # mg/cm2
    
    exposure_profile = ExposureProfile(bodyweight, POD, LOC, dermal_absorption=dermal_absorption)


    for formulation in transfer_coefficient:
        if ttr[formulation] == 0:
            ttr[formulation] = application_rate[formulation]  #(lb ai/acre)
            ttr[formulation] *= fraction_of_transferable_ai[formulation]['dermal']
            ttr[formulation] *= (1 - fraction_of_residue_dissipates_per_day[formulation]['dermal'])**(days_after_application[formulation]['dermal'])
            ttr[formulation] *= mass_conversion_factor_ug_lb*area_conversion_factor_acre_cm2

        #High Contact Lawn Activites
        for activity in transfer_coefficient[formulation]:
            for lifestage in transfer_coefficient[formulation][activity]:
                try:
                    exposure = ttr[formulation] *  mass_conversion_factor_mg_ug * transfer_coefficient[formulation][activity][lifestage] * hours_of_exposure[formulation][activity][lifestage] # mg/day
                except:
                    exposure = "Invalid"
                exposure_profile.update('dermal',formulation,activity,lifestage, exposure)
                
                   


    #HandToMouth
    fai_hands  = {'liquid':{},'solid':{}} 

    hand_residue  = {'liquid':{},'solid':{}} # mg/cm2

    fai_hands['liquid']['1_to_2'] = 0.06 # fraction active ingredient on hands
    fai_hands['solid']['1_to_2'] = 0.027

    surface_area_hand = {}
    surface_area_hand['1_to_2'] = 150. #cm2
    fraction_of_hand_mouthed_per_event = {}
    fraction_of_hand_mouthed_per_event['1_to_2'] = .127
    n_replenishment_intervals_per_hr = 4
    extraction_by_saliva = 0.48
    htm_events_per_hr = 13.9


    for formulation in fai_hands:

        for lifestage in ['1_to_2']:
            dermal_exposure = 0
            try:
                dermal_exposure += exposure_profile.exposure['dermal'][formulation]['high_contact_lawn_activities'][lifestage]        
                hand_residue[formulation][lifestage] = fai_hands[formulation][lifestage]*dermal_exposure/(surface_area_hand[lifestage]*2.)
            except:
                hand_residue[formulation][lifestage] = "Invalid"
            try:
                exposure =  hand_residue[formulation][lifestage] * fraction_of_hand_mouthed_per_event[lifestage] * surface_area_hand[lifestage] * hours_of_exposure[formulation]['high_contact_lawn_activities'][lifestage] * n_replenishment_intervals_per_hr * ( 1 - (1 - extraction_by_saliva)**(htm_events_per_hr/n_replenishment_intervals_per_hr))
            except:
                exposure = "Invalid"
            exposure_profile.update('oral',formulation,'hand_to_mouth',lifestage, exposure)
        
    
    
    #ObjectToMouth ORt = TTRt when TTR available
    fai_objects  = {'liquid':0.01,'solid':0.002}  # fraction active ingredient on object


    otm_events_per_hr = 8.8
    object_area_mouthed_per_event = {'1_to_2':10} # cm2 / event
    for formulation in object_residue:
        if object_residue[formulation] == 0.0:

            try:
                object_residue[formulation] = application_rate[formulation]  #(lb ai/acre)
                object_residue[formulation] *= fai_objects[formulation]
                object_residue[formulation] *= mass_conversion_factor_ug_lb*area_conversion_factor_acre_cm2
            except:
                object_residue[formulation] = "Invalid"


        for lifestage in ['1_to_2']:
            try:
                exposure =  object_residue[formulation] * mass_conversion_factor_mg_ug * object_area_mouthed_per_event[lifestage] * hours_of_exposure[formulation]['high_contact_lawn_activities'][lifestage] * n_replenishment_intervals_per_hr * ( 1 - (1 - extraction_by_saliva)**(otm_events_per_hr/n_replenishment_intervals_per_hr))
            except:
                exposure = "Invalid"     
            exposure_profile.update('oral',formulation,'object_to_mouth',lifestage, exposure)       


    #Ingestion
    #Soil Ingestion


    soil_FS = {'solid':1,'liquid':1}
    soil_FD = {'solid':.1,'liquid':.1}
    soil_t =  {'solid':0,'liquid':0}
    soil_residue = {'solid':None,'liquid':None}
    soil_volume_to_mass_conversion_factor = .67 #cm3/g soil
    soil_ingestion_rate = 50 #mg/day
    for formulation in soil_residue:
        soil_residue[formulation] = application_rate[formulation]*soil_FS[formulation]*((1 - soil_FD[formulation])**soil_t[formulation] )*mass_conversion_factor_ug_lb*area_conversion_factor_acre_cm2*soil_volume_to_mass_conversion_factor

        for lifestage in ['1_to_2']:
            try:
                exposure =  soil_residue[formulation]*soil_ingestion_rate*mass_conversion_factor_g_ug
            except:
                exposure = "Invalid"
            exposure_profile.update('oral',formulation,'soil_ingestion',lifestage, exposure) 




    # Granule Ingestion
    granule_injestion_rate = 0.3 # g/day

    try:
        exposure = fraction_active_ingredient * granule_injestion_rate*mass_conversion_factor_mg_g
    except:
        exposure = "Invalid"
    exposure_profile.update('dietary','granules/pellets','granule_ingestion','1_to_2', exposure) 
    

    return exposure_profile         

