from django.db import models

from onhand.management.models import Basis, Financing, AttachmentType, County, GovernmentLevel, Agency
from onhand.subscription.models import Company, CompanyPersonRole, Subscription


class InsuranceCarrier(models.Model):
    icar_id = models.AutoField(primary_key=True)
    comp = models.ForeignKey(Company, models.DO_NOTHING, db_column='comp_id', verbose_name=('company'))

    def __str__(self):
        return "%s (%s)" % (self.comp, self.icar_id)

    class Meta:
        db_table = 'oh_insurance_carrier'
        verbose_name = ("insurancecarrier")
        verbose_name_plural = "insurancecarrier"


class InsuranceDocType(models.Model):
    idoc_code = models.CharField(primary_key=True, max_length=6, verbose_name=('code'))
    idoc_desc = models.CharField(max_length=60,verbose_name=('description'))

    def __str__(self):
        return "%s (%s)" % (self.idoc_desc, self.idoc_code)

    class Meta:
        db_table = 'oh_insurance_doc_type'
        verbose_name = ("insurancedoctype")
        verbose_name_plural = "insurancedoctype"


class InsuranceType(models.Model):
    inty_id = models.AutoField(primary_key=True)
    agen_code = models.ForeignKey(Agency, models.DO_NOTHING, db_column='agen_code', verbose_name=('agency'),default=None)
    basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code', verbose_name=('basis'))
    inty_desc = models.CharField(max_length=60, verbose_name=('description'))

    def __str__(self):
        return "%s (%s)" % (self.inty_desc, self.inty_id)

    class Meta:
        db_table = 'oh_insurance_type'
        verbose_name = ("insurancetype")
        verbose_name_plural = "insurancetypes"


class InsuranceTypeJurisdiction(models.Model):
    insj_id = models.AutoField(primary_key=True)
    cont = models.ForeignKey(County, models.DO_NOTHING, db_column='cont_id', verbose_name=('county'), default='1859')
    govl_code = models.ForeignKey(GovernmentLevel, models.DO_NOTHING, db_column='govl_code', default='M')
    inty = models.ForeignKey(InsuranceType, models.DO_NOTHING, db_column='inty_id', verbose_name=('insurancetype'))
    insj_help_text = models.TextField(blank=True, null=True, verbose_name=('helptext'))

    def __str__(self):
        return "%s (%s)" % (self.insj_id, self.jurs)

    class Meta:
        db_table = 'oh_insurance_type_jurisdiction'
        verbose_name = ("insurancetypejurisdiction")
        verbose_name_plural = "insurancetypejurisdictions"
        unique_together = (('inty', 'cont', 'govl_code'),)



class InsurancePolicy(models.Model):
    ipol_id = models.AutoField(primary_key=True)
    basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code',  verbose_name=('jurisdiction'))
    icar = models.ForeignKey(InsuranceCarrier, models.DO_NOTHING, blank=True, null=True, db_column='icar_id', verbose_name=('insurancecarrier'))
    cprs = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, blank=True, null=True, db_column='cprs_id', verbose_name=('companypersonrole'))
    fina = models.ForeignKey(Financing, models.DO_NOTHING, blank=True, null=True, db_column='fina_id', verbose_name=('financing'))
    subs = models.ForeignKey(Subscription, models.DO_NOTHING, db_column='subs_id', verbose_name=('subscription'))
    insj = models.ForeignKey(InsuranceTypeJurisdiction, models.DO_NOTHING, db_column='insj_id', verbose_name=('insurancetypejurisdiction'))
    ipol_alert_date = models.DateField(blank=True, null=True,  verbose_name=('alertdate'))
    ipol_start_date = models.DateField(blank=True, null=True,  verbose_name=('startdate'))
    ipol_end_date = models.DateField(blank=True, null=True,  verbose_name=('enddate'))
    ipol_policy_no = models.CharField(max_length=40, blank=True, null=True, verbose_name=('policy_no'))
    ipol_premium = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True, verbose_name=('premium'))

    def __str__(self):
        return "%s " % (self.ipol_id)

    class Meta:
        db_table = 'oh_insurance_policy'
        verbose_name = ("insurancepolicy")
        verbose_name_plural = "insurancepolicies"


class InsurancePolicyAtt(models.Model):
    ipat_id = models.AutoField(primary_key=True)
    ipol = models.ForeignKey(InsurancePolicy, models.DO_NOTHING,  db_column='insj_id', verbose_name=('insurancepolicy'))
    atyp_code = models.ForeignKey(AttachmentType, models.DO_NOTHING, db_column='atyp_code', verbose_name=('attachmenttype'))
    idoc_code = models.ForeignKey(InsuranceDocType, models.DO_NOTHING, db_column='idoc_code', verbose_name=('insurancedoctype'))
    ipat_title = models.CharField(max_length=60, verbose_name=('title'))
    ipat_note = models.TextField(blank=True, null=True, verbose_name=('note'))
    ipat_attachment = models.TextField( verbose_name=('attachment'))
    ipat_date = models.DateTimeField(verbose_name=('date'))
    ipat_file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=('filename'))

    def __str__(self):
        return "%s " % (self.ipat_id)

    class Meta:
        db_table = 'oh_insurance_policy_att'
        verbose_name = ("insurancepolicyatt")
        verbose_name_plural = "insurancepolicyatt"
