from __future__ import unicode_literals
from django.db import models
# from onhand.management.models import Address
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from onhand.management.models import Address, Language, NaicsLevel5, Salessource, Permission
from onhand.products.models import ProductBasis, ProductDiscount

from . import app_settings



class Person(models.Model):
    prsn_id = models.AutoField(primary_key=True, verbose_name=('person'))
    address = models.ForeignKey(Address, models.DO_NOTHING, blank=True, null=True,db_column='addr_id', verbose_name=('address'))
    first_name = models.CharField(max_length=20,db_column='prsn_fname',verbose_name=('first name'))
    last_name = models.CharField(max_length=20,db_column='prsn_lname', verbose_name=('last name' ),blank=True, null=True,)
    office_phone = models.CharField(max_length=20, blank=True, null=True,db_column='prsn_office_phone', verbose_name=('office phone'))
    mobile_phone = models.CharField(max_length=20, blank=True, null=True,db_column='prsn_mobile_phone', verbose_name=('mobile phone'))
    fax = models.CharField(max_length=20, blank=True, null=True,db_column='prsn_fax', verbose_name=('fax'))
    email = models.CharField(max_length=60, blank=True, null=True,db_column='prsn_email', verbose_name=('email'))
    skype = models.CharField(max_length=40, blank=True, null=True,db_column='prsn_skype', verbose_name=('skype'))
    facebook = models.CharField(max_length=40, blank=True, null=True,db_column='prsn_facebook', verbose_name=('facebook'))
    notes = models.TextField(blank=True, null=True,db_column='prsn_notes', verbose_name=('notes'))

    def __str__(self):
        return "%s (%s)" % (self.first_name, self.last_name)

    class Meta:
        db_table = 'oh_person'
        verbose_name = ("person")
        verbose_name_plural = "Person"


class Company(models.Model):
    comp_id = models.AutoField(primary_key=True, verbose_name=('company'))
    comp_id_parent = models.IntegerField(blank=True, null=True, verbose_name=('parentcompany'))
    address = models.ForeignKey(Address, models.DO_NOTHING, blank=True, null=True, db_column='addr_id', verbose_name=('address'))
    name = models.CharField(max_length=30,db_column='comp_name', verbose_name=('name'))
    email = models.CharField(max_length=40, blank=True, null=True,db_column='comp_email', verbose_name=('email'))
    website = models.CharField(max_length=60, blank=True, null=True,db_column='comp_website', verbose_name=('website'))
    phone = models.CharField(max_length=20, blank=True, null=True,db_column='comp_phone', verbose_name=('phone'))
    fax = models.CharField(max_length=20, blank=True, null=True,db_column='comp_fax', verbose_name=('fax'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'oh_company'
        verbose_name = ("company")
        verbose_name_plural = "companies"

class PersonLanguage(models.Model):
    prsn = models.ForeignKey(Person, models.DO_NOTHING, verbose_name=('person'))
    lang_code = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_code', verbose_name=('languagecode'),default='ENG')
    plng_is_preferred = models.CharField(max_length=1, blank=True, null=True, verbose_name=('preferredlanguage'))

    def __str__(self):
        return "%s (%s)" % (self.prsn, self.lang_code)

    class Meta:
        db_table = 'oh_person_language'
        verbose_name = ("personlanguage")
        verbose_name_plural = "personlanguages"
        unique_together = (('prsn', 'lang_code'),)

class CompanyLanguage(models.Model):
    comp = models.ForeignKey(Company, models.DO_NOTHING, verbose_name=('company'))
    lang_code = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_code',default='ENG',
                                  verbose_name=('languagecode'))
    clng_is_preferred = models.CharField(max_length=1, blank=True, null=True,
                                         verbose_name=('preferredlanguage'))

    def __str__(self):
        return "%s (%s)" % (self.prsn, self.lang_code)

    class Meta:
        db_table = 'oh_company_language'
        verbose_name = ("companylanguage")
        verbose_name_plural = "companylanguages"
        unique_together = (('comp', 'lang_code'),)


class CompanyRole(models.Model):
    crol_code = models.CharField(primary_key=True, max_length=6,verbose_name=('code'))
    crol_desc = models.CharField(max_length=60, verbose_name=('description'))

    def __str__(self):
        return "%s (%s)" % (self.crol_desc, self.crol_code)

    class Meta:
        db_table = 'oh_company_role'
        verbose_name = ("companyrole")
        verbose_name_plural = "companyroles"


class CompanyPersonRole(models.Model):
    cprs_id = models.AutoField(primary_key=True)
    comp = models.ForeignKey(Company, models.DO_NOTHING,db_column='comp_id', verbose_name=('company'))
    prsn = models.ForeignKey(Person, models.DO_NOTHING,db_column='prsn_id', verbose_name=('person'))
    cprs_id_manager = models.ForeignKey('self', models.DO_NOTHING, db_column='cprs_id_manager', blank=True, null=True,verbose_name=('manager'))
    crol_code = models.ForeignKey(CompanyRole, models.DO_NOTHING, db_column='crol_code',verbose_name=('role'),default='OWNER')
    cprs_start_date = models.DateField(blank=True, null=True,verbose_name=('startdate'))
    cprs_end_date = models.DateField(blank=True, null=True,verbose_name=('enddate'))

    def __str__(self):
        return "%s" % (self.cprs_id)

    class Meta:
        db_table = 'oh_company_person_role'
        verbose_name = ("companypersonrole")
        verbose_name_plural = "companypersonroles"


class Subscription(models.Model):
    subs_id = models.AutoField(primary_key=True)
    comp = models.ForeignKey(Company, models.DO_NOTHING,db_column='comp_id',verbose_name=('company'))
    ssrc = models.ForeignKey(Salessource, models.DO_NOTHING,db_column='ssrc_id',verbose_name=('salessource'))
    subs_naic_group_level = models.IntegerField(verbose_name=('default'))
    subs_cc_exp_date = models.DateField(verbose_name=('ccexpiredate'))
    subs_api_id = models.IntegerField(blank=True, null=True,verbose_name=('subscriptionapi'),default='000001')
    subs_alert_date = models.DateField(blank=True, null=True,verbose_name=('alertdate'))
    subs_referring_url = models.CharField(max_length=2000, blank=True, null=True,verbose_name=('referring_url'))
    naic_level_5_code = models.ForeignKey(NaicsLevel5, models.DO_NOTHING, db_column='naic_level_5_code',verbose_name=('naicslevel5'),default='722511')
    subs_api_payment_id = models.IntegerField(default='000001')
    subs_payment_method = models.CharField(max_length=1,default='C')
    subs_termination_date = models.DateTimeField(blank=True, null=True, verbose_name=('terminationdate'))
    subs_termination_reason = models.CharField(max_length=2000, blank=True, null=True, verbose_name=('reason'))

    def __str__(self):
        return "%s" % (self.comp)

    class Meta:
        db_table = 'oh_subscription'
        verbose_name = ("subscription")
        verbose_name_plural = "subscriptions"



class SubscriptionDetail(models.Model):
    subd_id = models.AutoField(primary_key=True)
    subs = models.ForeignKey(Subscription, models.DO_NOTHING,db_column='subs_id',verbose_name=('subscription'))
    prdb = models.ForeignKey(ProductBasis, models.DO_NOTHING,db_column='prdb_id',verbose_name=('productbasis'))
    subd_id_first = models.ForeignKey('self', models.DO_NOTHING, db_column='subd_id_first',default='1')
    cprs = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, blank=True, null=True,db_column='cprs_id',verbose_name=('companypersonrole'))
    pdis = models.ForeignKey(ProductDiscount, models.DO_NOTHING, blank=True, null=True,db_column='pdis_id',verbose_name=('productdiscount'))
    subd_start_date = models.DateField(verbose_name=('subscriptionstartdate'))
    subd_end_date = models.DateField(verbose_name=('subscriptionenddate'))
    subd_list_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name=('listprice'))
    subd_discount_percent = models.DecimalField(max_digits=8, decimal_places=5,verbose_name=('discount'),default=0)
    subd_net_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name=('netprice'))
    subd_sales_tax = models.DecimalField(max_digits=18, decimal_places=2, verbose_name=('salestax'),default=0)
    subd_date = models.DateTimeField(verbose_name=('subscribeddate'))

    def __str__(self):
        return "%s (%s)" % (self.subd_id, self.subs)

    class Meta:
        db_table = 'oh_subscription_detail'
        verbose_name = ("subscriptiondetail")
        verbose_name_plural = "subscriptionsdetails"

class SubscriptionUser(models.Model):
    from onhand.users.models import User
    subu_id = models.AutoField(primary_key=True)
    subs = models.ForeignKey(Subscription, models.DO_NOTHING,db_column='subs_id',verbose_name=('Subscription'))
    user = models.ForeignKey(User, models.DO_NOTHING,db_column='user_id',verbose_name=('User'))
    perm_code = models.ForeignKey(Permission, models.DO_NOTHING, db_column='perm_code')

    def __str__(self):
        return "%s" % (self.subu_id)

    class Meta:
        db_table = 'oh_subscription_user'
        verbose_name = ("SubscriptionUser")
        verbose_name_plural = "SubscriptionUsers"
