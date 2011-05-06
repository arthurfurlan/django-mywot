# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime
from xml.dom import minidom
from urllib2 import urlopen
import re


## number of days required to expiry the loaded values
MYWOT_EXPIRATION_DAYS = getattr(settings, 'MYWOT_EXPIRATION_DAYS', 180)


class DomainRequiredError(Exception):
    pass


class Target(models.Model):

    domain = models.CharField(max_length=255, unique=True, db_index=True)
    last_update = models.DateTimeField(auto_now=True)

    ## reputation values
    reputation_0 = models.IntegerField(u'Trustworthiness', blank=True, null=True)
    reputation_1 = models.IntegerField(u'Vendor reliability', blank=True, null=True)
    reputation_2 = models.IntegerField(u'Privacy', blank=True, null=True)
    reputation_4 = models.IntegerField(u'Child safety', blank=True, null=True)

    ## confidence of the reputation values
    confidence_0 = models.IntegerField(u'Confidence of "Trustworthiness"', blank=True, null=True)
    confidence_1 = models.IntegerField(u'Confidence of "Vendor reliability"', blank=True, null=True)
    confidence_2 = models.IntegerField(u'Confidence of "Privacy"', blank=True, null=True)
    confidence_4 = models.IntegerField(u'Confidence of "Child safety"', blank=True, null=True)

    ## url of the mywot's api
    MYWOT_API = ' http://api.mywot.com/0.4/public_query2?target=%s'

    ## regular expression to validate domain names
    DOMAIN_RE = re.compile(
        r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,6}\.?$',
        re.IGNORECASE,
    )


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


    @staticmethod
    def get_or_create_object(domain):
        u''' Return the existent object with the specified domain, if it doesn't exists, create it. '''

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
