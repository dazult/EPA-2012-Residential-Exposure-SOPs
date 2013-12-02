from collections import defaultdict
from math import exp

transfer_coefficent={'adult':6800.,'1_to_2':1800.}

exposure_time=defaultdict(lambda : defaultdict(dict))
exposure_time['Carpet']['adult']=8.
exposure_time['Hard surface']['adult']=2.
exposure_time['Carpet']['1_to_2']=4.
exposure_time['Hard surface']['1_to_2']=2.
exposure_time['Space Spray']['adult']=16.
exposure_time['Space Spray']['1_to_2']=18.

conversion_factor_mg_lb = 450000 # not 453592.370
conversion_factor_ft2_cm2 = 0.0010764263
conversion_factor_lb_g = 0.00220264
conversion_factor_mg_g = 1000.

fraction_transfered = {'Carpet':0.06,'Hard surface':0.08}
SA_bw_ratio = {'adult':280., '1_to_2':640.}
inhalation_rate = {'adult':0.64, '1_to_2':0.33}
from exposure_profile import ExposureProfile

def indoor(POD, LOC, bodyweight, dermal_absorption, inhalation_absorption, space_spray_fraction_ai, space_spray_amount_of_product, space_spray_restriction, molecular_weight, vapor_pressure,residues,matress_residue ):

    exposure_profile = ExposureProfile(bodyweight, POD, LOC, dermal_absorption=dermal_absorption, inhalation_absorption=inhalation_absorption)
    
    # inhalation_space_spray    
    application_rate = space_spray_fraction_ai*space_spray_amount_of_product*1000*0.25*0.0000022/33.
    
    air_exchange_rate = 0.45
    for lifestage in ['adult','1_to_2']:
        if space_spray_restriction == "NA":
            initial_concentration = application_rate*454000.
            exposure = (((initial_concentration*inhalation_rate[lifestage])/air_exchange_rate)*(1-(exp(-(2*air_exchange_rate)))))
        else:
            concentration_t = application_rate*454000.*exp(-float(space_spray_restriction)*1.26)
            exposure = (((concentration_t*inhalation_rate[lifestage])/air_exchange_rate)*(1-(exp(-(exposure_time['Space Spray'][lifestage]*air_exchange_rate)))))
        exposure_profile.update('inhalation','Indoor','Space Spray',lifestage, exposure)
    # inhalation_surface_directed screening level
    saturation_concentration = (molecular_weight*vapor_pressure*1000.*1000.)/(760.*0.0821*298.)
    exposure = 0.64*saturation_concentration*16.
    exposure_profile.update('inhalation','Surface Directed','','adult',exposure)
    exposure = 0.33*saturation_concentration*18.
    exposure_profile.update('inhalation','Surface Directed','','1_to_2',exposure)
    # deposited_residue  === not exposure
        # floors and carpets
        # mattresses
        # foggers 
        # space sprays    
    # indoor dermal
    for residue in residues:    
        for surface in ['Carpet','Hard surface']:
            sub_scenario = "%s (%s)" % (residue, surface)
            for lifestage in ['adult','1_to_2']:
                exposure = exposure_time[surface][lifestage]*0.001*transfer_coefficent[lifestage]*residues[residue]*fraction_transfered[surface]
                exposure_profile.update('dermal',sub_scenario,'',lifestage,exposure)
    
    for lifestage in ['adult','1_to_2']:
        exposure = matress_residue*exposure_time[surface][lifestage]*0.001*SA_bw_ratio[lifestage]*bodyweight[lifestage]*0.5*0.06*0.5
        exposure_profile.update('dermal','Mattress','', lifestage, exposure)        

    # indoor htm
    for residue in residues: 
        for surface in ['Carpet','Hard surface']:
            sub_scenario = "%s (%s)" % (residue, surface)
            hand_residue_loading = 0.15*exposure_profile.exposure['dermal']['Indoor'][sub_scenario]['1_to_2']/(2*150.)
            exposure = (hand_residue_loading*(0.13*150.)) * (exposure_time[surface]['1_to_2']*4.) * (1-((1-.48)**(20./4.)))
            exposure_profile.update('oral',sub_scenario, "hand_to_mouth",'1_to_2',exposure)
    
    # indoor otm
    for residue in residues: 
        for surface in ['Carpet','Hard surface']:
            sub_scenario = "%s (%s)" % (residue, surface)
            object_residue = residues[residue]*fraction_transfered[surface]
            exposure = (object_residue*0.001*10.)*(exposure_time[surface]['1_to_2']*4)*(1-((1-0.48)**(14./4.)))
            exposure_profile.update('oral',sub_scenario,object_to_mouth,'1_to_2',exposure)

    return exposure_profile
    

