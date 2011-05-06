# -*- coding: utf-8 -*-

from django import template
from django.template.loader import render_to_string
from mywot.models import Target, MYWOT_CATEGORY_DESCRIPTION
import re

register = template.Library()


@register.simple_tag
def mywot_scorecard(url):
    ''' Return the MyWOT Scorecard for the specified domain. '''

    ## return the mywot scorecard of the extracted domain
    target = Target.get_or_create_object(url)
    return render_to_string(
        'mywot/mywot_scorecard.html',
        { 'target':target },
    )


@register.simple_tag
def mywot_scorecard_row(target, n):
    ''' Return one row f the the MyWOT Scorecard. '''

    ## return the row of the mywot scorecard
    return render_to_string(
        'mywot/mywot_scorecard_row.html',
        { 'target':target, 'n':n },
    )


@register.simple_tag
def mywot_reputation_score(target, n):
    ''' Return the target reputation score. '''

    return target.get_reputation_score(n)


@register.simple_tag
def mywot_confidence_score(target, n):
    ''' Return the target confidence score. '''

    return target.get_confidence_score(n)


@register.simple_tag
def mywot_reputation_score_label(target, n):
    ''' Return the label of the target reputation score. '''

    return target.get_reputation_score_label(n)


@register.simple_tag
def mywot_confidence_score_label(target, n):
    ''' Return the label of the target confidence score. '''

    return target.get_confidence_score_label(n)


@register.simple_tag
def mywot_reputation_score_image(target, n):
    ''' Return the image of the target reputation score. '''

    return target.get_reputation_score_image(n)


@register.simple_tag
def mywot_confidence_score_image(target, n):
    ''' Return the image of the target confidence score. '''

    return target.get_confidence_score_image(n)


@register.simple_tag
def mywot_category_description(n):
    ''' Return the descriptoin of the specified category. '''

    return MYWOT_CATEGORY_DESCRIPTION[n]


@register.tag
def mywot_load_target(parser, token):
    ''' Return the target object for the specified domain.
        {% mywot_load_targert url as target %} '''

    try:
        tag_name, domain, _, varname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly three arguments" \
                % token.contents.split()[0]
        )
    return LoadTargetNode(domain, varname)

class LoadTargetNode(template.Node):
    ''' Node object for the "mywot_load_target". '''

    def __init__(self, domain, varname):
        self.varname = varname
        self.domain = template.Variable(domain)
    
    def render(self, context):
        try:
           value = self.domain.resolve(context)
           context[self.varname] = Target.get_or_create_object(value)
        except template.VariableDoesNotExist:
            pass
        return ''
