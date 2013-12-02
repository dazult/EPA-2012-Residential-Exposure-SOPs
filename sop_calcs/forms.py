from __future__ import absolute_import

import copy
import datetime
from itertools import chain
from urlparse import urljoin

from django.conf import settings
from django.forms.util import flatatt, to_current_timezone
from django.utils.datastructures import MultiValueDict, MergeDict
from django.utils.html import escape, conditional_escape
from django.utils.translation import ugettext, ugettext_lazy
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.safestring import mark_safe
from django.utils import datetime_safe, formats

from django import forms
import json

from collections import defaultdict

import operator


class CheckboxSelectMultipleBootstrap(forms.SelectMultiple):
    def __init__(self,attrs=None, choices=()):
        super(CheckboxSelectMultipleBootstrap, self).__init__(attrs, choices)
        self.choices_attrs = {}

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<div>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''
            choice_attrs = copy.copy(final_attrs)
            if option_value in self.choices_attrs:  
                choice_attrs.update(self.choices_attrs[option_value])
            cb = forms.CheckboxInput(choice_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<div><label%s class="checkbox inline">%s %s</label></div>' % (label_for, rendered_cb, option_label))
        output.append(u'</div>')
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_


class RadioFieldBootstrapRenderer(forms.widgets.RadioSelect.renderer):
    def render(self):
        """
        Outputs a <ul> for this set of choice fields.
        If an id was given to the field, it is applied to the <ul> (each
        item in the list will get an id of `$id_$i`).
        """
        id_ = self.attrs.get('id', None)
        start_tag = '<div id="%s" class="radio inline">'% id_ if id_ else '<div>'
        output = [start_tag]
        for widget in self:
            output.append(force_unicode(widget))
        output.append('</div>')
        return mark_safe('\n'.join(output))

class RadioSelectBootstrap(forms.widgets.RadioSelect):
    renderer = RadioFieldBootstrapRenderer




from sop_calcs.gardensandtrees import gardensandtrees
from sop_calcs.treated_pets import treated_pets
from sop_calcs.insect_repellent import insect_repellent
from sop_calcs.lawnturfsop import lawnturfsop
from sop_calcs.general_handler_sop import general_handler_sop
from sop_calcs.paintsop import paintsop
from sop_calcs.impregnated_materials import impregnated_materials
from sop_calcs.outdoor_misting import outdoor_misting, outdoor_misting_handler
from sop_calcs.indoor_envirnoments import indoor
from sop_calcs.exposure_profile import RiskProfile

class ResultsForm(forms.Form):
    title = "Assessment Background Information"  
    def __init__(self,*args,**kwargs):
        self.input_data = kwargs.pop('_input_data',None)
        super(ResultsForm,self).__init__(*args,**kwargs)

    def inputs(self):
        return self.input_data

    def lifestage_displays(self):
        lifestages = {}
        lifestages['adult'] = "Adult (All)"
        lifestages['adult_general'] = "Adult (All)"
        lifestages['adult_female'] = "Adult Female"
        lifestages['adult_male'] = "Adult Male"  
        lifestages['1_to_2'] = "1 < 2 year old"  
        lifestages['3_to_6'] = "3 < 6 year old"
        lifestages['6_to_11'] = "6 < 11 year old"
        lifestages['11_to_16'] = "11 < 16 year old"
        return lifestages

    def results(self):
        try:       
            s = json.loads(self.input_data)
            ss = ""
            RIs = defaultdict(lambda : defaultdict(list))
            exposure_routes = set(s['0']['exposure_routes'])
            

            exposure_scenarios = set(s['0']['exposure_scenarios'])
            body_weights_adults_options = [80., 69., 86.] # kg
            bodyweight = {}
            bodyweight['adult'] = 80.#body_weights_adults_options[0]
            bodyweight['adult_general'] = 80.
            bodyweight['adult_female'] = 69.
            bodyweight['adult_male'] = 86.
            pop_selection = "gen"
            amended_RIs = {}

            for duration in s['0']['exposure_durations']:
                amended_RIs[duration] = {}
            for target in s['0']['target_population']:
                if target == 'adult_female':
                    pop_selection = "adult_female"
                    bodyweight['adult'] = bodyweight['adult_female']
                elif target == 'adult_male':
                    pop_selection = "adult_male"
                    bodyweight['adult'] = bodyweight['adult_male']
                else:
                    pop_selection = "gen"      
                    bodyweight['adult'] = bodyweight['adult_general']     
                bodyweight['1_to_2'] = 11.
                bodyweight['3_to_6'] = 19.
                bodyweight['6_to_11'] = 32.
                bodyweight['11_to_16'] = 57.

                inhalation_rate = {}
                inhalation_rate['adult'] = 0.64
                inhalation_rate['1_to_2'] = 0.33
                inhalation_rate['3_to_6'] = 0.42
                SA_BW_ratio = {'1_to_2':640., 'adult':280.}

                risk_profile = RiskProfile(exposure_routes)
                
                for duration in s['0']['exposure_durations']:
                    ss += "<br>%s<br>" % duration
                    POD = {}
                    LOC = {}
                    absorption = {}

                    POD['dermal'] = s['1']['dermal_%s_%s_POD'%(duration,target)]
                    LOC['dermal'] = s['1']['dermal_%s_%s_LOC'%(duration,target)]

                    try:
                        POD['dermal'] = s['1']['dermal_%s_%s_POD'%(duration,target)]
                        LOC['dermal'] = s['1']['dermal_%s_%s_LOC'%(duration,target)]
                        absorption['dermal'] = s['1']['dermal_absorption']
                    except:
                        absorption['dermal'] = 1
                    try:
                        POD['inhalation'] = s['1']['inhalation_%s_%s_POD'%(duration,target)]
                        LOC['inhalation'] = s['1']['inhalation_%s_%s_LOC'%(duration,target)]
                        absorption['inhalation'] = s['1']['inhalation_absorption']
                    except:
                        absorption['inhalation'] = 1
                    try:
                        POD['oral'] = s['1']['oral_%s_%s_POD'%(duration,target)]        
                        LOC['oral'] = s['1']['oral_%s_%s_LOC'%(duration,target)]
                    except:
                        pass
                    try:
                        POD['dietary'] = s['1']['dietary_POD']
                        LOC['dietary'] = s['1']['dietary_LOC']
                    except:
                        pass



                    
                    if s['3'] != None and 'generalhandler' in exposure_scenarios: #generalhandler
                        SOP = "General Handler"
                        combining_dermal_inhalation = [] 
                        #application_rate[formulation][scenario][application_method][application_type]
                        application_rate = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))  
                             
                        for formulation in GeneralHandlerForm.application_rate_form_map: 
                            for scenario in GeneralHandlerForm.application_rate_form_map[formulation]: 
                                for application_method in GeneralHandlerForm.application_rate_form_map[formulation][scenario]:
                                    for application_type in GeneralHandlerForm.application_rate_form_map[formulation][scenario][application_method]:
                                        if GeneralHandlerForm.application_rate_form_map[formulation][scenario][application_method][application_type] in s['3']:
                                            application_rate[formulation][scenario][application_method][application_type] = s['3'][GeneralHandlerForm.application_rate_form_map[formulation][scenario][application_method][application_type]]
                                        else: 
                                            application_rate[formulation][scenario][application_method][application_type] = 0                
                        results = general_handler_sop(POD, LOC, bodyweight, absorption, application_rate)
                        
                        risk_profile.update(results, SOP, duration)
                        

                    if s['4'] != None and 'generalhandler' in exposure_scenarios and 'generalhandler' in exposure_scenarios: #misting - handler
                        SOP = "General Handler"
                        OASS_fraction_ai = s['4']['OASS_fraction_ai']
                        OASS_amount_of_product_in_can = s['4']['OASS_amount_of_product_in_can']
                        ORMS_drum_size = s['4']['ORMS_drum_size']
                        ORMS_dilution_rate = s['4']['ORMS_dilution_rate']
                        ORMS_fraction_ai = s['4']['ORMS_fraction_ai']
                        AB_drum_size = s['4']['AB_drum_size']
                        AB_dilution_rate = s['4']['AB_dilution_rate']
                        AB_fraction_ai = s['4']['AB_fraction_ai']
                        
                        results = outdoor_misting_handler(POD, LOC, bodyweight, absorption['dermal'], absorption['inhalation'], OASS_fraction_ai, OASS_amount_of_product_in_can, ORMS_drum_size, ORMS_dilution_rate, ORMS_fraction_ai, AB_drum_size, AB_dilution_rate, AB_fraction_ai)
                        
                        risk_profile.update(results, SOP, duration)
                        
                    if s['5'] != None and 'treatedpet' in exposure_scenarios: #treatedpet
                        SOP = "Treated Pets" 
                        ai_amounts = {}
                        amount_applied_form_map = TreatedPetForm.amount_applied_form_map
                        for animal in ['cat','dog']:
                            ai_amounts[animal] = {}
                            for size in ['small','medium','large']:
                                ai_amounts[animal][size] = s['5'][TreatedPetForm.amount_applied_form_map[animal][size]]*s['5']['fraction_ai']*1000.
                        results = treated_pets(POD, LOC, bodyweight, absorption['dermal'], ai_amounts)
                        risk_profile.update(results, SOP, duration)



                    if s['6'] != None and 'lawn' in exposure_scenarios: #lawn
                        SOP = "Lawns and Turf"
                        fraction_active_ingredient = s['6']['fraction_ai_in_pellets']
                        ttr = {'liquid':s['6']['liquid_ttr_conc'], 'solid':s['6']['solid_ttr_conc']}
                        application_rate = {'liquid':s['6']['liquid_application_rate'],'solid':s['6']['solid_application_rate']} # lb ai / acre
                        results = lawnturfsop(POD, LOC,  bodyweight, absorption['dermal'], application_rate, ttr, fraction_active_ingredient)
                        risk_profile.update(results, SOP, duration)


                    if s['7'] != None and 'garden' in exposure_scenarios: #gardensandtrees 
                        SOP = "Gardens and Trees"
                        dfr = {'liquid':s['7']['liquid_dfr_conc'], 'solid':s['7']['solid_dfr_conc']}
                        application_rate = {'liquid':s['7']['liquid_application_rate'],'solid':s['7']['solid_application_rate']} # lb ai / acre
                        results = gardensandtrees(POD, LOC, bodyweight, absorption['dermal'], application_rate, dfr)
                        #return "Here1"
                        risk_profile.update(results, SOP, duration)
                    #return exposure_scenarios


                    if s['8'] != None and 'insect' in exposure_scenarios: #insect
                        SOP = "Insect Repellents"        
                        amount_ai = defaultdict(lambda : defaultdict(dict))
                        for sunscreen_status in ['without','with']: 
                            for formulation in InsectRepellentsForm.formulations:
                                amount_ai[sunscreen_status][formulation] = s['8'][InsectRepellentsForm.amount_ai_formulations_form_map[sunscreen_status][formulation]]
                        results = insect_repellent(POD, LOC, bodyweight, absorption['dermal'], SA_BW_ratio, amount_ai )
                        risk_profile.update(results, SOP, duration)
                        
                                       
                    if s['9'] != None and 'paint' in exposure_scenarios: #paint 
                        SOP = "Paint and Preservatives"       
                        surface_residue_concentration = s['9']['surface_residue_concentration']
                        fraction_of_body_exposed = PaintsAndPreservativesForm.DEFAULT_FRACTION_OF_BODY_EXPOSED#s['9']['fraction_of_body_exposed']
                        daily_material_to_skin_transfer_efficency = PaintsAndPreservativesForm.DEFAULT_DAILY_MATERIAL_TO_SKIN_TRANSFER_EFFICENCY#s['9']['daily_material_to_skin_transfer_efficency'] 
                        exposure_time = PaintsAndPreservativesForm.EXPOSURE_TIME[s['9']['indoor_or_outdoor']]#s['9']['exposure_time']
                        hand_to_mouth_event_freqency = PaintsAndPreservativesForm.HAND_TO_MOUTH_EVENTS_PER_HOUR[s['9']['indoor_or_outdoor']]#s['9']['hand_to_mouth_event_frequency']
                        results = paintsop(POD, LOC, bodyweight, absorption['dermal'], SA_BW_ratio, surface_residue_concentration, fraction_of_body_exposed, daily_material_to_skin_transfer_efficency, exposure_time, hand_to_mouth_event_freqency )
                        risk_profile.update(results, SOP, duration)
                        
                        
                                       

                    if s['10'] != None and 'impregnated_materials' in exposure_scenarios: #impregnated_materials  
                        SOP = "Impregnated Materials"  
            
                        surface_residue_concentration = s['10']['surface_residue_concentration']
                        weight_fraction = s['10']['weight_fraction_of_active_ingredient']
                        material_type = s['10']['material_type']
                        
                        if surface_residue_concentration is None or surface_residue_concentration == 0:
                            surface_residue_concentration = weight_fraction*ImpregnatedMaterialsForm.MATERIAL_WEIGHT_TO_SURFACE_AREA_DENSITY[material_type]
                        
                        body_fraction_exposed_type = s['10']['body_fraction_exposed_type']
                        
                        fraction_of_body_exposed = ImpregnatedMaterialsForm.BODY_FRACTION_EXPOSED[body_fraction_exposed_type]#s['10']['fraction_of_body_exposed']
                        
                        protective_barrier_present = s['10']['protective_barrier_present']
                        protection_factor = ImpregnatedMaterialsForm.PROTECTION_FACTOR[protective_barrier_present]
                        #HtM
                        type_of_flooring = s['10']['type_of_flooring']
                        fraction_of_ai_transferred_to_hands = ImpregnatedMaterialsForm.FRACTION_AI_HAND_TRANSFER[type_of_flooring]
                        hand_exposure_time = ImpregnatedMaterialsForm.FLOOR_EXPOSURE_TIME[type_of_flooring]

                        daily_material_to_skin_transfer_efficency = ImpregnatedMaterialsForm.FRACTION_AI_HAND_TRANSFER[type_of_flooring]
                        #daily_material_to_skin_transfer_efficency = ImpregnatedMaterialsForm.DEFAULT_DAILY_MATERIAL_TO_SKIN_TRANSFER_EFFICENCY
                        indoor_or_outdoor = s['10']['indoor_or_outdoor'] 
                        object_exposure_time = ImpregnatedMaterialsForm.EXPOSURE_TIME[indoor_or_outdoor]
                        hand_to_mouth_event_freqency = ImpregnatedMaterialsForm.HAND_TO_MOUTH_EVENTS_PER_HOUR[indoor_or_outdoor]
                        
                        #daily_material_to_skin_transfer_efficency = forms.FloatField(required=False,initial=0.14)
                        #OtM
                        FRACTION_AI_HAND_TRANSFER = {'':0., 'carpet':0.06,'hard':0.08}
                        fraction_of_residue_on_object = ImpregnatedMaterialsForm.FRACTION_AI_HAND_TRANSFER[type_of_flooring]
                        object_to_mouth_event_frequency = ImpregnatedMaterialsForm.OBJECT_TO_MOUTH_EVENTS_PER_HOUR[indoor_or_outdoor] 

                        
                        results = impregnated_materials(POD, LOC, bodyweight, absorption['dermal'], SA_BW_ratio, surface_residue_concentration, fraction_of_body_exposed, daily_material_to_skin_transfer_efficency, protection_factor, fraction_of_ai_transferred_to_hands, hand_exposure_time, hand_to_mouth_event_freqency, fraction_of_residue_on_object, object_exposure_time, object_to_mouth_event_frequency)
                        
                        risk_profile.update(results, SOP, duration)
                        
                        
                                        

                    if s['11'] != None and 'indoor' in exposure_scenarios: #indoor   
                        SOP = "Indoor"
                        space_spray_fraction_ai = s['11']['space_spray_fraction_ai']   
                        space_spray_amount_of_product = s['11']['space_spray_amount_of_product']  
                        space_spray_restriction = s['11']['space_spray_restriction']  
                        molecular_weight = s['11']['molecular_weight']  
                        vapor_pressure = s['11']['vapor_pressure'] 

                        residues = {} 
                        residues['broadcast'] = s['11']['broadcast_residue'] 
                        residues['perimeter/spot/bedbug (coarse)'] = s['11']['coarse_residue']
                        residues['perimeter/spot/bedbug (pin stream)'] = s['11']['pin_stream_residue']
                        residues['cracks and crevices'] = s['11']['crack_and_crevice_residue']
                        residues['foggers'] = s['11']['foggers_residue']
                        residues['space sprays'] = s['11']['space_sprays_residue']

                        matress_residue = s['11']['matress_residue'] 
                        results = indoor(POD, LOC, bodyweight, absorption['dermal'], absorption['inhalation'], space_spray_fraction_ai, space_spray_amount_of_product, space_spray_restriction, molecular_weight, vapor_pressure,residues,matress_residue)
                        risk_profile.update(results, SOP, duration)
                    if s['12'] != None and 'misting' in exposure_scenarios: #misting
                        SOP = "Misting"
                        OASS_fraction_ai = s['12']['OASS_fraction_ai']  
                        OASS_amount_of_product_in_can = s['12']['OASS_amount_of_product_in_can']  
                        CCTM_amount_ai_in_product= s['12']['CCTM_amount_ai_in_product']  
                        ORMS_application_rate= s['12']['ORMS_application_rate']  
                        ORMS_dilution_rate= s['12']['ORMS_dilution_rate'] 
                        ORMS_fraction_ai= s['12']['ORMS_fraction_ai'] 
                        AB_application_rate= s['12']['AB_application_rate'] 
                        AB_dilution_rate = s['12']['AB_dilution_rate'] 
                        AB_fraction_ai = s['12']['AB_fraction_ai'] 
                        results = outdoor_misting(POD, LOC, bodyweight, absorption['dermal'], absorption['inhalation'], OASS_fraction_ai, OASS_amount_of_product_in_can, CCTM_amount_ai_in_product, ORMS_application_rate, ORMS_dilution_rate, ORMS_fraction_ai, AB_application_rate, AB_dilution_rate, AB_fraction_ai)
                        risk_profile.update(results, SOP, duration)



                sorted_RIs = {}
                ri_id=0

                for duration in risk_profile.results:

                    sorted_RIs[duration] = {}

                    for lifestage in risk_profile.results[duration]:
                        lifestage_final = lifestage
                        if pop_selection != "gen" and lifestage != 'adult':
                            continue
                        elif pop_selection != "gen":
                            lifestage_final = pop_selection
                        sorted_RIs[duration][lifestage_final] = risk_profile.results[duration][lifestage]
                        sorted_RIs[duration][lifestage_final].sort()
                        amended_RIs[duration][lifestage_final] = []
                        for l in sorted_RIs[duration][lifestage_final]:
                            n = list(l)
                            n.append(ri_id)
                            ri_id+=1
                            amended_RIs[duration][lifestage_final].append(n)
            
            return amended_RIs
        
        except Exception as e:
            return e, str(e)



class IngredientOverviewForm(forms.Form):
    calls = 0
    title = "Assessment Background Information"    
    active_ingredient = forms.CharField(required=False)
    #GardenAndTreesForm, InsectRellentsForm, PaintsAndPreservativesForm
    SCENARIOS = [('generalhandler','Handler/Applicator (all scenarios)'),('insect','Insect Repellents'),('treatedpet','Treated Pets'),('lawn','Lawns/Turf'),('garden','Gardens And Trees'),('paint','Paints And Preservatives'),('impregnated_materials','Impregnated Materials'), ('indoor','Indoor'),('misting','Outdoor Misting ')] 
    exposure_scenarios = forms.MultipleChoiceField(choices=SCENARIOS, widget=CheckboxSelectMultipleBootstrap())
    ROUTES = [('oral', 'Incidental Oral'), ('dermal', 'Dermal'), ('inhalation', 'Inhalation') , ('dietary', 'Granule/Pellet Ingestion')] 
    exposure_routes = forms.MultipleChoiceField(choices=ROUTES, widget=CheckboxSelectMultipleBootstrap(), initial = ['oral','dermal','inhalation','dietary'])
    DURATIONS = [('short','Short-Term'),('intermediate','Intermediate-Term'),('long','Long-Term')]
    exposure_durations = forms.MultipleChoiceField(choices=DURATIONS , widget=CheckboxSelectMultipleBootstrap())
    TARGET_POP_CHOICES = [('gen','General Population (Adults + Children)'),('adult_female','Adult (Female Only)'),('adult_male','Adult (Male Only)')]
    TARGET_POP_CHOICES_DICT = {}
    for choice in TARGET_POP_CHOICES:
        TARGET_POP_CHOICES_DICT[choice[0]] = choice[1]
    target_population =  forms.MultipleChoiceField(choices=TARGET_POP_CHOICES , widget=CheckboxSelectMultipleBootstrap(),initial=['gen'])



    def __init__(self,*args,**kwargs):
        super(IngredientOverviewForm,self).__init__(*args,**kwargs)
        IngredientOverviewForm.calls += 1
        

    def clean(self):
        
        cleaned_data = super(IngredientOverviewForm, self).clean()
        exposure_scenarios = cleaned_data.get("exposure_scenarios")
        exposure_routes = cleaned_data.get("exposure_routes")

        if exposure_routes and exposure_scenarios:
            if 'dermal' in exposure_routes:
                return cleaned_data

            if 'oral' in exposure_routes:
                if True in [scenario in exposure_scenarios for scenario in ['lawn','insect','paint','treatedpet','indoor','impregnated_materials', 'misting']]:
                    return cleaned_data

            if 'inhalation' in exposure_routes:
                if True in [scenario in exposure_scenarios for scenario in ['indoor','misting','generalhandler']]:
                    return cleaned_data

            if 'dietary' in exposure_routes:
                if True in [scenario in exposure_scenarios for scenario in ['lawn']]:
                    return cleaned_data

            raise forms.ValidationError("No combinations of these routes and scenarios exist.")

        return cleaned_data

class ToxForm(forms.Form):
    calls = 0
    title = "Toxicological Information"
    POD_STUDY_CHOICES = [('',''),('route-specific','Route-specific'),('oral','Oral')]

    ABS_STUDY_CHOICES = [('',''), ('human-study', 'Human Study'),  ('animal-study', 'Animal Study'), ('POD or LOAEL/NOAEL comparison','Estimated by POD or LOAEL/NOAEL comparison'),('in vitro study','In vitro study'),('other','Other')]

    TARGET_POP_CHOICES = [('gen','General Population (Adults + Children)'),('adult_female','Adult (Female Only)'),('adult_male','Adult (Male Only)')]
    TARGET_POP_CHOICES_DICT = {}
    for choice in TARGET_POP_CHOICES:
        TARGET_POP_CHOICES_DICT[choice[0]] = choice[1]
    
    def __init__(self,*args,**kwargs):
        
        
        data = kwargs.pop('data_from_step_1',None) 
        self.data_from_step_1 = data 
        super(ToxForm,self).__init__(*args, **kwargs)
        
        self.data_from_step_1 = self.initial['data_from_step_1']
        ToxForm.calls += 1   
        logger.error("ToxForm __init__ calls: %s "%ToxForm.calls)
        
        if self.data_from_step_1:
            
            if 'dermal' in self.data_from_step_1['exposure_routes']:
                self.fields['dermal_absorption'] = forms.FloatField(required=False, initial=1, label="Dermal Absorption (0-1)",min_value=0., max_value=1.)
                self.fields['dermal_absorption_study'] = forms.ChoiceField(choices=ToxForm.ABS_STUDY_CHOICES,required=False,label="Dermal Absorption Study")

                self.fields['dermal_POD_study'] = forms.ChoiceField(choices=ToxForm.POD_STUDY_CHOICES,required=False,label="Dermal POD Study" )
            for duration in self.data_from_step_1['exposure_durations']:
                if 'dermal' in self.data_from_step_1['exposure_routes']:                    
                    for target in self.data_from_step_1['target_population']:
                        self.fields['dermal_%s_%s_POD'%(duration,target)] = forms.FloatField(required=False, min_value=0.,label="%s Term Dermal POD (mg/kg/day) (%s)"%(duration.capitalize(), ToxForm.TARGET_POP_CHOICES_DICT[target]) )
                        
                        self.fields['dermal_%s_%s_LOC'%(duration,target)] = forms.FloatField(required=False, initial=100, min_value=0.,label="%s Term Dermal LOC (%s)"%(duration.capitalize(), ToxForm.TARGET_POP_CHOICES_DICT[target]) )

                if True in [scenario in self.data_from_step_1['exposure_scenarios'] for scenario in ['lawn','insect','paint','treatedpet','indoor','impregnated_materials','misting']] and 'oral' in self.data_from_step_1['exposure_routes']:
                    for target in self.data_from_step_1['target_population']:
                        self.fields['oral_%s_%s_POD'%(duration,target)] = forms.FloatField(required=False, min_value=0.,label="%s Term Oral POD (mg/kg/day) (%s)"%(duration.capitalize(), ToxForm.TARGET_POP_CHOICES_DICT[target]))
                        self.fields['oral_%s_%s_LOC'%(duration,target)] = forms.FloatField(required=False, initial=100, min_value=0., label="%s Term Oral LOC (%s)"%(duration.capitalize(), ToxForm.TARGET_POP_CHOICES_DICT[target]))

            if True in [scenario in self.data_from_step_1['exposure_scenarios'] for scenario in ['indoor','misting','generalhandler']] and 'inhalation' in self.data_from_step_1['exposure_routes']:
                self.fields['inhalation_absorption'] = forms.FloatField(required=False, initial=1, label="Inhalation Absorption (0-1)",min_value=0., max_value=1.)
                self.fields['inhalation_absorption_study'] =  forms.ChoiceField(choices=ToxForm.ABS_STUDY_CHOICES,required=False,label="Inhalation Absorption Study")
                self.fields['inhalation_POD_study'] = forms.ChoiceField(choices=ToxForm.POD_STUDY_CHOICES,required=False, label="Inhalation POD Study")
            for duration in self.data_from_step_1['exposure_durations']:
                if True in [scenario in self.data_from_step_1['exposure_scenarios'] for scenario in ['indoor','misting','generalhandler']] and 'inhalation' in self.data_from_step_1['exposure_routes']:
                    
                    for target in self.data_from_step_1['target_population']:
                        self.fields['inhalation_%s_%s_POD'%(duration,target)] = forms.FloatField(required=False, min_value=0.,label="%s Term Inhalation POD (mg/kg/day) (%s)"%(duration.capitalize(), ToxForm.TARGET_POP_CHOICES_DICT[target]))

                        self.fields['inhalation_%s_%s_LOC'%(duration,target)] = forms.FloatField(required=False, initial=100, min_value=0.,label="%s Term Inhalation LOC (%s)"%(duration.capitalize(), ToxForm.TARGET_POP_CHOICES_DICT[target]))

            if 'lawn' in self.data_from_step_1['exposure_scenarios'] and 'dietary' in self.data_from_step_1['exposure_routes']:
                if 'gen' in self.data_from_step_1['target_population']:
                    self.fields['dietary_POD'] = forms.FloatField(required=False, min_value=0.,label="Dietary POD (mg/kg/day) (Children)")
                    self.fields['dietary_LOC'] = forms.FloatField(required=False, initial=100,min_value=0., label="Dietary LOC (Children)")
        #assert(self.data_from_step_1, Exception(self.data_from_step_1))
        #raise Exception(self.data_from_step_1)

    def clean(self, *args, **kwargs):        
        cleaned_data = super(ToxForm, self).clean()
    
        for route in self.data_from_step_1['exposure_routes']:
            if '%s_absorption'%(route) in self.fields:
                absorption = cleaned_data.get('%s_absorption'%(route))
                pod_study = cleaned_data.get('%s_POD_study'%(route))
                if pod_study == 'route-specific' and absorption != 1:
                    msg = u"Absorption must be 1 for route specific POD studies."
                    self._errors['%s_absorption'%(route)] = self.error_class([msg])
                    self._errors['%s_POD_study'%(route)] = self.error_class([msg])

                    del cleaned_data['%s_POD_study'%(route)]
                    if '%s_absorption'%(route) in cleaned_data:
                        del cleaned_data['%s_absorption'%(route)]
        # Always return the full collection of cleaned data.
        return cleaned_data




class GeneralHandlerForm(forms.Form):
    title = "General Handler Data Entry Form"
    application_rate = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))
    application_rate_units = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))
    application_rate_form_map = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))


    application_rate['Dust/Powder']['Indoor Environment']['Plunger Duster']['Broadcast; Perimeter/Spot/ Bedbug (course application)'] = 0
    application_rate['Dust/Powder']['Gardens / Trees']['Plunger Duster'][''] = 0
    application_rate['Dust/Powder']['Indoor Environment']['Bulb duster']['Perimeter/Spot/Bedbug; Crack and Crevice'] = 0
    application_rate['Dust/Powder']['Gardens / Trees']['Bulb duster'][''] = 0
    application_rate['Dust/Powder']['Indoor Environment']['Electric/power duster']['Broadcast; Perimeter/Spot/ Bedbug (course application)'] = 0
    application_rate['Dust/Powder']['Gardens / Trees']['Electric/power duster'][''] = 0
    application_rate['Dust/Powder']['Indoor Environment']['Hand crank duster']['Broadcast; Perimeter/Spot/ Bedbug (course application)'] = 0
    application_rate['Dust/Powder']['Gardens / Trees']['Hand crank duster'][''] = 0
    application_rate['Dust/Powder']['Indoor Environment']['Shaker can']['Broadcast'] = 0
    application_rate['Dust/Powder']['Indoor Environment']['Shaker can']['Broadcast; Perimeter/Spot/ Bedbug (course application)'] = 0
    application_rate['Dust/Powder']['Gardens / Trees']['Shaker can']['can'] = 0
    application_rate['Dust/Powder']['Gardens / Trees']['Shaker can']['ft2'] = 0
    application_rate['Liquid concentrate']['Indoor Environment']['Manually-pressurized handwand (w/ or w/o pin stream nozzle)']['Broadcast, Perimeter/Spot/ Bedbug (course application); Perimeter /Spot/ Bedbug (pinstream application); Crack and Crevice'] = 0
    application_rate['Liquid concentrate']['Gardens / Trees']['Manually-pressurized handwand']['ft2'] = 0
    application_rate['Liquid concentrate']['Gardens / Trees']['Manually-pressurized handwand']['gallons'] = 0
    application_rate['Liquid concentrate']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 0
    application_rate['Liquid concentrate']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 0
    application_rate['Liquid concentrate']['Lawns / Turf']['Hose-end Sprayer'][''] = 0
    application_rate['Liquid concentrate']['Lawns / Turf']['Manually-pressurized handwand'][''] = 0
    application_rate['Liquid concentrate']['Gardens / Trees']['Backpack']['ft2'] = 0
    application_rate['Liquid concentrate']['Gardens / Trees']['Backpack']['gallons'] = 0
    application_rate['Liquid concentrate']['Gardens / Trees']['Sprinkler can']['ft2'] = 0
    application_rate['Liquid concentrate']['Gardens / Trees']['Sprinkler can']['gallons'] = 0
    application_rate['Liquid concentrate']['Lawns / Turf']['Sprinkler can'][''] = 0
    application_rate['Ready-to-use']['Indoor Environment']['Aerosol can']['Broadcast Surface Spray'] = 0
    application_rate['Ready-to-use']['Indoor Environment']['Aerosol can']['Perimeter/ Spot/ Bedbug (course application)'] = 0
    application_rate['Ready-to-use']['Indoor Environment']['Aerosol can with pin stream nozzle']['Perimeter/ Spot/ Bedbug (pin stream application); Crack and Crevice'] = 0
    application_rate['Ready-to-use']['Indoor Environment']['Aerosol can']['Space spray'] = 0
    application_rate['Ready-to-use']['Gardens / Trees']['Aerosol can'][''] = 0
    application_rate['Ready-to-use']['Lawns / Turf']['Aerosol can'][''] = 0
    application_rate['Ready-to-use']['Indoor Environment']['Trigger-spray bottle']['Broadcast'] = 0
    application_rate['Ready-to-use']['Indoor Environment']['Trigger-spray bottle']['Perimeter/ Spot/ Bedbug (course application)'] = 0

    application_rate['Ready-to-use']['Insect Repellent']['Aerosol can'][''] = 0
    application_rate['Ready-to-use']['Insect Repellent']['Trigger-spray bottle'][''] = 0


    application_rate['Ready-to-use']['Gardens / Trees']['Trigger-spray bottle'][''] = 0
    application_rate['Ready-to-use']['Lawns / Turf']['Trigger-spray bottle'][''] = 0
    application_rate['Ready-to-use']['Indoor Environment']['Bait (granular, hand dispersal)'][''] = 0
    application_rate['Ready-to-use']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 0
    application_rate['Ready-to-use']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 0
    application_rate['Ready-to-use']['Lawns / Turf']['Hose-end Sprayer'][''] = 0
    application_rate['Wettable powders']['Indoor Environment']['Manually-pressurized handwand (w/ or w/o pin stream nozzle)']['Broadcast, Perimeter/Spot/ Bedbug (course application); Perimeter /Spot/ Bedbug (pinstream application); Crack and Crevice'] = 0
    application_rate['Liquid concentrate']['Lawns / Turf']['Backpack'][''] = 0
    application_rate['Wettable powders']['Gardens / Trees']['Manually-pressurized handwand']['ft2'] = 0
    application_rate['Wettable powders']['Gardens / Trees']['Manually-pressurized handwand']['gallons'] = 0
    application_rate['Wettable powders']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 0
    application_rate['Wettable powders']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 0
    application_rate['Wettable powders']['Lawns / Turf']['Hose-end Sprayer'][''] = 0
    application_rate['Wettable powders']['Lawns / Turf']['Manually-pressurized handwand'][''] = 0
    application_rate['Wettable powders']['Gardens / Trees']['Backpack']['ft2'] = 0
    application_rate['Wettable powders']['Gardens / Trees']['Backpack']['gallons'] = 0
    application_rate['Wettable powders']['Gardens / Trees']['Sprinkler can']['ft2'] = 0
    application_rate['Wettable powders']['Gardens / Trees']['Sprinkler can']['gallons'] = 0
    application_rate['Wettable powders']['Lawns / Turf']['Sprinkler can'][''] = 0
    application_rate['Wettable powders in water-soluble packaging']['Indoor Environment']['Manually-pressurized handwand (w/ or w/o pin stream nozzle)']['Broadcast, Perimeter/Spot/ Bedbug (course application); Perimeter /Spot/ Bedbug (pinstream application); Crack and Crevice'] = 0
    application_rate['Wettable powders']['Lawns / Turf']['Backpack'][''] = 0
    application_rate['Wettable powders in water-soluble packaging']['Gardens / Trees']['Manually-pressurized handwand']['ft2'] = 0
    application_rate['Wettable powders in water-soluble packaging']['Gardens / Trees']['Manually-pressurized handwand']['gallons'] = 0
    application_rate['Wettable powders in water-soluble packaging']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 0
    application_rate['Wettable powders in water-soluble packaging']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 0
    application_rate['Wettable powders in water-soluble packaging']['Lawns / Turf']['Hose-end Sprayer'][''] = 0
    application_rate['Wettable powders in water-soluble packaging']['Lawns / Turf']['Manually-pressurized handwand'][''] = 0
    application_rate['Wettable powders in water-soluble packaging']['Lawns / Turf']['Backpack'][''] = 0
    application_rate['Wettable powders in water-soluble packaging']['Gardens / Trees']['Sprinkler can']['ft2'] = 0
    application_rate['Wettable powders in water-soluble packaging']['Gardens / Trees']['Sprinkler can']['gallons'] = 0
    application_rate['Wettable powders in water-soluble packaging']['Lawns / Turf']['Sprinkler can'][''] = 0
    application_rate['Wettable powders in water-soluble packaging']['Gardens / Trees']['Backpack'][''] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Lawns / Turf']['Manually-pressurized handwand'][''] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Lawns / Turf']['Hose-end Sprayer'][''] = 0
    application_rate['Wettable powders in water-soluble packaging']['Gardens / Trees']['Backpack'][''] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Manually-pressurized handwand']['ft2'] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Manually-pressurized handwand']['gallons'] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Lawns / Turf']['Backpack'][''] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Sprinkler can']['ft2'] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Sprinkler can']['gallons'] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Lawns / Turf']['Sprinkler can'][''] = 0
    application_rate['Granule']['Gardens / Trees']['Push-type rotary spreader'][''] = 0
    application_rate['Granule']['Lawns / Turf']['Push-type rotary spreader'][''] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Backpack']['ft2'] = 0
    application_rate['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Backpack']['gallons'] = 0
    application_rate['Granule']['Lawns / Turf']['Belly grinder'][''] = 0
    application_rate['Granule']['Gardens / Trees']['Spoon'][''] = 0
    application_rate['Granule']['Lawns / Turf']['Spoon'][''] = 0
    application_rate['Granule']['Gardens / Trees']['Cup'][''] = 0
    application_rate['Granule']['Lawns / Turf']['Cup'][''] = 0
    application_rate['Granule']['Gardens / Trees']['Hand dispersal'][''] = 0
    application_rate['Granule']['Lawns / Turf']['Hand dispersal'][''] = 0
    application_rate['Granule']['Gardens / Trees']['Shaker can']['can'] = 0
    application_rate['Granule']['Gardens / Trees']['Shaker can']['ft2'] = 0
    application_rate['Granule']['Lawns / Turf']['Shaker can'][''] = 0
    application_rate['Microencapsulated']['Gardens / Trees']['Manually-pressurized handwand']['ft2'] = 0
    application_rate['Microencapsulated']['Gardens / Trees']['Manually-pressurized handwand']['gallons'] = 0
    application_rate['Microencapsulated']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 0
    application_rate['Microencapsulated']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 0
    application_rate['Microencapsulated']['Lawns / Turf']['Hose-end Sprayer'][''] = 0
    application_rate['Microencapsulated']['Lawns / Turf']['Manually-pressurized handwand'][''] = 0
    application_rate['Microencapsulated']['Gardens / Trees']['Backpack']['ft2'] = 0
    application_rate['Microencapsulated']['Gardens / Trees']['Backpack']['gallons'] = 0
    application_rate['Microencapsulated']['Lawns / Turf']['Backpack'][''] = 0
    application_rate['Microencapsulated']['Gardens / Trees']['Sprinkler can']['ft2'] = 0
    application_rate['Microencapsulated']['Gardens / Trees']['Sprinkler can']['gallons'] = 0
    application_rate['Microencapsulated']['Lawns / Turf']['Sprinkler can'][''] = 0
    application_rate['Ready-to-use']['Paints / Preservatives']['Aerosol can'][''] = 0
    application_rate['Paints / Preservatives/ Stains']['Paints / Preservatives']['Airless Sprayer'][''] = 0
    application_rate['Paints / Preservatives/ Stains']['Paints / Preservatives']['Brush'][''] = 0
    application_rate['Paints / Preservatives/ Stains']['Paints / Preservatives']['Manually-pressurized handwand'][''] = 0
    application_rate['Paints / Preservatives/ Stains']['Paints / Preservatives']['Roller'][''] = 0
    application_rate['Liquid concentrate']['Treated Pets']['Dip'][''] = 0
    application_rate['Liquid concentrate']['Treated Pets']['Sponge'][''] = 0
    application_rate['Ready-to-use']['Treated Pets']['Trigger-spray bottle'][''] = 0
    application_rate['Ready-to-use']['Treated Pets']['Aerosol can'][''] = 0
    application_rate['Ready-to-use']['Treated Pets']['Shampoo'][''] = 0
    application_rate['Ready-to-use']['Treated Pets']['Spot-on'][''] = 0
    application_rate['Ready-to-use']['Treated Pets']['Collar'][''] = 0
    application_rate['Dust/Powder']['Treated Pets']['Shaker Can'][''] = 0

    application_rate_units['Dust/Powder']['Indoor Environment']['Plunger Duster']['Broadcast; Perimeter/Spot/ Bedbug (course application)'] = 'lb ai/lb dust'
    application_rate_units['Dust/Powder']['Gardens / Trees']['Plunger Duster'][''] = 'lb ai/ft2'
    application_rate_units['Dust/Powder']['Indoor Environment']['Bulb duster']['Perimeter/Spot/Bedbug; Crack and Crevice'] = 'lb ai/lb dust'
    application_rate_units['Dust/Powder']['Gardens / Trees']['Bulb duster'][''] = 'lb ai/ft2'
    application_rate_units['Dust/Powder']['Indoor Environment']['Electric/power duster']['Broadcast; Perimeter/Spot/ Bedbug (course application)'] = 'lb ai/lb dust'
    application_rate_units['Dust/Powder']['Gardens / Trees']['Electric/power duster'][''] = 'lb ai/ft2'
    application_rate_units['Dust/Powder']['Indoor Environment']['Hand crank duster']['Broadcast; Perimeter/Spot/ Bedbug (course application)'] = 'lb ai/lb dust'
    application_rate_units['Dust/Powder']['Gardens / Trees']['Hand crank duster'][''] = 'lb ai/ft2'
    application_rate_units['Dust/Powder']['Indoor Environment']['Shaker can']['Broadcast'] = 'lb ai/can'
    application_rate_units['Dust/Powder']['Indoor Environment']['Shaker can']['Broadcast; Perimeter/Spot/ Bedbug (course application)'] = 'lb ai/can'
    application_rate_units['Dust/Powder']['Gardens / Trees']['Shaker can']['can'] = 'lb ai/can'
    application_rate_units['Dust/Powder']['Gardens / Trees']['Shaker can']['ft2'] = 'lb ai/ft2'
    application_rate_units['Liquid concentrate']['Indoor Environment']['Manually-pressurized handwand (w/ or w/o pin stream nozzle)']['Broadcast, Perimeter/Spot/ Bedbug (course application); Perimeter /Spot/ Bedbug (pinstream application); Crack and Crevice'] = 'lb ai/gallon'
    application_rate_units['Liquid concentrate']['Gardens / Trees']['Manually-pressurized handwand']['gallons'] = 'lb ai/gallon'
    application_rate_units['Liquid concentrate']['Gardens / Trees']['Manually-pressurized handwand']['ft2'] = 'lb ai/ft2'
    application_rate_units['Liquid concentrate']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 'lb ai/ft2'
    application_rate_units['Liquid concentrate']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 'lb ai/gallon'
    application_rate_units['Liquid concentrate']['Lawns / Turf']['Hose-end Sprayer'][''] = 'lb ai/acre'
    application_rate_units['Liquid concentrate']['Lawns / Turf']['Manually-pressurized handwand'][''] = 'lb ai/gallon'
    application_rate_units['Liquid concentrate']['Gardens / Trees']['Backpack']['ft2'] = 'lb ai/ft2'
    application_rate_units['Liquid concentrate']['Gardens / Trees']['Backpack']['gallons'] = 'lb ai/gallon'
    application_rate_units['Liquid concentrate']['Gardens / Trees']['Sprinkler can']['ft2'] = 'lb ai/ft2'
    application_rate_units['Liquid concentrate']['Gardens / Trees']['Sprinkler can']['gallons'] = 'lb ai/gallon'
    application_rate_units['Liquid concentrate']['Lawns / Turf']['Sprinkler can'][''] = 'lb ai/ft2'
    application_rate_units['Ready-to-use']['Indoor Environment']['Aerosol can']['Broadcast Surface Spray'] = 'lb ai/16-oz can'
    application_rate_units['Ready-to-use']['Indoor Environment']['Aerosol can']['Perimeter/ Spot/ Bedbug (course application)'] = 'lb ai/16-oz can'
    application_rate_units['Ready-to-use']['Indoor Environment']['Aerosol can with pin stream nozzle']['Perimeter/ Spot/ Bedbug (pin stream application); Crack and Crevice'] = 'lb ai/16-oz can'
    application_rate_units['Ready-to-use']['Indoor Environment']['Aerosol can']['Space spray'] = 'lb ai/16-oz can'

    application_rate_units['Ready-to-use']['Insect Repellent']['Aerosol can'][''] = 'lb ai/can'
    application_rate_units['Ready-to-use']['Insect Repellent']['Trigger-spray bottle'][''] = 'lb ai/bottle'

    application_rate_units['Ready-to-use']['Gardens / Trees']['Aerosol can'][''] = 'lb ai/can'
    application_rate_units['Ready-to-use']['Lawns / Turf']['Aerosol can'][''] = 'lb ai/can'
    application_rate_units['Ready-to-use']['Indoor Environment']['Trigger-spray bottle']['Broadcast'] = 'lb ai/bottle'
    application_rate_units['Ready-to-use']['Indoor Environment']['Trigger-spray bottle']['Perimeter/ Spot/ Bedbug (course application)'] = 'lb ai/bottle'

    application_rate_units['Ready-to-use']['Gardens / Trees']['Trigger-spray bottle'][''] = 'lb ai/bottle'
    application_rate_units['Ready-to-use']['Lawns / Turf']['Trigger-spray bottle'][''] = 'lb ai/bottle'
    application_rate_units['Ready-to-use']['Indoor Environment']['Bait (granular, hand dispersal)'][''] = 'lb ai/ft2'
    application_rate_units['Ready-to-use']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 'lb ai/ft2'
    application_rate_units['Ready-to-use']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 'lb ai/gallon'
    application_rate_units['Ready-to-use']['Lawns / Turf']['Hose-end Sprayer'][''] = 'lb ai/acre'
    application_rate_units['Wettable powders']['Indoor Environment']['Manually-pressurized handwand (w/ or w/o pin stream nozzle)']['Broadcast, Perimeter/Spot/ Bedbug (course application); Perimeter /Spot/ Bedbug (pinstream application); Crack and Crevice'] = 'lb ai/gallon'
    application_rate_units['Liquid concentrate']['Lawns / Turf']['Backpack'][''] = 'lb ai/gallon'
    application_rate_units['Wettable powders']['Gardens / Trees']['Manually-pressurized handwand']['ft2'] = 'lb ai/ft2'
    application_rate_units['Wettable powders']['Gardens / Trees']['Manually-pressurized handwand']['gallons'] = 'lb ai/gallon'
    application_rate_units['Wettable powders']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 'lb ai/ft2'
    application_rate_units['Wettable powders']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 'lb ai/gallon'
    application_rate_units['Wettable powders']['Lawns / Turf']['Hose-end Sprayer'][''] = 'lb ai/acre'
    application_rate_units['Wettable powders']['Lawns / Turf']['Manually-pressurized handwand'][''] = 'lb ai/gallon'
    application_rate_units['Wettable powders']['Gardens / Trees']['Backpack']['ft2'] = 'lb ai/ft2'
    application_rate_units['Wettable powders']['Gardens / Trees']['Backpack']['gallons'] = 'lb ai/gallon'
    application_rate_units['Wettable powders']['Gardens / Trees']['Sprinkler can']['ft2'] = 'lb ai/ft2'
    application_rate_units['Wettable powders']['Gardens / Trees']['Sprinkler can']['gallons'] = 'lb ai/gallon'
    application_rate_units['Wettable powders']['Lawns / Turf']['Sprinkler can'][''] = 'lb ai/ft2'
    application_rate_units['Wettable powders in water-soluble packaging']['Indoor Environment']['Manually-pressurized handwand (w/ or w/o pin stream nozzle)']['Broadcast, Perimeter/Spot/ Bedbug (course application); Perimeter /Spot/ Bedbug (pinstream application); Crack and Crevice'] = 'lb ai/gallon'
    application_rate_units['Wettable powders']['Lawns / Turf']['Backpack'][''] = 'lb ai/gallon'
    application_rate_units['Wettable powders in water-soluble packaging']['Gardens / Trees']['Manually-pressurized handwand']['ft2'] = 'lb ai/ft2'
    application_rate_units['Wettable powders in water-soluble packaging']['Gardens / Trees']['Manually-pressurized handwand']['gallons'] = 'lb ai/gallon'
    application_rate_units['Wettable powders in water-soluble packaging']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 'lb ai/ft2'
    application_rate_units['Wettable powders in water-soluble packaging']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 'lb ai/gallon'
    application_rate_units['Wettable powders in water-soluble packaging']['Lawns / Turf']['Hose-end Sprayer'][''] = 'lb ai/acre'
    application_rate_units['Wettable powders in water-soluble packaging']['Lawns / Turf']['Manually-pressurized handwand'][''] = 'lb ai/gallon'
    application_rate_units['Wettable powders in water-soluble packaging']['Lawns / Turf']['Backpack'][''] = 'lb ai/gallon'
    application_rate_units['Wettable powders in water-soluble packaging']['Gardens / Trees']['Sprinkler can']['ft2'] = 'lb ai/ft2'
    application_rate_units['Wettable powders in water-soluble packaging']['Gardens / Trees']['Sprinkler can']['gallons'] = 'lb ai/gallon'
    application_rate_units['Wettable powders in water-soluble packaging']['Lawns / Turf']['Sprinkler can'][''] = 'lb ai/ft2'
    application_rate_units['Wettable powders in water-soluble packaging']['Gardens / Trees']['Backpack'][''] = 'lb ai/ft2'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Lawns / Turf']['Manually-pressurized handwand'][''] = 'lb ai/gallon'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 'lb ai/ft2'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 'lb ai/gallon'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Lawns / Turf']['Hose-end Sprayer'][''] = 'lb ai/acre'
    application_rate_units['Wettable powders in water-soluble packaging']['Gardens / Trees']['Backpack'][''] = 'lb ai/gallon'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Manually-pressurized handwand']['ft2'] = 'lb ai/ft2'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Manually-pressurized handwand']['gallons'] = 'lb ai/gallon'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Lawns / Turf']['Backpack'][''] = 'lb ai/gallon'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Sprinkler can']['ft2'] = 'lb ai/ft2'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Sprinkler can']['gallons'] = 'lb ai/gallon'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Lawns / Turf']['Sprinkler can'][''] = 'lb ai/ft2'
    application_rate_units['Granule']['Gardens / Trees']['Push-type rotary spreader'][''] = 'lb ai/ft2'
    application_rate_units['Granule']['Lawns / Turf']['Push-type rotary spreader'][''] = 'lb ai/acre'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Backpack']['ft2'] = 'lb ai/ft2'
    application_rate_units['Water-disersible Granule / Dry Flowable']['Gardens / Trees']['Backpack']['gallons'] = 'lb ai/gallon'
    application_rate_units['Granule']['Lawns / Turf']['Belly grinder'][''] = 'lb ai/ft2'
    application_rate_units['Granule']['Gardens / Trees']['Spoon'][''] = 'lb ai/ft2'
    application_rate_units['Granule']['Lawns / Turf']['Spoon'][''] = 'lb ai/ft2'
    application_rate_units['Granule']['Gardens / Trees']['Cup'][''] = 'lb ai/ft2'
    application_rate_units['Granule']['Lawns / Turf']['Cup'][''] = 'lb ai/ft2'
    application_rate_units['Granule']['Gardens / Trees']['Hand dispersal'][''] = 'lb ai/ft2'
    application_rate_units['Granule']['Lawns / Turf']['Hand dispersal'][''] = 'lb ai/ft2'
    application_rate_units['Granule']['Gardens / Trees']['Shaker can']['can'] = 'lb ai/can'
    application_rate_units['Granule']['Gardens / Trees']['Shaker can']['ft2'] = 'lb ai/ft2'
    application_rate_units['Granule']['Lawns / Turf']['Shaker can'][''] = 'lb ai/ft2'
    application_rate_units['Microencapsulated']['Gardens / Trees']['Manually-pressurized handwand']['ft2'] = 'lb ai/ft2'
    application_rate_units['Microencapsulated']['Gardens / Trees']['Manually-pressurized handwand']['gallons'] = 'lb ai/gallon'
    application_rate_units['Microencapsulated']['Gardens / Trees']['Hose-end Sprayer']['ft2'] = 'lb ai/ft2'
    application_rate_units['Microencapsulated']['Gardens / Trees']['Hose-end Sprayer']['gallons'] = 'lb ai/gallon'
    application_rate_units['Microencapsulated']['Lawns / Turf']['Hose-end Sprayer'][''] = 'lb ai/acre'
    application_rate_units['Microencapsulated']['Lawns / Turf']['Manually-pressurized handwand'][''] = 'lb ai/gallon'
    application_rate_units['Microencapsulated']['Gardens / Trees']['Backpack']['ft2'] = 'lb ai/ft2'
    application_rate_units['Microencapsulated']['Gardens / Trees']['Backpack']['gallons'] = 'lb ai/gallon'
    application_rate_units['Microencapsulated']['Lawns / Turf']['Backpack'][''] = 'lb ai/gallon'
    application_rate_units['Microencapsulated']['Gardens / Trees']['Sprinkler can']['ft2'] = 'lb ai/ft2'
    application_rate_units['Microencapsulated']['Gardens / Trees']['Sprinkler can']['gallons'] = 'lb ai/gallon'
    application_rate_units['Microencapsulated']['Lawns / Turf']['Sprinkler can'][''] = 'lb ai/ft2'
    application_rate_units['Ready-to-use']['Paints / Preservatives']['Aerosol can'][''] = 'lb ai/12-oz can'
    application_rate_units['Paints / Preservatives/ Stains']['Paints / Preservatives']['Airless Sprayer'][''] = 'lb ai/1-gal can'
    application_rate_units['Paints / Preservatives/ Stains']['Paints / Preservatives']['Brush'][''] = 'lb ai/1-gal can'
    application_rate_units['Paints / Preservatives/ Stains']['Paints / Preservatives']['Manually-pressurized handwand'][''] = 'lb ai/1-gal can'
    application_rate_units['Paints / Preservatives/ Stains']['Paints / Preservatives']['Roller'][''] = 'lb ai/1-gal can'
    application_rate_units['Liquid concentrate']['Treated Pets']['Dip'][''] = 'lb ai/pet'
    application_rate_units['Liquid concentrate']['Treated Pets']['Sponge'][''] = 'lb ai/pet'
    application_rate_units['Ready-to-use']['Treated Pets']['Trigger-spray bottle'][''] = 'lb ai/pet'
    application_rate_units['Ready-to-use']['Treated Pets']['Aerosol can'][''] = 'lb ai/pet'
    application_rate_units['Ready-to-use']['Treated Pets']['Shampoo'][''] = 'lb ai/pet'
    application_rate_units['Ready-to-use']['Treated Pets']['Spot-on'][''] = 'lb ai/pet'
    application_rate_units['Ready-to-use']['Treated Pets']['Collar'][''] = 'lb ai/pet'
    application_rate_units['Dust/Powder']['Treated Pets']['Shaker Can'][''] = 'lb ai/pet'

    for formulation in application_rate: 
        for scenario in application_rate[formulation]:
            for application_method in application_rate[formulation][scenario]:
                for application_type in application_rate[formulation][scenario][application_method]:
                    application_rate_form_map[formulation][scenario][application_method][application_type] = "%s, %s, %s, %s" %(formulation, scenario, application_method, application_type )

    def __init__(self,*args,**kwargs):
        self.data_from_general_handler_sub_scenario_step = kwargs.pop('data_from_general_handler_sub_scenario_step',None)
        super(GeneralHandlerForm,self).__init__(*args,**kwargs)
        application_rates = []
        for formulation in GeneralHandlerForm.application_rate: 
            if self.data_from_general_handler_sub_scenario_step:
                if formulation in self.data_from_general_handler_sub_scenario_step['formulations']:
                    for scenario in GeneralHandlerForm.application_rate[formulation]:                    
                        if scenario in self.data_from_general_handler_sub_scenario_step['sub_scenarios']:
                            for application_method in GeneralHandlerForm.application_rate[formulation][scenario]:
                                if application_method in self.data_from_general_handler_sub_scenario_step['equipment']:
                                    application_rates.append((formulation, scenario, application_method,  GeneralHandlerForm.application_rate[formulation][scenario][application_method]))
        application_rates = sorted(application_rates, key=operator.itemgetter(1)) 

        for formulation, scenario, application_method, application_rate in application_rates:
                for application_type in application_rate:
                    self.fields[GeneralHandlerForm.application_rate_form_map[formulation][scenario][application_method][application_type]] = forms.FloatField(required=False,initial=0, label="%s [Application Rate (%s)]"%(GeneralHandlerForm.application_rate_form_map[formulation][scenario][application_method][application_type],GeneralHandlerForm.application_rate_units[formulation][scenario][application_method][application_type]),min_value=0.)


class GeneralHandlerSubScenariosForm(forms.Form):
    title = "General Handler Sub Scenario Selection"
    SUB_SCENARIOS_CHOICES = [('Insect Repellent','Insect Repellent'),('Treated Pets','Treated Pets'),('Lawns / Turf','Lawns / Turf'),('Gardens / Trees','Gardens / Trees'),('Paints / Preservatives','Paints / Preservatives'), ('Indoor Environment','Indoor Environment'),('Misting','Misting')] 
    sub_scenarios = forms.MultipleChoiceField(choices=SUB_SCENARIOS_CHOICES , widget=CheckboxSelectMultipleBootstrap())
    FORMULATION_CHOICES = [('Dust/Powder','Dust/Powder'), ('Granule', 'Granule'),('Liquid concentrate','Liquid concentrate'), ('Microencapsulated','Microencapsulated'), ('Paints / Preservatives/ Stains','Paints / Preservatives/ Stains'), ('Ready-to-use','Ready-to-use'), ('Water-disersible Granule / Dry Flowable','Water-disersible Granule / Dry Flowable'), ('Wettable powders','Wettable powders'), ('Wettable powders in water-soluble packaging','Wettable powders in water-soluble packaging')]
    formulations = forms.MultipleChoiceField(choices=FORMULATION_CHOICES , widget=CheckboxSelectMultipleBootstrap(), required=False)

    EQUIPMENT_CHOICES = [('Aerosol can with pin stream nozzle','Aerosol can with pin stream nozzle'),('Aerosol can','Aerosol can'),('Airless Sprayer','Airless Sprayer'),('Backpack','Backpack'),('Bait (granular, hand dispersal)','Bait (granular, hand dispersal)'),('Belly grinder','Belly grinder'),('Brush','Brush'),('Bulb duster','Bulb duster'),('Collar','Collar'),('Cup','Cup'),('Dip','Dip'),('Electric/power duster','Electric/power duster'),('Hand crank duster','Hand crank duster'),('Hand dispersal','Hand dispersal'),('Hose-end Sprayer','Hose-end Sprayer'),('Manually-pressurized handwand','Manually-pressurized handwand'),('Manually-pressurized handwand (w/ or w/o pin stream nozzle)', 'Manually-pressurized handwand (w/ or w/o pin stream nozzle)'),('Plunger Duster','Plunger Duster'), ('Push-type rotary spreader', 'Push-type rotary spreader'),('Roller','Roller'),('Shaker can','Shaker can'),('Shampoo','Shampoo'),('Sponge','Sponge'),('Spot-on','Spot-on'),('Sprinkler can','Sprinkler can'
),('Trigger-spray bottle','Trigger-spray bottle')]
    equipment = forms.MultipleChoiceField(choices=EQUIPMENT_CHOICES , widget=CheckboxSelectMultipleBootstrap(), required=False)
    
    n_inputs_equipment = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    n_inputs_formulation = defaultdict(lambda : defaultdict(int))
    n_inputs_scenarios = defaultdict(int)
    for i in xrange(0, len(SUB_SCENARIOS_CHOICES)): 
        for j in xrange(0, len(FORMULATION_CHOICES)):
            for k in xrange(0, len(EQUIPMENT_CHOICES)):
                formulation = FORMULATION_CHOICES[j][0]
                scenario = SUB_SCENARIOS_CHOICES[i][0]
                application_method = EQUIPMENT_CHOICES[k][0]
                try:
                    size = len(GeneralHandlerForm.application_rate[formulation][scenario][application_method])
                    n_inputs_equipment[i][j][k] += size
                    n_inputs_formulation[i][j] += size
                    n_inputs_scenarios[i] += size
                except:
                    pass
                    
                    
    def __init__(self,*args,**kwargs):
        super(GeneralHandlerSubScenariosForm,self).__init__(*args,**kwargs)
       

    def clean(self):
        
        cleaned_data = super(GeneralHandlerSubScenariosForm, self).clean()
        equipment = cleaned_data.get("equipment")
        formulations = cleaned_data.get("formulations")
        sub_scenarios = cleaned_data.get("sub_scenarios")
        if sub_scenarios == ['Misting']:
            return cleaned_data
        elif sub_scenarios:
            if formulations == [] or equipment == []:
                raise forms.ValidationError("Both formulations and equipment need to be selected for %s."%", ".join(sub_scenarios))
            count = 0
            for scenario in sub_scenarios:
                for formulation in formulations:
                    for application_method in equipment:
                        count += len(GeneralHandlerForm.application_rate[formulation][scenario][application_method])
            if count == 0:
                raise forms.ValidationError("No scenarios available for this selection of formulations and equipment. Ensure at least one of the equipment choices has greater than 1 in brackets.")


        return cleaned_data


         
class TreatedPetForm(forms.Form):
    title = "Treated Pet Data Entry Form"
    amount_applied_form_map = defaultdict(dict)
    for animal in ['cat','dog']:
        for size in ['small','medium','large']:
            amount_applied_form_map[animal][size] = "%s %s" %(size, animal)

#    amount_applied['Other Pet'][''] = 0
    fraction_ai = forms.FloatField(required=False,initial=0,min_value=0.,max_value=1.,label ="Fraction ai in product(0-1)");#defaultdict(dict)
    default_pet_weights = {'cat':{},'dog':{}} #lb
    default_pet_weights['dog'] = {'small':10.36535946,'medium':38.16827225,'large':76.50578234} #lb
    default_pet_weights['cat'] = {'small':3.568299485,'medium':7.8300955,'large':16.13607146}

    pet_weight = default_pet_weights['dog']['medium']
    #Surface Area (cm2) = ((12.3*((BW (lb)*454)^0.65))
    def pet_surface_area(lb):
        return 12.3*((lb*454)**0.65)

    def __init__(self,*args,**kwargs):
        super(TreatedPetForm,self).__init__(*args,**kwargs)
        for animal in TreatedPetForm.amount_applied_form_map: 
            for size in TreatedPetForm.amount_applied_form_map[animal]:
                TreatedPetForm.amount_applied_form_map[animal][size] = "%s %s" %(size, animal)
                self.fields[TreatedPetForm.amount_applied_form_map[animal][size]] = forms.FloatField(required=False,initial=0,min_value=0.,label = "Amount of product applied to a %s %s (g)" %(size, animal))

class LawnTurfForm(forms.Form):
    title = "Lawn and Turf Data Entry Form"
    liquid_application_rate = forms.FloatField(required=False,initial=0,min_value=0., label="Liquid Application Rate (lb ai/acre)")
    solid_application_rate = forms.FloatField(required=False,initial=0,min_value=0., label="Solid Application Rate (lb ai/acre)")

    liquid_ttr_conc = forms.FloatField(required=False,initial=0,min_value=0., label="Liquid TTR (calculated from application rate if not available) (ug/cm2)")#ORt = TTRt
    solid_ttr_conc = forms.FloatField(required=False,initial=0,min_value=0., label="Solid TTR (calculated from application rate if not available) (ug/cm2)")#ORt = TTRt

    fraction_ai_in_pellets = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1.,label="Fraction of ai in pellets/granules (0-1)")

class GardenAndTreesForm(forms.Form):
    title = "Garden and Trees Data Entry Form"
    liquid_application_rate = forms.FloatField(required=False,initial=0,min_value=0., label="Liquid Application Rate (lb ai/acre)")
    solid_application_rate = forms.FloatField(required=False,initial=0,min_value=0., label="Solid Application Rate (lb ai/acre)")

    liquid_dfr_conc = forms.FloatField(required=False,initial=0,min_value=0., label="Liquid DFR (calculated from application rate if not available) (ug/cm2)")
    solid_dfr_conc = forms.FloatField(required=False,initial=0,min_value=0., label="Solid DFR (calculated from application rate if not available) (ug/cm2)")

class InsectRepellentsForm(forms.Form):
    title = "Insect Repellent Data Entry Form"
    formulations = ['Aerosol', 'Pump spray', 'Lotion','Towelette']
    amount_ai_formulations_form_map = defaultdict(dict)
    for sunscreen_status in ['without','with']: 
        for formulation in formulations:
            amount_ai_formulations_form_map[sunscreen_status][formulation] = "%s repellent %s sunscreen" %(formulation, sunscreen_status)
    def __init__(self,*args,**kwargs):
        super(InsectRepellentsForm,self).__init__(*args,**kwargs)
        for sunscreen_status in ['without','with']: 
            for formulation in InsectRepellentsForm.formulations:
                self.fields[InsectRepellentsForm.amount_ai_formulations_form_map[sunscreen_status][formulation]] = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1., label = "Fraction of ai in %s repellent %s sunscreen (mg ai / mg product)"%(formulation,sunscreen_status))        

class PaintsAndPreservativesForm(forms.Form):
    title = "Paints and Preservatives Data Entry Form"
    surface_residue_concentration = forms.FloatField(required=False,initial=0, min_value=0., label="Surface Residue Concentration (mg ai/cm^2)")
    
    DEFAULT_FRACTION_OF_BODY_EXPOSED = 0.31
    DEFAULT_DAILY_MATERIAL_TO_SKIN_TRANSFER_EFFICENCY = 0.14
    EXPOSURE_TIME = {'indoor':4., 'outdoor':1.5}
    HAND_TO_MOUTH_EVENTS_PER_HOUR = {'indoor':20., 'outdoor':13.9}
    indoor_or_outdoor = forms.ChoiceField(choices=[('indoor','Indoor'),('outdoor','Outdoor')], initial='indoor', label="Location of interest (indoor/outdoor)")

class ImpregnatedMaterialsForm(forms.Form):
    title = "Impregnated Materials Data Entry Form"
    surface_residue_concentration = forms.FloatField(required=False)
    weight_fraction_of_active_ingredient = forms.FloatField(required=False)


    MATERIAL_CHOICES = [('cotton', 'Cotton'),  ('light_cotton_synthetic_mix', 'Light Cotton/Synthetic Mix'), ('heavy_cotton_synthetic_mix','Heavy Cotton/Synthetic Mix'),('all_synthetics','All Synthetics'),('household_carpets','Household Carpets'),('plastic_polymers','Plastic Polymers'), ('vinyl_flooring','Vinyl Flooring')]
    material_type = forms.ChoiceField(choices=MATERIAL_CHOICES,required=False)
    MATERIAL_CHOICES_DICT = {}
    for choice in MATERIAL_CHOICES:
        MATERIAL_CHOICES_DICT[choice[0]]=choice[1]
    MATERIAL_WEIGHT_TO_SURFACE_AREA_DENSITY = {'cotton': 20.,  'light_cotton_synthetic_mix': 10., 'heavy_cotton_synthetic_mix':24.,'all_synthetics':1.,'household_carpets':120.,'plastic_polymers':100., 'vinyl_flooring':40.}

    #DERMAL

    BODY_FRACTION_CHOICES = [('pants_jacket_shirt','Pants, Jacket, or Shirts'), ('total', 'Total Body Coverage'),  ('floor', 'Mattresses, Carpets or Flooring'), ('handlers','Handlers')]
    BODY_FRACTION_CHOICES_DICT = {}
    for choice in BODY_FRACTION_CHOICES:
        BODY_FRACTION_CHOICES_DICT[choice[0]]=choice[1]
    body_fraction_exposed_type = forms.ChoiceField(choices=BODY_FRACTION_CHOICES,required=True)
    BODY_FRACTION_EXPOSED = {'pants_jacket_shirt':0.5, 'total':1, 'floor':0.5, 'handlers':0.11}

    protective_barrier_present = forms.ChoiceField(choices=[('no','No'),('yes','Yes')],required=True,initial='no', label = "Is there a potential protective barried present (such as bed sheets or other fabrics)?")
    PROTECTION_FACTOR = {'no':1,'yes':0.5}

    #HtM
    TYPE_OF_FLOORING_CHOICES = [('',''), ('carpet','Carpet or Textiles'), ('hard', 'Hard Surface or Flooring')]
    TYPE_OF_FLOORING_CHOICES_DICT = {}
    for choice in TYPE_OF_FLOORING_CHOICES:
        TYPE_OF_FLOORING_CHOICES_DICT[choice[0]]=choice[1]
    type_of_flooring = forms.ChoiceField(choices=TYPE_OF_FLOORING_CHOICES ,required=False)
    FRACTION_AI_HAND_TRANSFER = {'':0., 'carpet':0.06,'hard':0.08}
    FLOOR_EXPOSURE_TIME = {'':0., 'carpet':4.,'hard':2.} 
    

    DEFAULT_FRACTION_OF_BODY_EXPOSED = 0.31
    type_of_flooring = forms.ChoiceField(choices=[('',''), ('carpet','Carpet'), ('hard', 'Hard Surface')] ,required=False)
    DEFAULT_DAILY_MATERIAL_TO_SKIN_TRANSFER_EFFICENCY = 0.14
    EXPOSURE_TIME = {'indoor':4., 'outdoor':1.5}
    HAND_TO_MOUTH_EVENTS_PER_HOUR = {'indoor':20., 'outdoor':13.9}
    indoor_or_outdoor = forms.ChoiceField(choices=[('indoor','Indoor'),('outdoor','Outdoor')], initial='indoor', label="Location of interest (indoor/outdoor)")

    #daily_material_to_skin_transfer_efficency = forms.FloatField(required=False,initial=0.14)
    #OtM
    
    FRACTION_AI_HAND_TRANSFER = {'':0., 'carpet':0.06,'hard':0.08}
    OBJECT_TO_MOUTH_EVENTS_PER_HOUR = {'':14.,'indoor':14., 'outdoor':8.8}
    


class IndoorEnvironmentsForm(forms.Form):
    title = "Indoor Environments Data Entry Form"
    space_spray_fraction_ai = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1.,label="Fraction of ai in Aerosol Space Sprays (0-1)") 
    space_spray_amount_of_product = forms.FloatField(required=False,initial=0, min_value=0.,label="Amount of product in Aerosol Space Spray can (g/can)")
    SPACE_SPRAY_RESTRICTION_CHOICES = [('NA','Not Applicable')] + [ (t/60., "%s minutes"%t) for t in [0,5,10,15,20,30,40,60,120]]   
    space_spray_restriction =  forms.ChoiceField(choices=SPACE_SPRAY_RESTRICTION_CHOICES) 
    molecular_weight = forms.FloatField(required=False,initial=0, min_value=0.,label="Molecular weight (g/mol)")    
    vapor_pressure = forms.FloatField(required=False,initial=0, min_value=0.,label="Vapor pressure (mmHg)")
    broadcast_residue = forms.FloatField(required=False,initial=0, min_value=0.,label="Residue deposited on broadcast (ug/cm^2)")    
    coarse_residue = forms.FloatField(required=False,initial=0, min_value=0.,label="Residue deposited on perimeter/spot/bedbug (coarse) (ug/cm^2)")    
    pin_stream_residue = forms.FloatField(required=False,initial=0, min_value=0.,label="Residue deposited on perimeter/spot/bedbug (pin stream) (ug/cm^2)")    
    crack_and_crevice_residue = forms.FloatField(required=False,initial=0, min_value=0.,label="Residue deposited on cracks and crevices  (ug/cm^2)")    
    foggers_residue = forms.FloatField(required=False,initial=0, min_value=0.,label="Residue deposited by foggers (ug/cm^2)")    
    space_sprays_residue = forms.FloatField(required=False,initial=0, min_value=0.,label="Residue deposited by space sprays (ug/cm^2)")
    matress_residue = forms.FloatField(required=False,initial=0, min_value=0.,label="Residue deposited on mattress (ug/cm^2)")        
    
    

class OutdoorMistingForm(forms.Form):
    title = "Outdoor Misting Data Entry Form"
    #OASS
    OASS_fraction_ai = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1.,label="Fraction of ai in Outdoor Aerosol Space Sprays (0-1)")
    OASS_amount_of_product_in_can = forms.FloatField(required=False,initial=0, min_value=0.,label="Amount of product in Outdoor Aerosol Space Spray can (g/can)")
    # CCTM
    CCTM_amount_ai_in_product = forms.FloatField(required=False,initial=0, min_value=0.,label="Amount ai in Candles, Coils, Torches, and/or Mats (mg ai/product)")
    # ORMS
    #product app rate on label:
    ORMS_application_rate = forms.FloatField(required=False,initial=0, min_value=0.,label="Application rate in Outdoor Residential Misting System(oz/1000 cu.ft.)")
    #else
    ORMS_dilution_rate = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1.,label="Dilution rate in Outdoor Residential Misting System (vol product/vol total solution) (0-1)")

    ORMS_fraction_ai = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1.,label="Fraction of ai in Outdoor Residential Misting System (0-1)")

    # AB
    #product app rate on label:
    AB_application_rate = forms.FloatField(required=False,initial=0, min_value=0.,label="Application rate in Animal Barns(oz/1000 cu.ft.)")
    #else
    AB_dilution_rate = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1.,label="Dilution rate in Animal Barns (vol product/vol total solution) (0-1)")

    AB_fraction_ai = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1.,label="Fraction of ai in Animal Barns (0-1)")
    

class OutdoorMistingGeneralHandlerForm(forms.Form):
    title = "Outdoor Misting General Handler Data Entry Form"
    OASS_fraction_ai = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1.,label="Fraction of ai in Outdoor Aerosol Space Sprays (0-1)")
    OASS_amount_of_product_in_can = forms.FloatField(required=False,initial=0, min_value=0.,label="Amount of product in Outdoor Aerosol Space Spray can (g/can)")
    # ORMS
    #product app rate on label:
    ORMS_DRUM_CHOICES = [(30,'30 gallons'), (55, '55 gallons')]    
    ORMS_drum_size =  forms.ChoiceField(choices=ORMS_DRUM_CHOICES,required=False, initial=55, label="Outdoor Residential Misting System Drum Size")
    ORMS_application_rate = forms.FloatField(required=False,initial=0, min_value=0.,label="Application rate in Outdoor Residential Misting System(oz/1000 cu.ft.)")
    #else
    ORMS_dilution_rate = forms.FloatField(required=False,initial=0, min_value=0.,label="Dilution rate in Outdoor Residential Misting System (vol product/vol total solution)")

    ORMS_fraction_ai = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1.,label="Fraction of ai in Outdoor Residential Misting System (0-1)")

    # AB
    #product app rate on label:
    AB_DRUM_CHOICES = [(30,'30 gallons'), (55, '55 gallons'), (125, '125 gallons')]
    AB_drum_size =  forms.ChoiceField(choices=AB_DRUM_CHOICES,required=False, initial=55, label="Animal Barn Drum Size" )
    #else
    AB_dilution_rate = forms.FloatField(required=False,initial=0, min_value=0.,label="Dilution rate in Animal Barns (vol product/vol total solution)")

    AB_fraction_ai = forms.FloatField(required=False,initial=0, min_value=0.,max_value=1.,label="Fraction of ai in Animal Barns (0-1)")

