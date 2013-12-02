from django.conf.urls import patterns, include, url

from sop_calcs.views import ContactWizard

urlpatterns = patterns('',
    url(r'^$', 'sop_calcs.views.index',name='sop_calcs.home'),
    url(r'^wizard/$', ContactWizard.as_view(ContactWizard.form_list, condition_dict=ContactWizard.condition_dict), name='sop_calcs.wizard'),
    url(r'^wizard/results/excel/$', 'sop_calcs.views.excel_reports', name='sop_calcs.wizard_results_excel'),
);
