from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from onhand.compliance.models import ComplianceService, ServiceJurisdiction


# csrv_id = models.AutoField(primary_key=True)
# basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code', verbose_name=('basis'))
# srvj = models.ForeignKey(ServiceJurisdiction, models.DO_NOTHING, db_column='srvj_id',
#                          verbose_name=('servicejurisdiction'))
# subs = models.ForeignKey(Subscription, models.DO_NOTHING, db_column='subs_id', verbose_name=('subscription'))
# csrv_alert_date = models.DateField(blank=True, null=True, verbose_name=('alertdate'))
# csrv_due_date = models.DateField(verbose_name=('duedate'))
# csrv_note = models.TextField(blank=True, null=True, verbose_name=('note'))


# srvj_id = models.AutoField(primary_key=True)
# ctyp = models.ForeignKey(ComplianceServiceType, models.DO_NOTHING, db_column='ctyp_id',
#                          verbose_name=('complianceservicetype'))
# cont = models.ForeignKey(County, models.DO_NOTHING, db_column='cont_id', verbose_name=('county'), default='1859')
# govl_code = models.ForeignKey(GovernmentLevel, models.DO_NOTHING, db_column='govl_code', default='M',
#                               verbose_name=('govermentlevl'))
# srvj_help_text = models.TextField(blank=True, null=True, verbose_name=('helptext'))

# @admin.register(ServiceJurisdiction)
# class SiteAdmin(admin.ModelAdmin):
#     list_display = ('ctyp', 'cont','govl_code')
#     search_fields = ('ctyp', 'cont','govl_code')
#
#
#
# class ComplianceServiceJurisdictionLevelFilter(SimpleListFilter):
#     """
#     List filter example that shows only referenced(used) values
#     """
#     title = 'CountryExample'
#     parameter_name = 'CountryExample'
#
#     def lookups(self, request, model_admin):
#         # You can use also "CountryExample" instead of "model_admin.model"
#         # if this is not direct relation
#         countries = set([c.CountryExample for c in model_admin.model.objects.all()])
#         return [(c.id, c.name) for c in countries]
#
#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(CountryExample__id__exact=self.value())
#         else:
#             return queryset


@admin.register(ComplianceService)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('subs_id', 'srvj')
    search_fields = ('subs_id', 'srvj')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(CountryExample__id__exact=self.value())
        else:
            return queryset

