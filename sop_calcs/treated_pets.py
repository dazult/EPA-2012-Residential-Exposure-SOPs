


default_pet_weights = {'cat':{},'dog':{}} #lb
default_pet_weights['dog'] = {'small':10.36535946,'medium':38.16827225,'large':76.50578234} #lb
default_pet_weights['cat'] = {'small':3.568299485,'medium':7.8300955,'large':16.13607146}
pet_weight = default_pet_weights['dog']['medium']
#Surface Area (cm2) = ((12.3*((BW (lb)*454)^0.65))
def pet_surface_area(lb):
    return 12.3*((lb*454)**0.65)


hours_of_exposure = {}
hours_of_exposure['adult'] = .77
hours_of_exposure['1_to_2'] = 1.

amount_applied = 10 # g input
fraction_ai = .01 # % input
ai_amount = amount_applied * fraction_ai * 1000. #mg ai



transfer_coefficient = {'liquid':{},'solid':{}}
transfer_coefficient['liquid']['pet'] = {}
transfer_coefficient['solid']['pet'] = {}
transfer_coefficient['liquid']['pet']['adult'] = 5200.
transfer_coefficient['solid']['pet']['adult'] = 140000.
transfer_coefficient['liquid']['pet']['1_to_2'] = 1400.
transfer_coefficient['solid']['pet']['1_to_2'] = 38000.

pet_Far = 0.02

pet_Fai_hands = {'solid':0.37,'liquid':0.04}
surface_area_of_1_to_2_hand = 150 #cm2
fraction_of_hand_mouthed = .13
replenishment_interval = 15. #min
n_replenishment_interval_per_hr = 60./replenishment_interval 
extraction_by_saliva = 0.48
htm_events_per_hr = 20 # note 13.9 in lawn sop

from exposure_profile import ExposureProfile

def treated_pets(POD, LOC, bodyweight, dermal_absorption, ai_amounts):
    exposure_profile = ExposureProfile(bodyweight, POD, LOC, dermal_absorption=dermal_absorption)    
    for formulation in transfer_coefficient:
        for pet in ['cat','dog']:
            for pet_size in ['small','medium','large']:
                pet_type = "%s %s" % (pet_size, pet)
                try:
                    transferable_residue = ai_amounts[pet][pet_size]*pet_Far/pet_surface_area(default_pet_weights[pet][pet_size]) #mg/cm2
                except:
                    transferable_residue = "Invalid"


                for lifestage in transfer_coefficient[formulation]['pet']:
                    try:
                        exposure = transferable_residue * transfer_coefficient[formulation]['pet'][lifestage] * hours_of_exposure[lifestage]
                    except:
                        exposure = "Invalid"
                    exposure_profile.update('dermal',formulation,pet_type,lifestage, exposure)


                for lifestage in ['1_to_2']:
                    hand_residue_loading = pet_Fai_hands[formulation]* exposure_profile.exposure['dermal'][formulation][pet_type][lifestage] / (2.0*surface_area_of_1_to_2_hand)
                    try:
                        exposure = hand_residue_loading * fraction_of_hand_mouthed * surface_area_of_1_to_2_hand * hours_of_exposure[lifestage] * n_replenishment_interval_per_hr *( 1 - ((1-extraction_by_saliva)**(htm_events_per_hr/n_replenishment_interval_per_hr)))
                    except:
                        exposure = "Invalid"
                    exposure_profile.update('oral', formulation, pet_type, lifestage, exposure)

    return exposure_profile
            

def test():
    POD = {}
    LOC = {}
    POD['oral'] = 1
    LOC['oral'] = 1
    POD['dermal'] = 1
    LOC['dermal'] = 1
    body_weights_adults_options = [80, 69, 86] # kg
    bodyweight = {}
    bodyweight['adult'] = body_weights_adults_options[0]
    bodyweight['1_to_2'] = 11
    dermal_absorption = 1   
    ai_amounts = {'cat':{'small':ai_amount,'medium':ai_amount,'large':ai_amount}, 'dog':{'small':ai_amount,'medium':ai_amount,'large':ai_amount}}             
    print treated_pets(POD, LOC, bodyweight, dermal_absorption, ai_amounts)
            

