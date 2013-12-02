from collections import defaultdict
import math

transfer_coefficent=defaultdict(lambda : defaultdict(dict))
transfer_coefficent['OASS']['adult']=180000
transfer_coefficent['OASS']['1_to_2']=49000
transfer_coefficent['ORMS']['adult']=180000
transfer_coefficent['ORMS']['1_to_2']=49000
transfer_coefficent['Animal Barn']['adult']=6800
transfer_coefficent['Animal Barn']['3_to_6']=2700
exposure_time=defaultdict(lambda : defaultdict(dict))
exposure_time['OASS']['adult']=1.5
exposure_time['OASS']['1_to_2']=1.5
exposure_time['ORMS']['adult']=1.5
exposure_time['ORMS']['1_to_2']=1.5
exposure_time['Animal Barn']['adult']=4.0
exposure_time['Animal Barn']['3_to_6']=2.0

inhalation_rate =  defaultdict(float)
inhalation_rate['adult']=0.64
inhalation_rate['1_to_2']=0.33
inhalation_rate['3_to_6']=0.42

q_rate =  defaultdict(float)
q_rate['adult']=5400.
q_rate['1_to_2']=5400.

conversion_factor_mg_lb = 454000. # not 453592.370
conversion_factor_ft2_cm2 = 0.0010764263
conversion_factor_lb_g = 0.00220264
conversion_factor_mg_g = 1000.

from exposure_profile import ExposureProfile

def outdoor_misting(POD, LOC, bodyweight, dermal_absorption, inhalation_absorption, OASS_fraction_ai, OASS_amount_of_product_in_can, CCTM_amount_ai_in_product, ORMS_application_rate, ORMS_dilution_rate, ORMS_fraction_ai, AB_application_rate, AB_dilution_rate, AB_fraction_ai):
    exposure_profile = ExposureProfile(bodyweight, POD, LOC, dermal_absorption=dermal_absorption, inhalation_absorption=inhalation_absorption)
    
    try:
        OASS_application_rate = OASS_fraction_ai*OASS_amount_of_product_in_can*conversion_factor_mg_g*1
    except:
        OASS_application_rate = None
    
    for lifestage in ['adult','1_to_2']:
        exposure = OASS_application_rate * (inhalation_rate[lifestage] / q_rate[lifestage])
        exposure_profile.update('inhalation','Outdoor Misting','OASS',lifestage, exposure)


    try:
        OASS_deposited_residue = OASS_fraction_ai*OASS_amount_of_product_in_can*conversion_factor_lb_g*1/400.
    except:
        OASS_deposited_residue = None
    
    for lifestage in ['adult','1_to_2']:
        exposure = OASS_deposited_residue * 0.01 * transfer_coefficent['OASS'][lifestage]*exposure_time['OASS'][lifestage] * conversion_factor_mg_lb * conversion_factor_ft2_cm2
        exposure_profile.update('dermal','Outdoor Misting','OASS',lifestage, exposure)


    fraction_of_hand_mouthed = 0.13
    hand_surface_area = 150.
    replenishment_intervals = 4.
    saliva_extraction_factor = 0.48
    fraction_ai_on_hands=0.06
    hand_to_mouth_event_freqency = 13.9
    for lifestage in ['1_to_2']:  
        handloading =   fraction_ai_on_hands* exposure_profile.exposure['dermal']['Outdoor Misting']['OASS'][lifestage] /(2.*hand_surface_area) 
        exposure = handloading*fraction_of_hand_mouthed*hand_surface_area*1.5*4
        exposure *= (1. - ((1.-saliva_extraction_factor)**(hand_to_mouth_event_freqency/replenishment_intervals)))
        exposure_profile.update('oral','Outdoor Misting','OASS',lifestage, exposure)

    try:
        CCTM_emission_rate = CCTM_amount_ai_in_product*1./4.
    except:
        CCTM_emission_rate = None
    for lifestage in ['adult','1_to_2']:
        exposure = CCTM_emission_rate * (inhalation_rate[lifestage] / 4000.) * (2.3 - 51./4000.)
        exposure_profile.update('inhalation','Outdoor Misting','CCTM',lifestage, exposure)

    

    #ORMS

    if ORMS_application_rate is None or ORMS_application_rate == 0:
        ORMS_air_application_rate = ORMS_fraction_ai*ORMS_dilution_rate*0.014*1*8.34/1000. 
    else:
        ORMS_air_application_rate = ORMS_application_rate * ORMS_fraction_ai * 8.34 / (1000.*128.)
    initial_air_concentration = ORMS_air_application_rate*454000.*35.3
    r_value = math.exp(-((5400./90.6)*1.))

    for lifestage in ['adult','1_to_2']:
        exposure = initial_air_concentration * inhalation_rate[lifestage] *90.6 /5400.
        exposure*= ((int(2.3*1.))+((1-(r_value**((2.3*1.)-int(2.3*1))))/(1-r_value)))
        exposure_profile.update('inhalation','Outdoor Misting','ORMS',lifestage, exposure)        



    if ORMS_application_rate is None or ORMS_application_rate == 0:
        ORMS_ground_residue = (ORMS_fraction_ai*ORMS_dilution_rate*0.014*1*8.34 / 125.) * (454000/929.)
    else:
        ORMS_ground_residue = (AB_application_rate * AB_fraction_ai * 8.34 * 8 / (128.*1000.)) * (454000/929.)

    for lifestage in ['adult','1_to_2']:
        exposure = ORMS_ground_residue * 0.01 *1.5* transfer_coefficent['ORMS'][lifestage]
        exposure_profile.update('dermal','Outdoor Misting','ORMS',lifestage, exposure)

    hand_residue_loading = exposure_profile.exposure['dermal']['Outdoor Misting']['ORMS']['1_to_2']
    hand_residue_loading *= 0.06 / (2*150.)

    exposure = hand_residue_loading *0.127* 150 * 1.5 * 4 *(1 - ((1-.48)**(13.9/4.)))
    
    exposure_profile.update('oral','Outdoor Misting','ORMS','1_to_2', exposure)

    #Animal Barn
    if AB_application_rate is None or AB_application_rate == 0:
        AB_air_application_rate = AB_fraction_ai*AB_dilution_rate*0.014*1*8.34/1000. 
    else:
        AB_air_application_rate = AB_application_rate * AB_fraction_ai *  8.34 / (1000.*128)

    initial_air_concentration = AB_air_application_rate*454000.*35.3

    for lifestage in ['adult','3_to_6']:
        exposure = initial_air_concentration * inhalation_rate[lifestage] *1 *exposure_time['Animal Barn'][lifestage] /(4.0)
        exposure_profile.update('inhalation','Outdoor Misting','Animal Barn',lifestage, exposure)        


    if AB_application_rate is None or AB_application_rate == 0:
        AB_ground_residue = (AB_fraction_ai*AB_dilution_rate*0.014*1*8.34 / 125.) * (454000000/929.)
    else:
        AB_ground_residue = (AB_application_rate * AB_fraction_ai * 0.008 * 8.34 * 8 / 1000.) * (454000000/929.)

    for lifestage in ['adult','3_to_6']:
        exposure = AB_ground_residue * 0.08 * transfer_coefficent['Animal Barn'][lifestage] * exposure_time['Animal Barn'][lifestage] * 0.001
        exposure_profile.update('dermal','Outdoor Misting','Animal Barn',lifestage, exposure)

    hand_residue_loading = 0.15 * exposure_profile.exposure['dermal']['Outdoor Misting']['Animal Barn']['3_to_6'] / (2*225.)
    exposure = hand_residue_loading *0.13* 225 * 2 * 4 *(1 - ((1-.48)**(14./4.)))
    exposure_profile.update('oral','Outdoor Misting','Animal Barn','3_to_6', exposure)

    return exposure_profile

def outdoor_misting_handler(POD, LOC, bodyweight, dermal_absorption, inhalation_absorption, OASS_fraction_ai, OASS_amount_of_product_in_can, ORMS_drum_size, ORMS_dilution_rate, ORMS_fraction_ai, AB_drum_size, AB_dilution_rate, AB_fraction_ai):
    exposure_profile = ExposureProfile(bodyweight, POD, LOC, dermal_absorption=dermal_absorption, inhalation_absorption=inhalation_absorption)

    #oass
    application_rate = OASS_amount_of_product_in_can*OASS_fraction_ai*conversion_factor_lb_g*1
    dermal_exposure = application_rate*370.
    inhalation_exposure = application_rate*3.
    exposure_profile.update('dermal','General Handler','Misting: Outdoor Aerosol Space Sprays','adult', dermal_exposure)
    exposure_profile.update('inhalation','General Handler','Misting: Outdoor Aerosol Space Sprays','adult', inhalation_exposure)

    #orms
    application_rate = ORMS_fraction_ai*ORMS_dilution_rate*float(ORMS_drum_size)*1*8.34
    dermal_exposure = application_rate*0.232
    inhalation_exposure = application_rate*0.000219
    exposure_profile.update('dermal','General Handler','Misting: Outdoor Residential Misting System (Drum size: %s gallons)'%ORMS_drum_size,'adult', dermal_exposure)
    exposure_profile.update('inhalation','General Handler','Misting: Outdoor Residential Misting System (Drum size: %s gallons)'%ORMS_drum_size,'adult', inhalation_exposure)

    #ab
    application_rate = AB_fraction_ai*AB_dilution_rate*float(AB_drum_size)*1*8.34
    dermal_exposure = application_rate*0.232
    inhalation_exposure = application_rate*0.000219
    exposure_profile.update('dermal','General Handler','Misting: Animal Barns (Drum size: %s gallons)'%AB_drum_size,'adult', dermal_exposure)
    exposure_profile.update('inhalation','General Handler','Misting: Animal Barns (Drum size: %s gallons)'%AB_drum_size,'adult', inhalation_exposure)

    return exposure_profile
