from collections import defaultdict

class ExposureProfile(object):
    def __init__(self, bodyweight, POD, LOC, absorption = defaultdict(lambda: 1.0),dermal_absorption=1,inhalation_absorption=1):
        self.exposure = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(dict))))
        self.absorbed_dose = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(dict))))
        self.MOE = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(dict))))
        self.RI = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(dict))))
        self.bodyweight = bodyweight
        self.POD = POD
        self.LOC = LOC
        self.absorption = absorption
        self.exposure_routes = set()

        if dermal_absorption != 1:
            self.absorption['dermal']=dermal_absorption
        if inhalation_absorption != 1:
            self.absorption['inhalation']=inhalation_absorption        


    def update(self, route, scenario, sub_scenario, lifestage, exposure):
        self.exposure_routes.add(route)
        try:
            self.exposure[route][scenario][sub_scenario][lifestage] = exposure
        except Exception as e:
            self.exposure[route][scenario][sub_scenario][lifestage] = "Invalid"
        try:
            self.absorbed_dose[route][scenario][sub_scenario][lifestage] = self.absorption[route]*self.exposure[route][scenario][sub_scenario][lifestage] / self.bodyweight[lifestage]
        except Exception as e:
            self.absorbed_dose[route][scenario][sub_scenario][lifestage] = "Invalid"
        try:
            self.MOE[route][scenario][sub_scenario][lifestage] = self.POD[route]/self.absorbed_dose[route][scenario][sub_scenario][lifestage]
        except Exception as e:
            #raise(e)
            self.MOE[route][scenario][sub_scenario][lifestage] = "NaN"
        try:
            self.RI[route][scenario][sub_scenario][lifestage] = self.MOE[route][scenario][sub_scenario][lifestage]/self.LOC[route]
        except Exception as e:
            self.RI[route][scenario][sub_scenario][lifestage] = "NaN"
    
    def toDict(self):
        return {'exposure':self.exposure,'absorbed_dose':self.absorbed_dose,"MOE":self.MOE, "RI":self.RI}  

class RiskProfile(object):
    def __init__(self, exposure_routes):
        self.results = defaultdict(lambda : defaultdict(list)) 
        self.exposure_routes = exposure_routes

    def update(self, exposure_profile, SOP, duration):
        for exposure_route in self.exposure_routes.intersection(exposure_profile.exposure_routes):
            for formulation in exposure_profile.exposure[exposure_route]:
                for activity in exposure_profile.exposure[exposure_route][formulation]:
                    for lifestage in exposure_profile.exposure[exposure_route][formulation][activity]:                
                        if  float(exposure_profile.exposure[exposure_route][formulation][activity][lifestage])>0:
                            RI = exposure_profile.RI[exposure_route][formulation][activity][lifestage]
                            absorbed_dose = exposure_profile.absorbed_dose[exposure_route][formulation][activity][lifestage]
                            exposure = exposure_profile.exposure[exposure_route][formulation][activity][lifestage]
                            MOE = exposure_profile.MOE[exposure_route][formulation][activity][lifestage]
                            self.results[duration][lifestage].append((RI,exposure_route,formulation, activity,SOP,absorbed_dose,exposure,MOE))
