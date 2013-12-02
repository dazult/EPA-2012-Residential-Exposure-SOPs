from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

import os 
APP_DIR = os.path.dirname(__file__)

import json

from sop_calcs.forms import *

from django.contrib.formtools.wizard.views import SessionWizardView, CookieWizardView

FORMS = [("info", IngredientOverviewForm), ("tox", ToxForm), ("generalhandler", GeneralHandlerForm), ("treatedpet", TreatedPetForm), ("lawn",LawnTurfForm), ("garden",GardenAndTreesForm), ("insect",InsectRepellentsForm), ("paint",PaintsAndPreservativesForm)]

TEMPLATES = {"0": "wiz_info_page.html","tox": "wiz_tox_page.html",
             "generalhandler": "wiz.html","treatedpet":"wiz.html",'2':"prehandler.html", '3':"handler.html", '4':"outdoor_misting_handler.html",'8': 'insect.html','11': 'indoor.html','12': 'outdoor_misting.html','13':'results.html'}



def show_key_form_condition(wizard, key):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    try:
        return key in cleaned_data['exposure_scenarios']
    except:
        return False

def show_general_handler_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('2') or {}
    try:
        if 'Misting' in cleaned_data['sub_scenarios']:
            return len(cleaned_data['sub_scenarios']) > 1
        else:
            return len(cleaned_data['sub_scenarios']) > 0
    except:
        return False

def show_misting_handler_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('2') or {}
    try:
        return 'Misting' in cleaned_data['sub_scenarios']
    except:
        return False

def show_results_condition(wizard):
    return True

#class ContactWizard(SessionWizardView):
class ContactWizard(CookieWizardView):
    form_list = [IngredientOverviewForm, ToxForm, GeneralHandlerSubScenariosForm, GeneralHandlerForm, OutdoorMistingGeneralHandlerForm, TreatedPetForm, LawnTurfForm, GardenAndTreesForm, InsectRepellentsForm, PaintsAndPreservativesForm, ImpregnatedMaterialsForm, IndoorEnvironmentsForm, OutdoorMistingForm, ResultsForm]
    condition_dict={} 
    condition_dict['2'] = lambda wizard: show_key_form_condition(wizard, 'generalhandler')
    condition_dict['3'] = lambda wizard: show_general_handler_form_condition(wizard)
    condition_dict['4'] = lambda wizard: show_misting_handler_form_condition(wizard)
    condition_dict['5'] = lambda wizard: show_key_form_condition(wizard, 'treatedpet')
    condition_dict['6'] = lambda wizard: show_key_form_condition(wizard, 'lawn')
    condition_dict['7'] = lambda wizard: show_key_form_condition(wizard, 'garden')
    condition_dict['8'] = lambda wizard: show_key_form_condition(wizard, 'insect')
    condition_dict['9'] = lambda wizard: show_key_form_condition(wizard, 'paint')
    condition_dict['10'] = lambda wizard: show_key_form_condition(wizard, 'impregnated_materials')
    condition_dict['11'] = lambda wizard: show_key_form_condition(wizard, 'indoor')
    condition_dict['12'] = lambda wizard: show_key_form_condition(wizard, 'misting')
    condition_dict['13'] = lambda wizard: show_results_condition(wizard)


    def get_template_names(self):
        return [TEMPLATES[self.steps.current] if self.steps.current in TEMPLATES else "wiz.html"]

    def parse_params(self, request, *args, **kwargs):
        current_step = self.determine_step(request, *args, **kwargs)
        if request.method == 'POST' and current_step != 1:
            form = self.get_form(current_step, request.POST)
            if form.is_valid():
                self.initial[1] = form.cleaned_data

    def get_form_initial(self, step):
        initial = self.initial_dict.get(step, {})
        if step == '1':
            data_from_step_1 = self.get_cleaned_data_for_step('0')
            initial.update({'data_from_step_1': data_from_step_1})
        return initial


    def get_context_data(self, form, **kwargs):
        context = super(ContactWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.step0 == 1:
            data_from_step_1 = self.get_cleaned_data_for_step('0') # zero indexed       
            context.update({'data_from_step_1':data_from_step_1,})
        if self.steps.step0 == 3:
            data_from_general_handler_sub_scenario_step = self.get_cleaned_data_for_step('2') # zero indexed       
            context.update({'data_from_general_handler_sub_scenario_step':data_from_general_handler_sub_scenario_step,})
        if self.steps.step0 == 13:        
            s = {}
            for i in xrange(0,13):
                s[i] = self.get_cleaned_data_for_step('%s'%i)
            context.update({'_input_data': json.dumps(s) })

        return context

    def get_form_kwargs(self, step=None):
        
        kwargs = super(ContactWizard, self).get_form_kwargs(step=step)
        if step == '1':        
            data_from_step_1 = self.get_cleaned_data_for_step('0') # zero indexed       
            kwargs.update({'data_from_step_1':data_from_step_1,})
        if step == '3':
            data_from_general_handler_sub_scenario_step = self.get_cleaned_data_for_step('2') # zero indexed       
            kwargs.update({'data_from_general_handler_sub_scenario_step':data_from_general_handler_sub_scenario_step,})
        if step == '13':
            s = {}
            for i in xrange(0,13):
                s[i] = self.get_cleaned_data_for_step('%s'%i)
            kwargs.update({'_input_data': json.dumps(s) })
        return kwargs

    def done(self, form_list, **kwargs):
        return HttpResponseRedirect('/wizard/')

from gardensandtrees import gardensandtrees
from treated_pets import treated_pets
from insect_repellent import insect_repellent
from lawnturfsop import lawnturfsop
from general_handler_sop import general_handler_sop
from paintsop import paintsop

def index(request):
    return render_to_response('intro.html', {},context_instance=RequestContext(request))

    
from StringIO import StringIO  
from zipfile import ZipFile, ZIP_DEFLATED
from django.http import HttpResponse  
  
def excel_reports(request): 
    try:
        s = json.loads(request.POST['_input_data'])#json.loads(request.session.get('_input_data'))
    except:
        return HttpResponse('No data input received')

    in_memory = StringIO()  
    zip = ZipFile(in_memory, "w", ZIP_DEFLATED)  
    for duration in s['0']['exposure_durations']:
        for target in s['0']['target_population']:
            standard_replacements = [('Active_ingredient',s['0']['active_ingredient'])]
            standard_replacements.append(('Duration',"%s-term"%duration))


            POD = {}
            LOC = {}
            absorption = {}

            try:
                POD['dermal'] = s['1']['dermal_%s_%s_POD' % (duration,target)]
                LOC['dermal'] = s['1']['dermal_%s_%s_LOC' % (duration,target)]

                standard_replacements.append(('Dermal_POD_Source',"%s"%s['1']['dermal_POD_study'] or ''))
                standard_replacements.append(('Dermal_POD',POD['dermal']))
                standard_replacements.append(('Dermal_LOC',LOC['dermal']))


                absorption['dermal'] = s['1']['dermal_absorption']
                standard_replacements.append(('Dermal_Absorption_Source',"%s"%s['1']['dermal_absorption_study'] or ''))
                standard_replacements.append(('Dermal_Absorption',absorption['dermal']))
            except:
                standard_replacements.append(('Dermal_POD_Source',''))
                standard_replacements.append(('Dermal_POD',''))
                standard_replacements.append(('Dermal_LOC',''))  
                standard_replacements.append(('Dermal_Absorption_Source',''))
                standard_replacements.append(('Dermal_Absorption',''))

            try:
                POD['inhalation'] = s['1']['inhalation_%s_%s_POD' % (duration,target)]
                LOC['inhalation'] = s['1']['inhalation_%s_%s_LOC' % (duration,target)]
                standard_replacements.append(('Inhalation_POD_Source',"%s"%s['1']['inhalation_POD_study'] or ''))
                standard_replacements.append(('Inhalation_POD',POD['inhalation']))

                standard_replacements.append(('Inhalation_LOC',LOC['inhalation']))  
                absorption['inhalation'] = s['1']['inhalation_absorption']
                standard_replacements.append(('Inhalation_Absorption_Source',"%s"%s['1']['inhalation_absorption_study'] or ''))
                standard_replacements.append(('Inhalation_Absorption',absorption['inhalation']))
            except:
                standard_replacements.append(('Inhalation_POD_Source',''))
                standard_replacements.append(('Inhalation_POD',''))
                standard_replacements.append(('Inhalation_LOC',''))  
                standard_replacements.append(('Inhalation_Absorption_Source',''))
                standard_replacements.append(('Inhalation_Absorption',''))
            try:
                POD['oral'] = s['1']['oral_%s_%s_POD' % (duration,target)]
                LOC['oral'] = s['1']['oral_%s_%s_LOC' % (duration,target)]
                try:
                    standard_replacements.append(('Oral_POD_Source',"%s"%s['1']['oral_POD_study'] or ''))
                except:
                    standard_replacements.append(('Oral_POD_Source',''))
                standard_replacements.append(('Oral_POD',POD['oral']))
                standard_replacements.append(('Oral_LOC',LOC['oral']))
            except:
                standard_replacements.append(('Oral_POD_Source',''))
                standard_replacements.append(('Oral_POD',''))
                standard_replacements.append(('Oral_LOC',''))
            try:
                POD['dietary'] = s['1']['dietary_%s_POD' % duration]
                LOC['dietary'] = s['1']['dietary_%s_LOC' % duration]
                standard_replacements.append(('Dietary_POD',POD['dietary']))
                standard_replacements.append(('Dietary_LOC',LOC['dietary']))
            except: 
                standard_replacements.append(('Dietary_POD',''))
                standard_replacements.append(('Dietary_LOC',''))


            body_weights_adults_options = [80, 69, 86] # kg
            bodyweight = {}
            bodyweight['adult'] = body_weights_adults_options[0]
            bodyweight['adult_general'] = 80
            bodyweight['gen'] = 80
            bodyweight['adult_female'] = 69
            bodyweight['adult_male'] = 86
            bodyweight['1_to_2'] = 11
            bodyweight['3_to_6'] = 19
            bodyweight['6_to_11'] = 32
            bodyweight['11_to_16'] = 57
            standard_replacements.append(('Adult_bw',str(bodyweight[target])))
            standard_replacements.append(('Child_1_2_bw',"11"))
            standard_replacements.append(('Child_3_6_bw',"19"))
            standard_replacements.append(('Child_6_11_bw',"32"))
            standard_replacements.append(('Child_11_16_bw',"57"))        
            inhalation_rate = {}
            inhalation_rate['adult'] = 0.64
            inhalation_rate['1_to_2'] = 0.33
            inhalation_rate['3_to_6'] = 0.42
            standard_replacements.append(('Adult_inhalation_rate',"0.64"))
            standard_replacements.append(('Child_1_2_inhalation_rate',"0.33"))
            standard_replacements.append(('Child_3_6_inhalation_rate',"0.42"))
            SA_BW_ratio = {'1_to_2':640, 'adult':280}

            def write_excel_file(file_template,new_file_name, replacements=[]):
                gh_template_xlsx = ZipFile(file_template)
                gh_in_memory = StringIO()  
                gh_xlsx = ZipFile(gh_in_memory, "w", ZIP_DEFLATED)  
                for name in gh_template_xlsx.namelist():
                    if name == "xl/sharedStrings.xml":
                        sharedStrings = gh_template_xlsx.read(name)
                        for replacement in replacements:
                            try:
                                logger.error("KEY_%s"%replacement[0],"=VALUE(%s)"%float(replacement[1]))
                                sharedStrings = sharedStrings.replace("KEY_%s"%replacement[0],float(replacement[1]))                           
                            except:
                                sharedStrings = sharedStrings.replace("KEY_%s"%replacement[0],"%s"%replacement[1])
                        gh_xlsx.writestr(name, sharedStrings)                    
                    elif 'xl/worksheets/sheet' in name:
                        gh_xlsx.writestr(name, gh_template_xlsx.read(name).replace('</sheetData>','</sheetData><sheetCalcPr fullCalcOnLoad="true"/>'))                           
                    else:
                        gh_xlsx.writestr(name, gh_template_xlsx.read(name))   
                # fix for Linux zip files read in Windows  
                for file in gh_xlsx.filelist:  
                    file.create_system = 0                
                gh_xlsx.close()
                zip.writestr('%s/%s_%s_%s.xlsx'%(duration,duration,target,new_file_name),  gh_in_memory.getvalue())
            

            if s['2'] != None: #generalhandler 
                handler_replacements = [] 
                for formulation in GeneralHandlerForm.application_rate_form_map: 
                    for scenario in GeneralHandlerForm.application_rate_form_map[formulation]:      
                        for application_method in GeneralHandlerForm.application_rate_form_map[formulation][scenario]:
                            for application_type in GeneralHandlerForm.application_rate_form_map[formulation][scenario][application_method]:
                                try:
                                    handler_replacements.append(("%s_%s_%s_%s"%(formulation.replace(" ",""),scenario.replace(" ",""),application_method.replace(" ",""),application_type.replace(" ","")) ,"%s" % s['3'][GeneralHandlerForm.application_rate_form_map[formulation][scenario][application_method][application_type]] or 0.))
                                except:
                                    handler_replacements.append(("%s_%s_%s_%s"%(formulation.replace(" ",""),scenario.replace(" ",""),application_method.replace(" ",""),application_type.replace(" ","")) ,"" ))
                #misting
                if s['4'] != None:
                    handler_replacements.append(("OASS_fraction_ai",100*s['4']['OASS_fraction_ai']))
                    handler_replacements.append(("OASS_amount_of_product_in_can",s['4']['OASS_amount_of_product_in_can']))
                    handler_replacements.append(("ORMS_drum_size",s['4']['ORMS_drum_size']))
                    handler_replacements.append(("ORMS_application_rate",s['4']['ORMS_application_rate']))
                    handler_replacements.append(("ORMS_dilution_rate",s['4']['ORMS_dilution_rate']))
                    handler_replacements.append(("ORMS_fraction_ai",100*s['4']['ORMS_fraction_ai']))
                    handler_replacements.append(("AB_drum_size",s['4']['AB_drum_size']))
                    handler_replacements.append(("AB_dilution_rate",s['4']['AB_dilution_rate']))
                    handler_replacements.append(("AB_fraction_ai",100*s['4']['AB_fraction_ai']))                
                else:
                    handler_replacements.append(("OASS_fraction_ai",""))
                    handler_replacements.append(("OASS_amount_of_product_in_can",""))
                    handler_replacements.append(("ORMS_drum_size",""))
                    handler_replacements.append(("ORMS_application_rate",""))
                    handler_replacements.append(("ORMS_dilution_rate",""))
                    handler_replacements.append(("ORMS_fraction_ai",""))
                    handler_replacements.append(("AB_drum_size",""))
                    handler_replacements.append(("AB_dilution_rate",""))
                    handler_replacements.append(("AB_fraction_ai",""))
                handler_replacements.sort()
                write_excel_file(APP_DIR + '/excel_templates/Handler_SOP_2012.xlsx', 'general_handler',standard_replacements+handler_replacements[::-1])
            if s['5'] != None: #treated_pet
                pet_replacements = [('fraction_ai',"%s"%s['5']['fraction_ai'])]
                for animal in ['dog','cat']:
                    for size in ['large','medium','small']:
                        pet_replacements.append(('%s_%s'%(animal,size), "%s"%s['5'][TreatedPetForm.amount_applied_form_map[animal][size]]))
                write_excel_file(APP_DIR + '/excel_templates/treated_pets.xlsx', 'treated_pets',standard_replacements+pet_replacements)
                
            if s['6'] != None: #lawn
                lawn_replacements = [('fraction_ai',"%s"%s['6']['fraction_ai_in_pellets'])]
                lawn_replacements.append(('liquid_application_rate',"%s"%s['6']['liquid_application_rate']))
                lawn_replacements.append(('solid_application_rate',"%s"%s['6']['solid_application_rate']))
                lawn_replacements.append(('liquid_ttr',"%s"%s['6']['liquid_ttr_conc']))
                lawn_replacements.append(('solid_ttr',"%s"%s['6']['solid_ttr_conc']))
                
                write_excel_file(APP_DIR + '/excel_templates/Lawns_Turf.xlsx',  'lawns_turf',standard_replacements+lawn_replacements)
            if s['7'] != None: #gardensandtrees 
                garden_replacements = []
                garden_replacements.append(('liquid_application_rate',"%s"%s['7']['liquid_application_rate']))
                garden_replacements.append(('solid_application_rate',"%s"%s['7']['solid_application_rate']))
                garden_replacements.append(('liquid_dfr',"%s"%s['7']['liquid_dfr_conc']))
                garden_replacements.append(('solid_dfr',"%s"%s['7']['solid_dfr_conc']))
                write_excel_file(APP_DIR + '/excel_templates/Gardens_Trees.xlsx',  'gardens_trees',standard_replacements+garden_replacements)
            if s['8'] != None: #insectrepellents
                insect_replacements = []
                for sunscreen_status in ['without','with']: 
                    for formulation in InsectRepellentsForm.formulations:
                        insect_replacements.append(( "%s_%s_amount"%(sunscreen_status,formulation.lower().replace(" ","")), "%s"%s['8'][InsectRepellentsForm.amount_ai_formulations_form_map[sunscreen_status][formulation]]))
                write_excel_file(APP_DIR + '/excel_templates/InsectRepellents.xlsx',  'insect_repellents', standard_replacements+insect_replacements)
            if s['9'] != None: #paint
                paint_replacements = []         
                paint_replacements.append(('body_fraction_exposed',"%s"%PaintsAndPreservativesForm.DEFAULT_FRACTION_OF_BODY_EXPOSED))
                paint_replacements.append(('material_to_skin_transfer_efficiency',"%s"%PaintsAndPreservativesForm.DEFAULT_DAILY_MATERIAL_TO_SKIN_TRANSFER_EFFICENCY))
                paint_replacements.append(('surface_residue_concentration',"%s"%s['9']['surface_residue_concentration']))
                paint_replacements.append(('exposure_time',"%s"%PaintsAndPreservativesForm.EXPOSURE_TIME[s['9']['indoor_or_outdoor']]))
                paint_replacements.append(('hand_to_mouth_fequency', "%s" %PaintsAndPreservativesForm.HAND_TO_MOUTH_EVENTS_PER_HOUR[s['9']['indoor_or_outdoor']] ))
                write_excel_file(APP_DIR + '/excel_templates/PaintsAndPreservatives.xlsx',  'paints_preservatives',standard_replacements+paint_replacements)  

            if s['10'] != None: #impre
                impregnated_materials_replacements = []
                if s['10']['surface_residue_concentration'] is None or s['10']['surface_residue_concentration'] == 0:
                    impregnated_materials_replacements.append(('Residue_data_available','No'))
                    weight_fraction = s['10']['weight_fraction_of_active_ingredient']
                    impregnated_materials_replacements.append(('Residue_concentration_or_weight_fraction', weight_fraction))
                else:
                    impregnated_materials_replacements.append(('Residue_data_available','Yes'))
                    impregnated_materials_replacements.append(('Residue_concentration_or_weight_fraction', s['10']['surface_residue_concentration']))
                material_type = s['10']['material_type']
                impregnated_materials_replacements.append(('material_type',ImpregnatedMaterialsForm.MATERIAL_CHOICES_DICT[material_type]))
                impregnated_materials_replacements.append(('material_weight_surface_area',  ImpregnatedMaterialsForm.MATERIAL_WEIGHT_TO_SURFACE_AREA_DENSITY[material_type]))
                impregnated_materials_replacements.append(('protective_barrier', s['10']['protective_barrier_present'].capitalize()))
                 
                
                body_fraction_exposed_type = s['10']['body_fraction_exposed_type']
                impregnated_materials_replacements.append(('fraction_body_value',ImpregnatedMaterialsForm.BODY_FRACTION_EXPOSED[body_fraction_exposed_type]))                    
                impregnated_materials_replacements.append(('fraction_body',ImpregnatedMaterialsForm.BODY_FRACTION_CHOICES_DICT[body_fraction_exposed_type]))
                

                type_of_flooring = s['10']['type_of_flooring']
                impregnated_materials_replacements.append(('type_of_flooring_et',ImpregnatedMaterialsForm.FLOOR_EXPOSURE_TIME[type_of_flooring] ))
                impregnated_materials_replacements.append(('type_of_flooring_value',ImpregnatedMaterialsForm.FRACTION_AI_HAND_TRANSFER[type_of_flooring] ))
                impregnated_materials_replacements.append(('type_of_flooring',ImpregnatedMaterialsForm.TYPE_OF_FLOORING_CHOICES_DICT[type_of_flooring] ))
                
                indoor_or_outdoor = s['10']['indoor_or_outdoor']
                impregnated_materials_replacements.append(('indoor_or_outdoor_et',ImpregnatedMaterialsForm.EXPOSURE_TIME[indoor_or_outdoor] ))
                impregnated_materials_replacements.append(('indoor_or_outdoor_otm',ImpregnatedMaterialsForm.OBJECT_TO_MOUTH_EVENTS_PER_HOUR[indoor_or_outdoor] ))
                impregnated_materials_replacements.append(('indoor_or_outdoor',indoor_or_outdoor.capitalize() ))
                
                
                write_excel_file(APP_DIR + '/excel_templates/impregnated_materials.xlsx',  'indoor',standard_replacements+impregnated_materials_replacements)
            if s['11'] != None:#indoor
                indoor_replacements = []
                indoor_replacements.append(('space_spray_fraction_ai',s['11']['space_spray_fraction_ai']))
                indoor_replacements.append(('space_spray_amount_of_product',s['11']['space_spray_amount_of_product']))
                s['11']['space_spray_restriction']
                indoor_replacements.append(('molecular_weight',s['11']['molecular_weight']))
                indoor_replacements.append(('vapor_pressure',s['11']['vapor_pressure']))
                indoor_replacements.append(('broadcast_residue',s['11']['broadcast_residue']))
                indoor_replacements.append(('coarse_residue',s['11']['coarse_residue']))
                indoor_replacements.append(('pin_stream_residue',s['11']['pin_stream_residue']))
                indoor_replacements.append(('crack_and_crevice_residue',s['11']['crack_and_crevice_residue']))
                indoor_replacements.append(('foggers_residue',s['11']['foggers_residue']))
                indoor_replacements.append(('space_sprays_residue',s['11']['space_sprays_residue']))
                indoor_replacements.append(('matress_residue',s['11']['matress_residue']))
                indoor_replacements.append(('ventilation_time',""))
                write_excel_file(APP_DIR + '/excel_templates/indoor.xlsx',  'indoor',standard_replacements+indoor_replacements)
            if s['12'] != None: #outdoor_misting
                outdoor_misting_replacements = []
                outdoor_misting_replacements.append(('OASS_fraction_ai',100*s['12']['OASS_fraction_ai']))
                outdoor_misting_replacements.append(('OASS_amount_of_product_in_can',s['12']['OASS_amount_of_product_in_can']))
                outdoor_misting_replacements.append(('CCTM_amount_ai_in_product',s['12']['CCTM_amount_ai_in_product']))
                outdoor_misting_replacements.append(('ORMS_application_rate',s['12']['ORMS_application_rate']))
                outdoor_misting_replacements.append(('ORMS_dilution_rate',s['12']['ORMS_dilution_rate']))
                outdoor_misting_replacements.append(('ORMS_fraction_ai',100*s['12']['ORMS_fraction_ai']))
                outdoor_misting_replacements.append(('AB_application_rate',s['12']['AB_application_rate']))
                outdoor_misting_replacements.append(('AB_dilution_rate',s['12']['AB_dilution_rate']))
                outdoor_misting_replacements.append(('AB_fraction_ai',100*s['12']['AB_fraction_ai']))
                write_excel_file(APP_DIR + '/excel_templates/outdoor_misting.xlsx',  'outdoor_misting',standard_replacements+outdoor_misting_replacements) 
                

            
    # fix for Linux zip files read in Windows  
    for file in zip.filelist:  
        file.create_system = 0   
    zip.close()  
 
    
    response = HttpResponse(mimetype="application/zip")  
    response["Content-Disposition"] = "attachment; filename=sop_results.zip"  
       
    response.write(in_memory.getvalue())  
      
    return response    
