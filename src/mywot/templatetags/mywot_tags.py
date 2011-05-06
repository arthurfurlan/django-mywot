# -*- coding: utf-8 -*-

from django import template
from django.template.loader import render_to_string
from mywot.models import Target, MYWOT_CATEGORY_DESCRIPTION
import re

register = template.Library()

## regular expressions to clean up url
URL_PROTOCOL_RE = re.compile('^https?://')
URL_PATHINFO_RE = re.compile('/.*$')


@register.simple_tag
def mywot_scorecard(url):
    ''' Return the MyWOT Scorecard for the specified domain. '''

    ## extract the domain from the URL
    domain = URL_PROTOCOL_RE.sub('', url)
    domain = URL_PATHINFO_RE.sub('', domain)

    ## return the mywot scorecard of the extracted domain
    target = Target.get_or_create_object(domain)
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
