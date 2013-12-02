from collections import defaultdict

from exposure_profile import ExposureProfile
def paintsop(POD, LOC, bodyweight,dermal_absorption, SA_BW_ratio, surface_residue_concentration, fraction_of_body_exposed, daily_material_to_skin_transfer_efficency, exposure_time, hand_to_mouth_event_freqency):
    #hand_to_mouth_event_freqency 13.9 indoor 20 outdoor
    exposure_profile = ExposureProfile(bodyweight, POD, LOC, dermal_absorption=dermal_absorption) 
    
    
    for lifestage in ['adult','1_to_2']:
        try:
            exposure = surface_residue_concentration * SA_BW_ratio[lifestage] * fraction_of_body_exposed * daily_material_to_skin_transfer_efficency*bodyweight[lifestage]
        except:
            exposure = "Invalid"
        exposure_profile.update('dermal','paint','',lifestage, exposure)
        

    fraction_of_hand_mouthed = 0.13
    hand_surface_area = 150.
    replenishment_intervals = 4.
    saliva_extraction_factor = 0.48
    for lifestage in ['1_to_2']:
        try:

            exposure = surface_residue_concentration *  daily_material_to_skin_transfer_efficency * fraction_of_hand_mouthed * hand_surface_area * replenishment_intervals * exposure_time
            exposure *= (1. - ((1.-saliva_extraction_factor)**(hand_to_mouth_event_freqency/replenishment_intervals)))
        except:
            exposure = "Invalid"
        exposure_profile.update('oral','paint','',lifestage, exposure)

    return exposure_profile

def test():
    pass

#

