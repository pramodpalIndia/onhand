import datetime

from django.db import models
from django.utils.timezone import now
from onhand.management.models import Agency, Basis, County, Financing, AttachmentType, GovernmentLevel, Country, State
from onhand.subscription.models import Subscription, CompanyPersonRole, Company


class ComplianceServiceType(models.Model):
    ctyp_id = models.AutoField(primary_key=True)
    agen_code = models.ForeignKey(Agency, models.DO_NOTHING, db_column='agen_code', verbose_name=('agency'))
    basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code', verbose_name=('basis'))
    ctyp_desc = models.CharField(max_length=60, verbose_name=('description'))

    def __str__(self):
        return "%s" % (self.ctyp_desc)
        # return "%s ( %s / %s )" % (self.ctyp_desc, self.agen_code.agen_name, self.basi_code.basi_desc)


    class Meta:
        db_table = 'oh_compliance_service_type'
        verbose_name = ("complianceservicetype")
        verbose_name_plural = "complianceservicetypes"




class ServiceJurisdiction(models.Model):
    srvj_id = models.AutoField(primary_key=True)
    ctyp = models.ForeignKey(ComplianceServiceType, models.DO_NOTHING, db_column='ctyp_id', verbose_name=('Service (Agency/Basis)'))
    cont = models.ForeignKey(County, models.DO_NOTHING, db_column='cont_id', verbose_name=('county'), default='1859')
    govl_code = models.ForeignKey(GovernmentLevel, models.DO_NOTHING, db_column='govl_code', default='M', verbose_name=('govermentlevl'))
    srvj_help_text = models.TextField(blank=True, null=True, verbose_name=('helptext'))

    def __str__(self):
        # return "%s" % (self.ctyp.ctyp_desc)
        # return "%s / %s / %s" % (self.ctyp.ctyp_desc, self.ctyp.agen_code.agen_name, self.govl_code.govl_desc)
        return "%s / %s " % (self.ctyp.ctyp_desc, self.ctyp.agen_code.agen_name)

    class Meta:
        db_table = 'oh_service_jurisdiction'
        verbose_name = ("servicejurisdiction")
        verbose_name_plural = "servicejurisdictions"
        unique_together = (('ctyp', 'cont', 'govl_code'),)


class Factor(models.Model):
    fact_code = models.CharField(primary_key=True,db_column='fact_code', max_length=6, verbose_name=('code'))
    ctyp = models.ForeignKey(ComplianceServiceType, models.DO_NOTHING, db_column='ctyp_id', verbose_name=('complianceservicetype'))
    fact_desc = models.CharField(max_length=60, verbose_name=('description'))

    def __str__(self):
        return "%s" % (self.fact_code)

    class Meta:
        db_table = 'oh_factor'
        verbose_name = ("factor")
        verbose_name_plural = "factors"


class ComplianceService(models.Model):
    csrv_id = models.AutoField(primary_key=True)
    basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code', verbose_name='basis', default="ANNUAL")
    srvj = models.ForeignKey(ServiceJurisdiction, models.DO_NOTHING, db_column='srvj_id' , verbose_name=('services / Jurisdiction / Level'))
    subs = models.ForeignKey(Subscription, models.DO_NOTHING, db_column='subs_id', verbose_name=('subscription'))
    csrv_alert_date = models.DateField(blank=True, null=True, verbose_name=('alertdate'))
    csrv_due_date = models.DateField(verbose_name=('duedate'))
    csrv_note = models.TextField(blank=True, null=True, verbose_name=('note'))

    def __str__(self):
        return "%s" % (self.csrv_id)

    class Meta:
        db_table = 'oh_compliance_service'
        verbose_name = ("complianceservice")
        verbose_name_plural = "complianceservices"

class ScheduleStatus(models.Model):
    schs_code = models.CharField(primary_key=True, max_length=6)
    schs_desc = models.CharField(max_length=60)

    def __str__(self):
        return "%s" % (self.schs_code)

    class Meta:
        db_table = 'oh_schedule_status'
        verbose_name = ("schedulestatus")
        verbose_name_plural = "schedulestatus"


class ComplianceServiceSchedule(models.Model):
    cssc_id = models.AutoField(primary_key=True)
    csrv = models.ForeignKey(ComplianceService, models.DO_NOTHING, db_column='csrv_id', verbose_name='ComplianceService',default='2')
    comp = models.ForeignKey(Company, models.DO_NOTHING, db_column='comp_id',
                             verbose_name='company',default='1')
    schs_code = models.ForeignKey(ScheduleStatus, models.DO_NOTHING, db_column='schs_code',default='PEND')
    cprs_id_provider = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cprs_id_provider', blank=True, null=True,
                                         related_name='cprs_id_provider_scd', verbose_name='Provider')
    cprs_id_responsible = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cprs_id_responsible',
                                         related_name='cprs_id_responsible_scd', verbose_name='Responsible', default='2')
    cprs_id_assigner = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cprs_id_assigner', related_name='cprs_id_assigner_scd', verbose_name='Assigner', default='2')
    cssc_service_date = models.DateTimeField( db_column='cssc_service_date', verbose_name='Scheduled_Date',default=now)
    cssc_note = models.TextField(blank=True, null=True, db_column='cssc_note', verbose_name='Note')
    cssc_date = models.DateTimeField( db_column='cssc_date', verbose_name='Date_Created',default=now)


    def __str__(self):
        return "%s " % (self.cssc_id)

    class Meta:
        db_table = 'oh_compliance_service_schedule'
        verbose_name = ("ComplianceServiceSchedule")
        verbose_name_plural = "ComplianceServiceSchedules"

class ComplianceServiceAction(models.Model):
    csac_id = models.AutoField(primary_key=True)
    csrv = models.ForeignKey(ComplianceService, models.DO_NOTHING,db_column='csrv_id', verbose_name='complianceservice')
    comp = models.ForeignKey(Company, models.DO_NOTHING,db_column='comp_id', verbose_name='company',default='')
    cssc = models.ForeignKey(ComplianceServiceSchedule, models.DO_NOTHING, blank=True, null=True, db_column='cssc_id', verbose_name='serviceschedule')
    fina = models.ForeignKey(Financing, models.DO_NOTHING,db_column='fina_id', blank=True, null=True, verbose_name='Financing')
    csac_service_date = models.DateField(verbose_name='servicedate')
    csac_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='price')
    csac_note = models.TextField(blank=True, null=True, verbose_name='note')
    csac_date = models.DateTimeField(verbose_name='date')
    cprs_id = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cprs_id', related_name='cprs_id_recorder', verbose_name='Recorded By', default=1)

    def __str__(self):
        return "%s " % (self.csac_id)

    class Meta:
        db_table = 'oh_compliance_service_action'
        verbose_name = ("complianceserviceaction")
        verbose_name_plural = "complianceserviceactions"

class ProviderServicePerson(models.Model):
    psvp_id = models.AutoField(primary_key=True)
    csac = models.ForeignKey(ComplianceServiceAction, models.DO_NOTHING,db_column='csac_id', verbose_name='complianceserviceaction')
    cprs = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING,db_column='cprs_id', verbose_name='companyperson')

    def __str__(self):
        return "%s " % (self.psvp_id)

    class Meta:
        db_table = 'oh_provider_service_person'
        verbose_name = ("ProviderServicePerson")
        verbose_name_plural = "ProviderServicePerson"


class ComplianceServiceActionAtt(models.Model):
    csaa_id = models.AutoField(primary_key=True)
    csac = models.ForeignKey(ComplianceServiceAction, models.DO_NOTHING, db_column='csac_id', verbose_name=('complianceserviceaction'))
    atyp_code = models.ForeignKey(AttachmentType, models.DO_NOTHING, db_column='atyp_code', verbose_name=('attachmenttype'))
    csaa_title = models.CharField(max_length=60, verbose_name=('title'))
    csaa_note = models.TextField(blank=True, null=True, verbose_name=('note'))
    csaa_attachment = models.TextField(verbose_name=('attachment'))
    csaa_date = models.DateTimeField( verbose_name=('date'))
    csaa_file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=('filename'))


    def __str__(self):
        return "%s " % (self.csaa_id)

    class Meta:
        db_table = 'oh_compliance_service_action_att'
        verbose_name = ("complianceserviceactionatt")
        verbose_name_plural = "complianceserviceactionatt"


class ComplianceServiceAtt(models.Model):
    csat_id = models.AutoField(primary_key=True)
    csrv = models.ForeignKey(ComplianceService, models.DO_NOTHING, db_column='csrv_id', verbose_name=('complianceservice'))
    atyp_code = models.ForeignKey(AttachmentType, models.DO_NOTHING, db_column='atyp_code', verbose_name=('filename'))
    csat_title = models.CharField(max_length=60, verbose_name=('title'))
    csat_note = models.TextField(blank=True, null=True, verbose_name=('note'))
    csat_attachment = models.TextField(verbose_name=('attachment'))
    csat_date = models.DateTimeField(verbose_name=('date'))
    csat_file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=('filename'))

    def __str__(self):
        return "%s " % (self.csat_id)

    class Meta:
        db_table = 'oh_compliance_service_att'
        verbose_name = ("complianceserviceatt")
        verbose_name_plural = "complianceserviceatt"

class ComplianceResponsibility(models.Model):
    cres_id = models.AutoField(primary_key=True)
    csrv = models.ForeignKey(ComplianceService, models.DO_NOTHING, db_column='csrv_id')
    cprs_id_responsible = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cprs_id_responsible', related_name='cprs_id_responsible', verbose_name='Responsible',default='2')
    cprs_id_assigner = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cprs_id_assigner', related_name='cprs_id_assigner_res', verbose_name='Assigner',default='2')
    cres_is_active = models.CharField(max_length=1)
    cres_note = models.TextField(blank=True, null=True)
    cres_date = models.DateTimeField()

    def __str__(self):
        return "%s " % (self.cres_id)

    class Meta:
        db_table = 'oh_compliance_responsibility'
        verbose_name = "ComplianceResponsibility"
        verbose_name_plural = "ComplianceResponsibility"

class CompanyServiceJurisdiction(models.Model):
    csrj_id = models.AutoField(primary_key=True)
    comp = models.ForeignKey(Company, models.DO_NOTHING, db_column='comp_id', default='1', verbose_name='Company')
    srvj = models.ForeignKey(ServiceJurisdiction, models.DO_NOTHING, db_column='srvj_id', default='1', verbose_name='Jurisdiction')

    def __str__(self):
       return "%s" % (self.csrj_id)

    class Meta:
       db_table = 'oh_company_service_jurisdiction'
       verbose_name = "CompanyServiceJurisdiction"
       verbose_name_plural = "CompanyServiceJurisdictions"


class FactorValue(models.Model):
    fval_id = models.AutoField(primary_key=True)
    csrv = models.ForeignKey(ComplianceService, models.DO_NOTHING, db_column='csrv_id', verbose_name='Compliance')
    fact = models.ForeignKey(Factor, models.DO_NOTHING, db_column='fact_code',verbose_name='code')
    fval_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='value')

    def __str__(self):
        return "%s" % (self.fval_id)

    class Meta:
        db_table = 'oh_factor_value'
        verbose_name = ("factorvalue")
        verbose_name_plural = "factorsvalues"
        unique_together = (('csrv', 'fact'))

# class ProviderServicePerson(models.Model):
#     psvp_id = models.AutoField(primary_key=True)
#     csac = models.ForeignKey(ComplianceServiceAction, models.DO_NOTHING,db_column='csac_id', verbose_name='Service action', default=1)
#     cprs = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING,db_column='cprs_id', verbose_name='Person Id', default=1)
#
#     def __str__(self):
#         return "%s" % (self.psvp_id)
#
#     class Meta:
#         db_table = 'oh_provider_service_person'
#         verbose_name = "providerserviceperson"
#         verbose_name_plural = "providerserviceperson"


class V_Service_jurisdiction(models.Model):
    # ctry_code = models.CharField(primary_key=True, max_length=6, db_column='ctry_code', verbose_name=('CountryCode'))
    ctry_code = models.ForeignKey(Country, models.DO_NOTHING, db_column='ctry_code', verbose_name=('country'))
    ctry_name = models.CharField(max_length=60, db_column='ctry_name', verbose_name=('Countryname'))
    # stat_code = models.CharField(primary_key=True, max_length=2, db_column='stat_code', verbose_name=('Statecode'))
    stat_code = models.ForeignKey(State, models.DO_NOTHING, db_column='stat_code', verbose_name=('state'))
    stat_name = models.CharField(max_length=60, db_column='stat_name', verbose_name=('Statename'))
    # cont_id = models.AutoField(primary_key=True, db_column='cont_id', verbose_name=('Countyid'))
    cont_id = models.ForeignKey(County, models.DO_NOTHING, db_column='cont_id', verbose_name=('county'), default='1859')
    cont_name = models.CharField(max_length=60, db_column='cont_name', verbose_name=('Countyname'))
    agen_code = models.ForeignKey(Agency, models.DO_NOTHING, db_column='agen_code', verbose_name=('agency'))
    srvj_id = models.ForeignKey(ServiceJurisdiction, models.DO_NOTHING, db_column='srvj_id',
                             verbose_name=('services'))
    ctyp_id = models.ForeignKey(ComplianceServiceType, models.DO_NOTHING, db_column='ctyp_id', verbose_name=('Service (Agency/Basis)'))
    govl_code = models.ForeignKey(GovernmentLevel, models.DO_NOTHING, db_column='govl_code', default='M', verbose_name=('govermentlevl'))
    srvj_help_text = models.TextField(blank=True, null=True, verbose_name=('helptext'))

    def __unicode__(self):
        return u'{0}'.format(self.lname)

    def __str__(self):
        return "%s " % (self.ctyp_id)

    class Meta:
        managed = False
        db_table = 'V_Service_jurisdiction'
        verbose_name = ("V_Service_jurisdiction")
        verbose_name_plural = "V_Service_jurisdiction"

class v_provider_jurisdiction(models.Model):
    comp = models.ForeignKey(Company, models.DO_NOTHING, db_column='comp_id',verbose_name='company')
    srvj_id = models.ForeignKey(ServiceJurisdiction, models.DO_NOTHING, db_column='srvj_id', verbose_name=('services'))
    comp_name = models.CharField(primary_key=True,max_length=30, db_column='comp_name', verbose_name=('name'))
    comp_phone = models.CharField(max_length=20, blank=True, null=True, db_column='comp_phone', verbose_name=('phone'))
    comp_email = models.CharField(max_length=40, blank=True, null=True, db_column='comp_email', verbose_name=('email'))
    ctyp_id = models.ForeignKey(ComplianceServiceType, models.DO_NOTHING, db_column='ctyp_id', verbose_name=('Service (Agency/Basis)'))
    ctyp_desc = models.CharField(max_length=60, db_column='ctyp_desc', verbose_name=('Compliance'))
    cont_id = models.ForeignKey(County, models.DO_NOTHING, db_column='cont_id', verbose_name=('county'))
    cont_name = models.CharField(max_length=60, db_column='cont_name', verbose_name=('Countyname'))

    def __unicode__(self):
        return u'{0}'.format(self.comp_name)

    def __str__(self):
        return "%s " % (self.ctyp_id)

    class Meta:
        managed = False
        db_table = 'v_provider_jurisdiction'
        verbose_name = ("v_provider_jurisdiction")
        verbose_name_plural = "v_provider_jurisdictions"

class v_last_compliance_service_action(models.Model):
    from onhand.subscription.models import Subscription, CompanyPersonRole
    from onhand.compliance.models import ComplianceServiceAction,ComplianceServiceSchedule,ServiceJurisdiction, ComplianceServiceType
    csrv_id = models.ForeignKey(ComplianceService, models.DO_NOTHING, db_column='csrv_id', verbose_name='Compliance')
    subs_id = models.ForeignKey(Subscription, models.DO_NOTHING, db_column='subs_id', verbose_name=('subscriber'))
    srvj_id = models.ForeignKey(ServiceJurisdiction, models.DO_NOTHING, db_column='srvj_id',verbose_name='Jurisdiction')
    csac_id = models.IntegerField(primary_key=True,db_column='csac_id',verbose_name='complianceserviceaction')
    comp_id = models.ForeignKey(Company, models.DO_NOTHING, db_column='comp_id', verbose_name='company')
    comp_name = models.CharField(primary_key=True, max_length=30, db_column='comp_name', verbose_name=('name'))
    comp_phone = models.CharField(max_length=20, blank=True, null=True, db_column='comp_phone', verbose_name=('phone'))
    comp_email = models.CharField(max_length=40, blank=True, null=True, db_column='comp_email', verbose_name=('email'))
    csac_price_last = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True,
                                          verbose_name=('lastprice'))
    csac_service_date_last = models.DateField(verbose_name=('lastservicedate'))
    cprs_id = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cprs_id',
                                            related_name='cprs_id_responsible_lastservic', verbose_name='Responsible')
    prsn_name = models.CharField(max_length=20, db_column='prsn_name', verbose_name=('prsn_name'))
    prsn_email = models.CharField(max_length=60, blank=True, null=True, db_column='prsn_email', verbose_name='Person email')
    prsn_mobile_phone = models.CharField(max_length=20, blank=True, null=True, db_column='prsn_mobile_phone',
                                    verbose_name='mobile phone')
    prsn_office_phone = models.CharField(max_length=20, blank=True, null=True, db_column='prsn_office_phone',
                                    verbose_name='office phone')

    def __str__(self):
        return "%s " % (self.csac_id)

    class Meta:
        managed = False
        db_table = 'v_last_compliance_service_action'
        verbose_name = "v_last_compliance_service_action"
        verbose_name_plural = "v_last_compliance_service_action"
