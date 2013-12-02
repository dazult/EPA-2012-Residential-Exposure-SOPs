


from collections import defaultdict


#application_rate[formulation][scenario][application_method][application_type]
formulation_specific_AR = defaultdict(lambda : defaultdict(dict))
exposure_time = {'adult':3.7,'1_to_2':3.5}
application_frequency = {'with':0.25,'without':0.5}



formulations = ['Aerosol', 'Pump spray', 'Lotion','Towelette']
sunscreen_statii = ['without','with']

for sunscreen_status in sunscreen_statii:
    formulation_specific_AR[sunscreen_status]['Aerosol'] = 1.1
    formulation_specific_AR[sunscreen_status]['Pump spray'] = 0.62
    formulation_specific_AR[sunscreen_status]['Lotion'] = 2.0
    formulation_specific_AR[sunscreen_status]['Towelette'] = 1.1


def test():
    POD = {}
    LOC = {}
    POD['dermal'] = 1
    LOC['dermal'] = 1
    POD['oral'] = 1
    LOC['oral'] = 1
    SA_BW_ratio = {'1_to_2':640,'adult':280}
    body_weights_adults_options = [80, 69, 86] # kg
    bodyweight = {}
    bodyweight['adult'] = body_weights_adults_options[0]
    bodyweight['1_to_2'] = 11
    dermal_absorption = 1
    amount_ai = defaultdict(lambda : defaultdict(dict))
    for sunscreen_status in sunscreen_statii:
        amount_ai[sunscreen_status]['Aerosol'] = 1.1
        amount_ai[sunscreen_status]['Pump spray'] = 0.62
        amount_ai[sunscreen_status]['Lotion'] = 2.0
        amount_ai[sunscreen_status]['Towelette'] = 1.1
    print insect_repellent(POD, LOC, bodyweight, dermal_absorption, SA_BW_ratio, amount_ai )['RI']['oral']
from math import ceil

from exposure_profile import ExposureProfile

def insect_repellent(POD, LOC, bodyweight, dermal_absorption, SA_BW_ratio, amount_ai ):
    exposure_profile = ExposureProfile(bodyweight, POD, LOC, dermal_absorption=dermal_absorption) 
    fraction_body_exposed = 0.75
    for sunscreen_status in sunscreen_statii:
        for formulation in formulations:
            for lifestage in ['adult','1_to_2']:
                try:
                    exposure = ceil(max(1, exposure_time[lifestage] * application_frequency[sunscreen_status])) * amount_ai[sunscreen_status][formulation] * formulation_specific_AR[sunscreen_status][formulation] * SA_BW_ratio[lifestage] * fraction_body_exposed*bodyweight[lifestage]
                except:
                    exposure = "Invalid"
                exposure_profile.update('dermal',"%s sunscreen"%sunscreen_status,formulation,lifestage, exposure)
                

    fraction_of_hand_SA_mouthed = 0.127
    surface_area_one_hand = 150.
    saliva_extraction = .48
    HtM_events_per_hour = 13.9
    for sunscreen_status in sunscreen_statii:
        for formulation in formulations:
            for lifestage in ['1_to_2']:
                try:
                    nApplications = 1.0*ceil(max(1, exposure_time[lifestage] * application_frequency[sunscreen_status]))
                    exposure =  nApplications * amount_ai[sunscreen_status][formulation] * formulation_specific_AR[sunscreen_status][formulation] * surface_area_one_hand * fraction_of_hand_SA_mouthed * (1 - ((1 - saliva_extraction) **(HtM_events_per_hour*exposure_time[lifestage]/nApplications)))
                except:
                    exposure = "Invalid"
                exposure_profile.update('oral',"%s sunscreen"%sunscreen_status,formulation,lifestage, exposure)
                
    return exposure_profile



