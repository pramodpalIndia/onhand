from django.db import models

from onhand.management.models import Agency, Basis, AttachmentType, County, GovernmentLevel
from onhand.subscription.models import Subscription, CompanyPersonRole


class SubmissionType(models.Model):
    subt_id = models.AutoField(primary_key=True)
    agen_code = models.ForeignKey(Agency, models.DO_NOTHING, db_column='agen_code', verbose_name=('agency'))
    basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code', verbose_name=('basis'))
    subt_desc = models.CharField(max_length=60)

    def __str__(self):
        return "%s (%s)" % (self.subt_desc, self.subt_id)

    class Meta:
        db_table = 'oh_submission_type'
        verbose_name = ("submissiontype")
        verbose_name_plural = "subscriptions"

class SubmissionTypeJurisdiction(models.Model):
    subj_id = models.AutoField(primary_key=True)
    subt = models.ForeignKey(SubmissionType, models.DO_NOTHING, db_column='subt_id', verbose_name=('submissiontype'))
    cont = models.ForeignKey(County, models.DO_NOTHING, db_column='cont_id', verbose_name=('county'), default='1859')
    govl_code = models.ForeignKey(GovernmentLevel, models.DO_NOTHING, db_column='govl_code', default='M')
    subj_help_text = models.TextField(blank=True, null=True,  verbose_name=('agency'))

    def __str__(self):
        return "%s (%s)" % (self.subj_id, self.subt)

    class Meta:
        db_table = 'oh_submission_type_jurisdiction'
        verbose_name = ("submissiontypejurisdiction")
        verbose_name_plural = "submissiontypejurisdiction"
        unique_together = (('subt', 'cont', 'govl_code'),)


class Submission(models.Model):
    subm_id = models.AutoField(primary_key=True)
    subs = models.ForeignKey(Subscription, models.DO_NOTHING, db_column='subs_id', verbose_name=('subscription'))
    cprs = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cprs_id', verbose_name=('subscription'))
    subj = models.ForeignKey(SubmissionTypeJurisdiction, models.DO_NOTHING, db_column='subj_id', verbose_name=('submissiontypejurisdiction'))
    basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code',  verbose_name=('basis'))
    subm_amt = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True,  verbose_name=('amount'))
    subm_ref = models.CharField(max_length=60, blank=True, null=True,  verbose_name=('reference'))
    subm_desc = models.CharField(max_length=60, blank=True, null=True,  verbose_name=('description'))
    subm_alert_date = models.DateField(blank=True, null=True,  verbose_name=('alertdate'))
    subm_due_date = models.DateField( verbose_name=('duedate'))
    subm_file_date = models.DateField(blank=True, null=True,  verbose_name=('filedate'))
    subm_preparer_fee = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True,  verbose_name=('preparerfee'))
    subm_date = models.DateTimeField(blank=True, null=True,  verbose_name=('date'))

    def __str__(self):
        return "%s " % (self.subm_id)

    class Meta:
        db_table = 'oh_submission'
        verbose_name = ("submission")
        verbose_name_plural = "submission"

class SubmissionAttachment(models.Model):
    suba_id = models.AutoField(primary_key=True)
    subm = models.ForeignKey(Submission, models.DO_NOTHING, db_column='subs_id', verbose_name=('submission'))
    atyp_code = models.ForeignKey(AttachmentType, models.DO_NOTHING, db_column='atyp_code', verbose_name=('attachmenttype'))
    suba_date = models.DateTimeField(verbose_name=('date'))
    suba_note = models.TextField(blank=True, null=True,verbose_name=('note'))
    suba_attachment = models.TextField(verbose_name=('attachment'))

    def __str__(self):
        return "%s " % (self.suba_id)

    class Meta:
        db_table = 'oh_submission_attachment'
        verbose_name = ("submissionattachment")
        verbose_name_plural = "submissionattachments"
