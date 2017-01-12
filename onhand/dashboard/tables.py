import django_filters
import django_tables2 as tables
import itertools

from datetime import date
from django.db.models import F
from django_tables2 import A
from django_tables2 import TemplateColumn

from onhand.compliance.models import ServiceJurisdiction, ComplianceServiceType

import datetime
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm, Form


from onhand.dashboard.models import Alert
import django_tables2 as tables



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
from onhand.management.models import  GovernmentLevel, v_SubscribedServicesTable

view_template = """
<a href="#" class="dismiss" title="Clear Alert">
    <i class="fa fa-eye fa-2x text-danger" style="color: #72a525"></i>
</a>
"""

delete_template = """
<a href="#" class="dismiss" title="Clear Alert">
    <i class="fa fa-trash-o fa-2x" style="color: red"></i>
</a>
"""

# <select id='basi_code'>
# <option {% if record.basi_code = 'ANNUAL' %} selected {% endif %}>Annual
# <option {% if record.basi_code = 'BIEN' %} selected {% endif %}>Bi-Annual
# <option {% if record.basi_code = 'DAILY' %} selected {% endif %}>Daily
# <option {% if record.basi_code = 'MNTHLY' %} selected {% endif %}>Monthly
# <option {% if record.basi_code = 'ONCE' %} selected {% endif %}>One Time Only
# <option {% if record.basi_code = 'QTLY' %} selected {% endif %}>Quartely
# <option {% if record.basi_code = 'SEMIAN' %} selected {% endif %}>Semi-Annual
# <option {% if record.basi_code = 'WEEKLY' %} selected {% endif %}>Weekly
#  </select>

basi_template = """
{% if record.csac_service_date == None  %}
     <select style="width:auto" id="compliancedropdown{{ record.csrv_id }}" name="compliancedropdown{{ record.csrv_id }}"
              onchange="servicebasischange('compliancedropdown{{ record.csrv_id }}',this)">
              <option value="ANNUAL" {% if record.basi_code|stringformat:"s"  == 'ANNUAL' %} selected {% endif %}>Annual</option>
              <option value="BIEN" {% if record.basi_code|stringformat:"s"  == 'BIEN' %} selected {% endif %}>Bi-Annual</option>
              <option value="DAILY" {% if record.basi_code|stringformat:"s"  == 'DAILY' %} selected {% endif %}>Daily</option>
              <option value="MNTHLY" {% if record.basi_code|stringformat:"s" == "MNTHLY" %} selected {% endif %}>Monthly</option>
              <option value="ONCE" {% if record.basi_code|stringformat:"s"  == 'ONCE' %} selected {% endif %}>One Time Only</option>
              <option value="SEMIAN" {% if record.basi_code|stringformat:"s"  == 'SEMIAN' %} selected {% endif %}>Semi-Annual</option>
              <option value="WEEKLY" {% if record.basi_code|stringformat:"s"  == 'WEEKLY' %} selected {% endif %}>Weekly</option>
     </select>
{% endif %}
{% if record.csac_service_date != None  %}
        {% if record.basi_code|stringformat:"s"  == 'ANNUAL' %} Annual {% endif %}
        {% if record.basi_code|stringformat:"s"  == 'BIEN' %} Bi-Annual {% endif %}
        {% if record.basi_code|stringformat:"s"  == 'DAILY' %} Daily {% endif %}
        {% if record.basi_code|stringformat:"s"  == 'MNTHLY' %} Monthly {% endif %}
        {% if record.basi_code|stringformat:"s"  == 'ONCE' %} One Time Only {% endif %}
        {% if record.basi_code|stringformat:"s"  == 'SEMIAN' %} Semi-Annual {% endif %}
        {% if record.basi_code|stringformat:"s"  == 'WEEKLY' %} Weekly {% endif %}
{% endif %}
"""



due_date_template = """
{% if record.csac_service_date == None  %}
<a href="#" class="dismiss" title="Clear Alert" name="complianceinputduedate{{ record.csrv_id }}"
   id="complianceinputduedate{{ record.csrv_id }}"
   onclick="servicerenewaldateclick('compliancedropdown{{ record.csrv_id }}',this)">
<input style="width:60%;text-align: center;" name="compliancerenewaldate{{ record.csrv_id }}" id="compliancerenewaldate{{  record.csrv_id }}"
maxlength="9" value="{{ record.csrv_due_date|date:"m/d/y" }}" type="text" onclick="servicerenewaldateclick('compliancedropdown{{ record.csrv_id }}',this)"/>
 <i class="fa fa-calendar " style="color: black" onclick="servicerenewaldateclick('compliancedropdown{{ record.csrv_id }}',this)"></i>
 </a>
 {% endif %}
 {% if record.csac_service_date != None  %}
        {{ record.csrv_due_date|date:"m/d/y" }}
{% endif %}
"""

action_date_template = """
{% if record.csac_service_date == None  %}
<a href="#" class="dismiss" title="Clear Alert" }}"
   onclick="serviceactiondateclick('compliancedropdown{{ record.csrv_id }}',this)">
 <i class="fa fa-calendar-plus-o fa-2x" style="color: black;text-align: center;;" onclick="serviceactiondateclick('compliancedropdown{{ record.csrv_id }}',this)"></i>
 </a>
 {% endif %}
 {% if record.csac_service_date != None  %}
        {{ record.csac_service_date|date:"m/d/y" }}
{% endif %}
"""

# action_date_template = """
# {% if record.csac_service_date == None  %}
# <a href="#" class="dismiss" title="Clear Alert" name="complianceinputactiondate{{ record.csrv_id }}"
#    id="complianceinputactiondate{{ record.csrv_id }}"
#    onclick="serviceactiondateclick('compliancedropdown{{ record.csrv_id }}',this)">
# <input style="width:auto" name="complianceactiondate{{ record.csrv_id }}" id="complianceactiondate{{  record.csrv_id }}"
# maxlength="9" value="{{ record.csac_service_date|date:"m/d/y" }}" type="text" onclick="serviceactiondateclick('compliancedropdown{{ record.csrv_id }}',this)"/>
#  <i class="fa fa-calendar-plus-o fa-2x" style="color: black" onclick="serviceactiondateclick('compliancedropdown{{ record.csrv_id }}',this)"></i>
#  </a>
#  {% endif %}
#  {% if record.csac_service_date != None  %}
#         {{ record.csac_service_date|date:"m/d/y" }}
# {% endif %}
# """

amountpaid_template = """
{% if record.csac_service_date == None  %}
    {% if record.csac_price_last  %}
        <i class="fa fa-usd " style="color: #000000"></i>{{ record.csac_price_last }}
    {% endif %}
{% endif %}
 {% if record.csac_service_date != None  %}
        {% if record.csac_price_last  %}
        <i class="fa fa-usd " style="color: #000000"></i>{{ record.csac_price }}
    {% endif %}
{% endif %}
"""

lastaction_date_template = """
 {% if record.csac_service_date_last != None  %}
        {{ record.csac_service_date_last|date:"m/d/y" }}
 {% endif %}
"""

value_template = """
{% if record.csac_service_date  == None %}
<a href="#" class="dismiss" title="Clear Alert">
{% if record.csac_price_last  <= 0  %} <i class="fa fa-thumbs-o-up fa-2x" style="color: #72a525"></i> {% endif %}
{% if record.csac_price_last  > 0  %} <i class="fa fa-thumbs-o-down fa-2x" style="color: red"></i> {% endif %}
</a>
{% endif %}
"""

class SubscribedServicesTable(tables.Table):

    alert_action = tables.TemplateColumn(view_template, orderable=False,verbose_name="")
    delete_action = tables.TemplateColumn(delete_template, orderable=False, verbose_name=" ")
    # subscriber = tables.Column(accessor='subscriber', verbose_name=('Subscription'))
    Service = tables.Column(accessor='Service', verbose_name=('Type'))
    ctyp_desc = tables.Column(accessor='ctyp_desc', orderable=False, verbose_name=('Description'))
    # basi_code = tables.Column(accessor='basi_code', orderable=False, verbose_name = ('Frequency'))
    basi_code = tables.TemplateColumn(basi_template, orderable=False,verbose_name="Frequency")
    # csrv_due_date = tables.DateColumn(format='m/d/Y' , accessor='csrv_due_date', orderable=False, verbose_name=('Due / Renewal date'))
    csrv_due_date = tables.TemplateColumn(due_date_template, orderable=False, verbose_name=('Due / Renewal date'))
    # csac_date = tables.DateColumn(format='m/d/Y', accessor='csac_date', orderable=False, verbose_name=('Action date'))
    csac_date = tables.TemplateColumn(action_date_template, orderable=False, verbose_name=('Action date'))
    # csac_price = tables.Column(accessor='csac_price', orderable=False, verbose_name=('Amount Paid'))
    csac_price = tables.TemplateColumn(amountpaid_template, orderable=False, verbose_name="(Last) Paid ")
    # csac_service_date_last = tables.TemplateColumn(lastaction_date_template, orderable=False, verbose_name=('Last Actioned'))
    # average_price = tables.Column(accessor='average_price', orderable=False, verbose_name=('Avg Price'))
    # off_from_avg = tables.Column(accessor='off_from_avg', orderable=False, verbose_name=('Off Price'))
    off_from_avg = tables.TemplateColumn(value_template, orderable=False, verbose_name="Value")
    # basi_alert_days = tables.Column(accessor='basi_alert_days', verbose_name=('Alert Days'))
    # due_status = tables.Column(accessor='due_status', verbose_name=('DueStatus'))
    agen_code = tables.Column(accessor='agen_code', orderable=False, verbose_name=('Agency'))
    govl_code = tables.Column(accessor='govl_code', orderable=False, verbose_name=('Jurisdiction'))


    class Meta:
        attrs = {'class': 'paleblue' , 'id' :'SubscribedServicesTable'}
        # , 'style': 'height: 60vh;'
        # attrs = {"td": {"colspan": "4"}}
        alert_action = tables.Column(orderable=False)
        csrv_due_date = tables.DateColumn(format='m/d/Y')
        ctyp_desc = tables.Column(attrs={"Style": {"background": "rgba(255, 153, 0, 0.23);"}})
        # model = v_SubscribedServicesTable
        # actions = tables.Column(orderable=False)
        row_attrs = {
            'data-alert-pk': lambda record: record.csrv_id
        }
        empty_text = "There are no active alerts to display in this view."



    # def render_Service(self, record, column):
    #     print('Been called render_Service, checked record.due_status', record.due_status, column.attrs)
    #     if (record.due_status == 'coming due'):
    #         column.attrs = {'td': {'Style': "background: rgba(207, 42, 39, 0.23)"}}
    #     # else:
    #     #     column.attrs = {'td': {}}
    #
    #     if (record.due_status == 'past due'):
    #         column.attrs = {'td': {'Style': "background: rgba(255, 153, 0, 0.23)"}}
    #
    #     if (record.due_status == 'current'):
    #         column.attrs = {'td': {'Style': "background: rgba(0, 158, 15, 0.23)"}}
    #
    #     return record.Service


    def render_ctyp_desc(self, record, column):
        # print('Been called render_Service, checked record.due_status', record.due_status, column.attrs)
        if (record.due_status == 'coming due'):
            column.attrs = {'td': {'Style': "background-color: #ff9900;color: #ffffff"}}
        if(record.due_status == 'past due'):
            column.attrs = {'td':  {'Style': "background-color: #cf2a27;color: #ffffff"}}
        if (record.due_status == 'current'):
            column.attrs = {'td': {'Style': "background-color: #009e0f;color: #ffffff"}}
        if (record.due_status == 'completed'):
            column.attrs = {'td': {}}
        return record.ctyp_desc

    # def render_basi_code(self, record, column):
    #     if (record.due_status == 'coming due'):
    #         column.attrs = {'td': {'Style': "background: rgba(207, 42, 39, 0.23)"}}
    #     if(record.due_status == 'past due'):
    #         column.attrs = {'td':  {'Style': "background: rgba(255, 153, 0, 0.23)"}}
    #     if (record.due_status == 'current'):
    #         column.attrs = {'td': {'Style': "background: rgba(0, 158, 15, 0.23)"}}
    #     return self
    #
    # def render_csrv_due_date(self, record, column):
    #     if (record.due_status == 'coming due'):
    #         column.attrs = {'td': {'Style': "background: rgba(207, 42, 39, 0.23)"}}
    #     if(record.due_status == 'past due'):
    #         column.attrs = {'td':  {'Style': "background: rgba(255, 153, 0, 0.23)"}}
    #     if (record.due_status == 'current'):
    #         column.attrs = {'td': {'Style': "background: rgba(0, 158, 15, 0.23)"}}
    #     return record.csrv_due_date
    #
    # # def render_csac_date(self, record, column):
    # #     if (record.due_status == 'coming due'):
    # #         column.attrs = {'td': {'Style': "background: rgba(207, 42, 39, 0.23)"}}
    # #     if(record.due_status == 'past due'):
    # #         column.attrs = {'td':  {'Style': "background: rgba(255, 153, 0, 0.23)"}}
    # #     if (record.due_status == 'current'):
    # #         column.attrs = {'td': {'Style': "background: rgba(0, 158, 15, 0.23)"}}
    # #     return record.csac_date
    #
    # def render_csac_price(self, record, column):
    #     if (record.due_status == 'coming due'):
    #         column.attrs = {'td': {'Style': "background: rgba(207, 42, 39, 0.23)"}}
    #     if(record.due_status == 'past due'):
    #         column.attrs = {'td':  {'Style': "background: rgba(255, 153, 0, 0.23)"}}
    #     if (record.due_status == 'current'):
    #         column.attrs = {'td': {'Style': "background: rgba(0, 158, 15, 0.23)"}}
    #     return record.csac_price
    #
    # def render_off_from_avg(self, record, column):
    #     if (record.due_status == 'coming due'):
    #         column.attrs = {'td': {'Style': "background: rgba(207, 42, 39, 0.23)"}}
    #     if(record.due_status == 'past due'):
    #         column.attrs = {'td':  {'Style': "background: rgba(255, 153, 0, 0.23)"}}
    #     if (record.due_status == 'current'):
    #         column.attrs = {'td': {'Style': "background: rgba(0, 158, 15, 0.23)"}}
    #     return record.off_from_avg
    #
    # def render_agen_code(self, record, column):
    #     if (record.due_status == 'coming due'):
    #         column.attrs = {'td': {'Style': "background: rgba(207, 42, 39, 0.23)"}}
    #     if(record.due_status == 'past due'):
    #         column.attrs = {'td':  {'Style': "background: rgba(255, 153, 0, 0.23)"}}
    #     if (record.due_status == 'current'):
    #         column.attrs = {'td': {'Style': "background: rgba(0, 158, 15, 0.23)"}}
    #     return record.agen_code
    #
    # def render_govl_code(self, record, column):
    #     if (record.due_status == 'coming due'):
    #         column.attrs = {'td': {'Style': "background: rgba(207, 42, 39, 0.23)"}}
    #     if(record.due_status == 'past due'):
    #         column.attrs = {'td':  {'Style': "background: rgba(255, 153, 0, 0.23)"}}
    #     if (record.due_status == 'current'):
    #         column.attrs = {'td': {'Style': "background: rgba(0, 158, 15, 0.23)"}}
    #     return record.agen_code



class MyFilter(django_filters.FilterSet):
  field1 = django_filters.CharFilter()
  field2 = django_filters.CharFilter()

class CheckBoxService(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name


class BooleanService(tables.BooleanColumn):
    @property
    def header(self):
        return self.verbose_name


class DueRenewalDate(tables.DateColumn):
    @property
    def header(self):
        return self.verbose_name


class ServicesTable(tables.Table):

    # select = BooleanService(verbose_name="Action", accessor="pk")
    # action = tables.URLColumn()
    action = tables.LinkColumn('users:detail', attrs={
        'a': {'style': 'background: url(../static/images/menu/ohdashboard/view.png);background-repeat: no-repeat;font-size: 25px;color: transparent;background-position: center;'}}, args=[A('pk')],text='.   .' )

    servicetype = tables.Column(accessor='ctyp_id', verbose_name="Type")
    compliance = tables.Column(accessor='ctyp_id',verbose_name="Compliance")
    # frequency = tables.Column(accessor='ctyp_id', verbose_name="Frequency")
    frequency = TemplateColumn('<select> <option value="ANNUAL">Annual</option>'
                                   '<option value="BIAN">Bi-Annual</option><option value="QUARTE">Quartely</option>'
                                   '<option value="MNTHLY">Monthly</option><option value="Weekly">Annual</option></select>', verbose_name="Frequency")

    # renewaldate = tables.Column(accessor='ctyp_id', verbose_name="Due/Renewal date")
    # date_field = forms.DateField(widget=SelectDateWidget)
    # renewaldate = tables.DateColumn(format="YYYY-MM-DD",verbose_name="Due/Renewal date")
    renewaldate = tables.Column( verbose_name="Due/Renewal date")
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




action_template = """
<a href="#" class="dismiss" title="Clear Alert">
    <i class="fa fa-eye fa-2x text-danger"></i>
</a>
"""

delete_template = """
<a href="#" class="dismiss" title="Clear Alert">
    <i class="fa fa-trash-o fa-2x"></i>
</a>
"""

class AlertsTable(tables.Table):
    alert_action = tables.TemplateColumn(action_template)
    delete_action = tables.TemplateColumn(delete_template)

    class Meta:
        model = Alert
        row_attrs = {
            'data-alert-pk': lambda record: record.id
        }
        empty_text = "There are no active alerts to display in this view."
