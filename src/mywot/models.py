# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from datetime import datetime
from xml.dom import minidom
from urllib2 import urlopen
import os
import re


## number of days required to expiry the loaded values
MYWOT_EXPIRATION_DAYS = getattr(settings, 'MYWOT_EXPIRATION_DAYS', 180)

## limits of the score value for the reputation
MYWOT_REPUTATION_SCOREVAL = [80, 60, 40, 20, 1]
MYWOT_REPUTATION_SCOREMAX = 5
MYWOT_REPUTATION_SCOREMIN = 0

## limits of the score value for the confidence
MYWOT_CONFIDENCE_SCOREVAL = [45, 34, 23, 12, 6]
MYWOT_CONFIDENCE_SCOREMAX = 5
MYWOT_CONFIDENCE_SCOREMIN = 0

## label of the reputation/confidence categories
try:
    MYWOT_CATEGORY_DESCRIPTION = settings.MYWOT_CATEGORY_DESCRIPTION
except AttributeError:
    MYWOT_CATEGORY_DESCRIPTION = {
        0: _(u'Trustworthiness'),
        1: _(u'Vendor reliability'),
        2: _(u'Privacy'),
        4: _(u'Child safety'),
    }

## label of the reputation values
try:
    MYWOT_REPUTATION_SCORELBL = settings.MYWOT_REPUTATION_SCORELBL
except AttributeError:
    MYWOT_REPUTATION_SCORELBL = {
        5: _(u'Excellent'),
        4: _(u'Good'),
        3: _(u'Unsatisfactory'),
        2: _(u'Poor'),
        1: _(u'Very poor'),
        0: _(u'Not rated'),
    }

## label of the confidence values
try:
    MYWOT_CONFIDENCE_SCORELBL = settings.MYWOT_CONFIDENCE_SCORELBL
except AttributeError:
    MYWOT_CONFIDENCE_SCORELBL = {
        5: u'5 / 5',
        4: u'4 / 5',
        3: u'3 / 5',
        2: u'2 / 5',
        1: u'1 / 5',
        0: u'0 / 5',
    }


class DomainRequiredError(Exception):
    pass


class Target(models.Model):

    domain = models.CharField(max_length=255, unique=True, db_index=True)
    last_update = models.DateTimeField(auto_now=True)

    ## reputation values
    reputation_0 = models.IntegerField(MYWOT_CATEGORY_DESCRIPTION[0], blank=True, null=True)
    reputation_1 = models.IntegerField(MYWOT_CATEGORY_DESCRIPTION[1], blank=True, null=True)
    reputation_2 = models.IntegerField(MYWOT_CATEGORY_DESCRIPTION[2], blank=True, null=True)
    reputation_4 = models.IntegerField(MYWOT_CATEGORY_DESCRIPTION[4], blank=True, null=True)

    ## confidence of the reputation values
    confidence_0 = models.IntegerField(u'Confidence of ' + MYWOT_CATEGORY_DESCRIPTION[0], blank=True, null=True)
    confidence_1 = models.IntegerField(u'Confidence of ' + MYWOT_CATEGORY_DESCRIPTION[1], blank=True, null=True)
    confidence_2 = models.IntegerField(u'Confidence of ' + MYWOT_CATEGORY_DESCRIPTION[2], blank=True, null=True)
    confidence_4 = models.IntegerField(u'Confidence of ' + MYWOT_CATEGORY_DESCRIPTION[4], blank=True, null=True)

    ## url of the mywot's api
    MYWOT_API = ' http://api.mywot.com/0.4/public_query2?target=%s'

    ## regular expression to validate domain names
    DOMAIN_RE = re.compile(
        r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,6}\.?$',
        re.IGNORECASE,
    )

    ## regular expressions to extract domains from urls
    URL_PROTOCOL_RE = re.compile('^https?://')
    URL_PATHINFO_RE = re.compile('/.*$')


    def __unicode__(self):
        return self.domain


    def clean(self):
        u''' Check if the domain is a valid domain name. '''

        if self.DOMAIN_RE.match(self.domain):
            return self.domain.lower()
        else:
            raise ValidationError(u'Invalid domain name.')


    def load_values(self):
        u''' Load the reputation and confidence values from MyWOT. '''

        if not self.domain:
            message = u'You need to specify a domain before loading the value.'
            raise DomainRequiredError(message)

        ## consume the mywot's webservice
        url = self.get_api_url()
        dom = minidom.parse(urlopen(url))

        ## parse the xml data and extract the values
        query = dom.childNodes[0]
        for entry in query.childNodes:
            n = entry.getAttribute('name')
            setattr(self, 'reputation_' + n, entry.getAttribute('r'))
            setattr(self, 'confidence_' + n, entry.getAttribute('c'))


    def get_api_url(self):
        u''' Return the url of the MyWOT's api for the current domain. '''

        return self.MYWOT_API % self.domain


    def get_reputation_score(self, n):
        ''' Return the reputation score based on the thresholds of MyWOT.
            http://www.mywot.com/wiki/API#Reputation_and_confidence '''

        ## get the value of the "n" reputation
        value = getattr(self, 'reputation_' + str(n))
        if value is None:
            return MYWOT_REPUTATION_SCOREMIN

        ## calculate the score of the reputation
        score = MYWOT_REPUTATION_SCOREMAX
        for v in MYWOT_REPUTATION_SCOREVAL:
            if v <= value:
                return score
            score -= 1
        return score


    def get_confidence_score(self, n):
        ''' Return the confidence score based on the thresholds of MyWOT.
            http://www.mywot.com/wiki/API#Reputation_and_confidence '''

        value = getattr(self, 'confidence_' + str(n))
        if value is None:
            return MYWOT_CONFIDENCE_SCOREMIN

        ## calculate the score of the confidence
        score = MYWOT_CONFIDENCE_SCOREMAX
        for v in MYWOT_CONFIDENCE_SCOREVAL:
            if v <= value:
                return score
            score -= 1
        return score


    def get_reputation_score_label(self, n):
        u''' Return the lable of the specified reputation score. '''

        value = self.get_reputation_score(n)
        return MYWOT_REPUTATION_SCORELBL[value]


    def get_confidence_score_label(self, n):
        u''' Return the lable of the specified confidence score. '''

        value = self.get_confidence_score(n)
        return MYWOT_CONFIDENCE_SCORELBL[value]


    def get_reputation_score_image(self, n):
        u''' Return the image of the specified reputation score. '''

        score = self.get_reputation_score(n)
        return os.path.join(
            settings.MEDIA_URL, 'mywot',
            'reputation-%d.png' % score
        )


    def get_confidence_score_image(self, n):
        u''' Return the image of the specified confidence score. '''

        score = self.get_confidence_score(n)
        return os.path.join(
            settings.MEDIA_URL, 'mywot',
            'confidence-%d.png' % score
        )


    @staticmethod
    def get_or_create_object(url):
        u''' Return the existent object with the specified domain, if it doesn't exists, create it. '''

        ## extract the domain from the URL
        domain = Target.URL_PROTOCOL_RE.sub('', url)
        domain = Target.URL_PATHINFO_RE.sub('', domain)

        try:
            # try to get an existent object
            target = Target.objects.get(domain=domain)

        except Target.DoesNotExist:
            # ... if it doesn't exist, create it
            target = Target(domain=domain)
            target.load_values()
            target.save()

        else:
            # ... if it exists, check if it's not expired
            delta = datetime.now() - target.last_update
            if delta.days > MYWOT_EXPIRATION_DAYS:
                target.load_values()
                target.save()

        finally:
            #... finally, return the object
            return target
