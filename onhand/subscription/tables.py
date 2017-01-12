import django_tables2 as tables
import itertools

from datetime import date
from django.db.models import F
from django_tables2 import TemplateColumn

from onhand.compliance.models import ServiceJurisdiction, ComplianceServiceType

import datetime
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm, Form





# from onhand.management.models import Basis
#
# basis = tuple(Basis.objects.values_list('basi_code', 'basi_desc'))
#

#
#
# class UpperColumn(tables.Column):
#     def render(self, value):
#         return value.upper()
#
from onhand.management.models import  GovernmentLevel


class CheckBoxService(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name

class DueRenewalDate(tables.DateColumn):
    @property
    def header(self):
        return self.verbose_name


class ServicesTable(tables.Table):
    select = CheckBoxService(verbose_name="Select", accessor="pk")
    servicetype = tables.Column(accessor='ctyp_id', verbose_name="Type")
    compliance = tables.Column(accessor='ctyp_id',verbose_name="Compliance")
    # frequency = tables.Column(accessor='ctyp_id', verbose_name="Frequency")
    frequency = TemplateColumn('<select> <option value="ANNUAL">Annual</option>'
                                   '<option value="BIAN">Bi-Annual</option><option value="QUARTE">Quartely</option>'
                                   '<option value="MNTHLY">Monthly</option><option value="Weekly">Annual</option></select>', verbose_name="Frequency")

    # renewaldate = tables.Column(accessor='ctyp_id', verbose_name="Due/Renewal date")
    # date_field = forms.DateField(widget=SelectDateWidget)
    renewaldate = tables.DateColumn(format="YYYY-MM-DD",verbose_name="Due/Renewal date")
    agency = tables.Column(accessor='ctyp_id', verbose_name="Agency")

    govermentlevel = tables.Column(accessor='govl_code', verbose_name="Goverment level")

    class Meta:
    #     # model = ServiceJurisdiction
        attrs = {'class': 'paleblue'}
        actions = tables.Column(orderable=True)


    def render_servicetype(self, record):
        return 'Service'

    def render_compliance(self, record):
        return str(ComplianceServiceType.objects.get(ctyp_id=  record.ctyp_id).ctyp_desc)

    # def render_frequency(self, record):
    #     # return '<%s>' % record
    #     return '<select> <option value="ANNUAL">Annual</option> <option value="BIAN" selected>Bi-Annual</option><option value="QUARTE">Quartely</option><option value="MNTHLY">Monthly</option><option value="Weekly">Annual</option></select>)'
    #     # return str(ComplianceServiceType.objects.get(ctyp_id=  record.ctyp_id).basi_code.basi_desc)

    # def render_renewaldate(self, record):
    #     return str(date.today())

    def render_agency(self, record):
        return str(ComplianceServiceType.objects.get(ctyp_id=  record.ctyp_id).agen_code.agen_name)

    def render_govermentlevel(self, record):
        return str(record.govl_code.govl_desc)
        # print('render_govermentlevel record.govl_code', str(record.govl_code.govl_desc))
        # print('render_govermentlevel objects', GovernmentLevel.objects.get(govl_code='M').govl_desc)
        # return str(GovernmentLevel.objects.get(govl_code=record.govl_code).govl_desc )
        # return str(Jurisdiction.objects.get(jurs_id=  record.jurs_id).govl_code.govl_desc)
        # return  None


    def order_compliance(self, queryset, is_descending):
        queryset = queryset.annotate(
            amount=F('shirts') + F('pants')
        ).order_by(('-' if is_descending else '') + 'amount')
        return (queryset, True)


#
#     # row_number = tables.Column(empty_values=())
#     # id = tables.Column()
#     # upper = UpperColumn()
#     # actions = tables.Column(orderable=False)
#     clothing = table.
#     # # select = CheckBoxService(verbose_name="Select", accessor="pk")
#     # #
#     # # frequency = TemplateColumn('<select> <option value="ANNUAL">Annual</option>'
#     #                            '<option value="BIAN">Bi-Annual</option><option value="QUARTE">Quartely</option>'
#     #                            '<option value="MNTHLY">Monthly</option><option value="Weekly">Annual</option></select>', verbose_name="Frequency")
#     #
#
#     # basi_code = tables.Column(verbose_name="Frequency", accessor='ServiceJurisdiction.ctyp_id')
#
#
#     class Meta:
#         model = ServiceJurisdiction
#
#         # fields =['jurs_id', 'ctyp_id',ServiceJurisdiction.ctyp.basi_code]
#         # sequence =['select','ctyp','jurs','clothing' ]
#         # exclude =['srvj_id', 'srvj_help_text']
#         attrs = {'class': 'paleblue'}
#
#
#     def render_clothing(self, record):
#         print('render_clothing',record)
#         return str(record.ctyp_id)
#
#
#     # def render_new_revision(self, record, value):
#     #     basislist = tables.Column()
#
#
#     # def __init__(self, *args, **kwargs):
#     #     super(ServicesTable, self).__init__(*args, **kwargs)
#     #     self.counter = itertools.count()
#
#     # def render_row_number(self):
#     #     return '%d' % next(self.counter)
#     #
#     # def render_id(self, value):
#     #     return '<%s>' % value
#     #
#     # def render_frequency(self, value):
#     #     print('render_frequency',self)
#     #     return '<%s>' % value
#
#
#
#

data = [
    {'name': 'Bradley'},
    {'name': 'Stevie'},
]


class NameTable(tables.Table):
    name = tables.Column()

    class Meta:
        attrs = {'class': 'paleblue'}
#
# table = NameTable(data)

