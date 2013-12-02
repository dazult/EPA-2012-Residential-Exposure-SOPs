#!/usr/bin/python

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

register = template.Library()


@register.filter(name="dictget")
def dictget(thedict, key):
    "{{ dictionary|dictget:variableholdingkey }}"
    return thedict.get(key, None)

@register.filter(name="defaultdictget")
def defaultdictget(thedict, key):
    "{{ dictionary|defaultdictget:variableholdingkey }}"
    return thedict[key]

@register.filter(name="contains")
def contains(s, ss):
    "{{ string|contains:substring }}"
    return ss in s

@register.filter(name="not_contains")
def not_contains(s, ss):
    "{{ string|not_contains:substring }}"
    return not (ss in s)

@register.filter(name="n_significant_decimals")
def n_significant_decimals(value, n):
    "{{ value|n_significant_decimals:n }}"
    try:
        if abs(value) > 1:
            return ("{0:0.%sf}"%(n)).format(value)
        else:
            return ("{0:0.%sg}"%(n)).format(value)
    except:
        return value

