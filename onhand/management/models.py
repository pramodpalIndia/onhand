from django.db import models




class NaicsLevel1(models.Model):
    # naic_level_1_id = models.AutoField(primary_key=True, verbose_name=('id'))
    naic_level_1_code = models.CharField(primary_key=True,max_length=3, verbose_name=('code'))
    naic_level_1_desc = models.CharField(max_length=60, verbose_name=('description'))

    def __str__(self):
        return "%s (%s)" % (self.naic_level_1_desc, self.naic_level_1_code)

    class Meta:
        db_table = 'oh_naics_level_1'
        verbose_name = ("NaicsLevel1")
        verbose_name_plural = "NaicsLevel1"


class NaicsLevel2(models.Model):
    # naic_level_2_id = models.AutoField(primary_key=True, verbose_name=('id'))
    naic_level_2_code = models.CharField(primary_key=True,max_length=3, verbose_name=('code'))
    naic_level_2_desc = models.CharField(max_length=60, verbose_name=('description'))
    naic_level_1_code = models.ForeignKey(NaicsLevel1, models.DO_NOTHING, db_column='naic_level_1_code', verbose_name=('naicslevel1code'), default='72')

    def __str__(self):
        return "%s (%s)" % (self.naic_level_2_desc, self.naic_level_2_code)

    class Meta:
        db_table = 'oh_naics_level_2'
        verbose_name = ("naicslevel2")
        verbose_name_plural = "NaicsLevel2"


class NaicsLevel3(models.Model):
    # naic_level_3_id = models.AutoField(primary_key=True, verbose_name=('id'))
    naic_level_3_code = models.CharField(primary_key=True, max_length=4, verbose_name=('code'))
    naic_level_3_desc = models.CharField(max_length=60, verbose_name=('description'))
    naic_level_2_code = models.ForeignKey(NaicsLevel2, models.DO_NOTHING,  db_column='naic_level_2_code', verbose_name=('naicslevel2code'), default='722')

    def __str__(self):
        return "%s (%s)" % (self.naic_level_3_desc, self.naic_level_3_code)

    class Meta:
        db_table = 'oh_naics_level_3'
        verbose_name = ("naicslevel3")
        verbose_name_plural = "NaicsLevel3"


class NaicsLevel4(models.Model):
    # naic_level_4_id = models.AutoField(primary_key=True, verbose_name=('id'))
    naic_level_4_code = models.CharField(primary_key=True, max_length=5, verbose_name=('code'))
    naic_level_4_desc = models.CharField(max_length=60, verbose_name=('description'))
    naic_level_3_code = models.ForeignKey(NaicsLevel3, models.DO_NOTHING, db_column='naic_level_3_code', verbose_name=('naicslevel3code'), default='7225')

    def __str__(self):
        return "%s (%s)" % (self.naic_level_4_desc, self.naic_level_4_code)

    class Meta:
        db_table = 'oh_naics_level_4'
        verbose_name = ("naicslevel4")
        verbose_name_plural = "NaicsLevel4"


class NaicsLevel5(models.Model):
    # naic_level_5_id = models.IntegerField(primary_key=True, verbose_name=('id'))
    naic_level_5_code = models.CharField(primary_key=True, max_length=6, verbose_name=('code'))
    naic_level_5_desc = models.CharField(max_length=60, verbose_name=('description'))
    naic_level_4_code = models.ForeignKey(NaicsLevel4, models.DO_NOTHING, db_column='naic_level_4_code', verbose_name=('naicslevel4code'), default='72251')

    def __str__(self):
        return "%s (%s)" % (self.naic_level_5_desc, self.naic_level_5_code)

    class Meta:
        db_table = 'oh_naics_level_5'
        verbose_name = ("naicslevel5")
        verbose_name_plural = "NaicsLevel5"

# Jurisdiction classification

class Country(models.Model):
    code = models.CharField(primary_key=True, max_length=6, db_column='ctry_code', verbose_name=('code'))
    name = models.CharField(max_length=60, db_column='ctry_name', verbose_name=('name'))

    def __str__(self):
        return "%s (%s)" % (self.name, self.code)

    class Meta:
        db_table = 'oh_country'
        verbose_name = ("country")
        verbose_name_plural = "countries"


class State(models.Model):
    code = models.CharField(primary_key=True, max_length=2, db_column='stat_code', verbose_name=('code'))
    name = models.CharField(max_length=60, db_column='stat_name', verbose_name=('name'))
    country = models.ForeignKey(Country, models.DO_NOTHING, db_column='ctry_code', verbose_name=('country'))
    state_is_collect_sales_tax = models.CharField(max_length=1,default='N')
    state_sales_tax_rate = models.DecimalField(max_digits=8, decimal_places=6)



    def __str__(self):
        return "%s (%s)" % (self.name, self.code)

    class Meta:
        db_table = 'oh_state'
        verbose_name = ("state")
        verbose_name_plural = "states"


class County(models.Model):
    cont_id = models.AutoField(primary_key=True, db_column='cont_id', verbose_name=('id'))
    name = models.CharField(max_length=60, db_column='cont_name', verbose_name=('name'))
    state = models.ForeignKey(State, models.DO_NOTHING, db_column='stat_code', verbose_name=('state'))

    def __str__(self):
        return "%s (%s)" % (self.name, self.state)

    class Meta:
        db_table = 'oh_county'
        verbose_name = ("county")
        verbose_name_plural = "counties"


class Zipcode(models.Model):
    zipc_code = models.CharField(primary_key=True, max_length=5, verbose_name=('id'))
    county = models.ForeignKey(County, models.DO_NOTHING, db_column='cont_id', verbose_name=('county'))

    def __str__(self):
        return "%s (%s)" % (self.zipc_code, self.county)

    class Meta:
        db_table = 'oh_zip'
        verbose_name = ("zipcode")
        verbose_name_plural = "Zipcodes"


class City(models.Model):
    city_id = models.AutoField(primary_key=True, verbose_name=('id'))
    zipc_code = models.ForeignKey(Zipcode, models.DO_NOTHING, db_column='zipc_code', verbose_name=('zipcode'),default='16595')
    name = models.CharField(max_length=60, db_column='city_name', verbose_name=('name'))
    city_is_user_added = models.CharField(max_length=1, verbose_name=('city_user_added'),default='n')

    def __str__(self):
        return "%s (%s)" % (self.name, self.zipc_code)

    class Meta:
        db_table = 'oh_city'
        verbose_name = ("city")
        verbose_name_plural = "city"


class Basis(models.Model):
    basi_code = models.CharField(primary_key=True, max_length=6, verbose_name=('code'))
    basi_alert_days = models.IntegerField(verbose_name=('alertdays'))
    basi_repeat_alert_days = models.IntegerField(verbose_name=('repeatalertdays'))
    basi_desc = models.CharField(max_length=60, verbose_name=('description'))

    def __str__(self):
        # return "%s (%s)" % (self.basi_code, self.basi_desc)
        return "%s" % (self.basi_desc)

    class Meta:
        db_table = 'oh_basis'
        verbose_name = ("basis")
        verbose_name_plural = "basis"


class Address(models.Model):
    addr_id = models.AutoField(primary_key=True, verbose_name=('id'))
    city = models.ForeignKey(City, models.DO_NOTHING, db_column='city_id',verbose_name=('city'))
    address_line_1 = models.CharField(max_length=40, db_column='addr_line1', verbose_name=('addressline1'))
    address_line_2 = models.CharField(max_length=40, blank=True, null=True,db_column='addr_line2', verbose_name=('addressline2'))

    def __str__(self):
        return "%s " % self.addr_id

    class Meta:
        db_table = 'oh_address'
        verbose_name = ("address")
        verbose_name_plural = "address"

class Language(models.Model):
    lang_code = models.CharField(primary_key=True, max_length=6, verbose_name=('code'))
    lang_desc = models.CharField(max_length=60, verbose_name=('description'))

    def __str__(self):
        return "%s " % (self.lang_desc)

    class Meta:
        db_table = 'oh_language'
        verbose_name = ("language")
        verbose_name_plural = "languages"

class Role(models.Model):
    role_code = models.CharField(primary_key=True, max_length=6,db_column='role_code', verbose_name=('code'))
    role_desc = models.CharField(max_length=60,db_column='role_desc', verbose_name=('description'))

    def __str__(self):
        return "%s " % (self.role_desc)

    class Meta:
        db_table = 'oh_role'
        verbose_name = ("role")
        verbose_name_plural = "roles"

class Salessource(models.Model):
    ssrc_id = models.AutoField(primary_key=True)
    ssrc_desc = models.CharField(max_length=60, verbose_name=('description'))
    ssrc_url = models.CharField(max_length=2000, blank=True, null=True, verbose_name=('url'))

    def __str__(self):
        return "%s" % (self.ssrc_desc)

    class Meta:
        db_table = 'oh_sales_source'
        verbose_name = ("salessource")
        verbose_name_plural = "salessources"



class GovernmentLevel(models.Model):
    govl_code = models.CharField(primary_key=True, max_length=1, verbose_name=('code'))
    govl_desc = models.CharField(max_length=60, verbose_name=('description'))

    def __str__(self):
        return "%s" % (self.govl_desc)
        # return "%s (%s)" % (self.govl_desc, self.govl_code)

    class Meta:
        db_table = 'oh_government_level'
        verbose_name = ("govermentlevel")
        verbose_name_plural = "govermentlevel"


# class Jurisdiction(models.Model):
#     jurs_id = models.AutoField(primary_key=True)
#     city = models.ForeignKey(City, models.DO_NOTHING, verbose_name=('city'))
#     govl_code = models.ForeignKey(GovernmentLevel, models.DO_NOTHING, db_column='govl_code', verbose_name=('govermentlevel'))
#
#
#     def __str__(self):
#         return "%s (%s)" % (self.city, self.govl_code)
#
#     class Meta:
#         db_table = 'oh_jurisdiction'
#         verbose_name = ("jurisdiction")
#         verbose_name_plural = "jurisdiction"


class Financing(models.Model):
    fina_id = models.AutoField(primary_key=True)
    basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code', verbose_name=('basis'))
    fina_start_date = models.DateField(verbose_name=('startdate'))
    fina_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name=('amount'))
    fina_downpay_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True, verbose_name=('downpayment'))
    fina_period_pay_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True, verbose_name=('paymentperiod'))
    fina_rate = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True, verbose_name=('rate'))
    fina_fee = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True, verbose_name=('fee'))
    fina_pay_start_date = models.DateField(blank=True, null=True, verbose_name=('paymentstartdate'))
    fina_last_pay_date = models.DateField(blank=True, null=True, verbose_name=('lastpaymentdate'))

    def __str__(self):
        return "%s " % (self.fina_id)

    class Meta:
        db_table = 'oh_financing'
        verbose_name = ("financing")
        verbose_name_plural = "financing"


class Agency(models.Model):
    agen_code = models.CharField(primary_key=True, max_length=6, verbose_name=('code'))
    agen_name = models.CharField(max_length=60, blank=True, null=True, verbose_name=('name'))
    agen_website = models.CharField(max_length=60, blank=True, null=True, verbose_name=('website'))

    def __str__(self):
        return "%s" % (self.agen_name)
        # return "%s (%s)" % (self.agen_name, self.agen_code)

    class Meta:
        db_table = 'oh_agency'
        verbose_name = ("agency")
        verbose_name_plural = "agency"

class AttachmentType(models.Model):
    atyp_code = models.CharField(primary_key=True, max_length=6, verbose_name=('code'))
    atyp_desc = models.CharField(max_length=60, verbose_name=('description'))

    def __str__(self):
        return "%s (%s)" % (self.atyp_desc, self.atyp_code)

    class Meta:
        db_table = 'oh_attachment_type'
        verbose_name = ("attachmenttype")
        verbose_name_plural = "attachmenttypes"


class Permission(models.Model):
    perm_code = models.CharField(primary_key=True, max_length=6, verbose_name=('Code'))
    perm_desc = models.CharField(max_length=60, verbose_name=('Description'))

    def __str__(self):
        return "%s" % (self.perm_desc)

    class Meta:
        db_table = 'oh_permission'
        verbose_name = ("Permission")
        verbose_name_plural = "Permissions"



class UserPreferenceType(models.Model):
    uprt_code = models.CharField(primary_key=True, max_length=6, verbose_name='Code')
    uprt_desc = models.CharField(max_length=60, verbose_name='Description')
    uprt_default_value = models.CharField(max_length=40, blank=True, null=True, verbose_name='Default value')
    uprt_usage = models.TextField(blank=True, null=True, verbose_name='Usage')

    def __str__(self):
        return "%s" % (self.uprt_desc)

    class Meta:
        db_table = 'oh_user_preference_types'
        verbose_name = "UserPreferenceType"
        verbose_name_plural = "UserPreferenceTypes"





class v_SubscribedServicesTable(models.Model):
    csrv_id = models.AutoField(primary_key=True)
    Service = models.CharField(max_length=10, verbose_name=('Service'), default='Service')
    ctyp_desc = models.CharField(max_length=60, verbose_name=('description'))
    basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code', verbose_name=('basis'))
    csrv_due_date = models.DateField(verbose_name=('duedate'))
    csac_date = models.DateTimeField(verbose_name=('date'))
    csac_price = models.DecimalField(max_digits=18, decimal_places=2, blank=True, verbose_name=('price'), default=0)
    average_price = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True, verbose_name=('average_price'))
    off_from_avg = models.DecimalField(max_digits=19, decimal_places=8, blank=True, null=True,
                                        verbose_name=('off_from_avg'))
    agen_code = models.ForeignKey(Agency, models.DO_NOTHING, db_column='agen_code', verbose_name=('agency'))
    govl_code = models.ForeignKey(GovernmentLevel, models.DO_NOTHING, db_column='govl_code', default='C',
                                  verbose_name=('govermentlevl'))

    class Meta:
        managed = False
        db_table = 'v_SubscribedServicesTable'
        verbose_name = ("v_SubscribedServicesTable")
        verbose_name_plural = "v_SubscribedServicesTable"


class v_dashboard_service(models.Model):
    from onhand.subscription.models import Subscription, CompanyPersonRole
    from onhand.compliance.models import ComplianceServiceAction,ComplianceServiceSchedule,ServiceJurisdiction, ComplianceServiceType
    subscriber = models.ForeignKey(Subscription, models.DO_NOTHING, verbose_name=('subscriber'))
    csrv_id = models.AutoField(primary_key=True)
    Service = models.CharField(max_length=10, verbose_name=('Service'), default='Service')
    srvj = models.ForeignKey(ServiceJurisdiction, models.DO_NOTHING, db_column='srvj_id',verbose_name='Jurisdiction')
    ctyp = models.ForeignKey(ComplianceServiceType, models.DO_NOTHING, db_column='ctyp_id',verbose_name=('Service (Agency/Basis)'))
    ctyp_desc = models.CharField(max_length=60, verbose_name=('description'))
    basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code', verbose_name=('basis'))
    csrv_due_date = models.DateField(verbose_name=('duedate'))
    csac = models.ForeignKey(ComplianceServiceAction, models.DO_NOTHING, db_column='csac_id',
                             verbose_name='complianceserviceaction')
    csac_service_date = models.DateField(verbose_name=('servicedate'))
    csac_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name=('price'))
    cssc_id = models.ForeignKey(ComplianceServiceSchedule, models.DO_NOTHING, db_column='cssc_id', verbose_name='ComplianceServiceSchedule')
    cssc_service_date = models.DateField(blank=True, null=True, db_column='cssc_service_date',verbose_name='servicedate')
    average_price = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True, verbose_name=('average_price'))
    csac_price_last = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True,
                                       verbose_name=('lastprice'))
    csac_service_date_last = models.DateField(verbose_name=('lastservicedate'))
    off_from_avg = models.DecimalField(max_digits=19, decimal_places=8, blank=True, null=True,
                                        verbose_name=('off_from_avg'))
    basi_alert_days = models.IntegerField(verbose_name='Alertdays')
    due_status = models.CharField(max_length=10, verbose_name='DueStatus')
    agen_code = models.ForeignKey(Agency, models.DO_NOTHING, db_column='agen_code', verbose_name=('agency'))
    govl_code = models.ForeignKey(GovernmentLevel, models.DO_NOTHING, db_column='govl_code', default='C',
                                  verbose_name=('govermentlevl'))
    cres_id = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cres_id')
    cprs_id_responsible = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cprs_id_responsible',
                                            related_name='cprs_id_responsible_dashboard', verbose_name='Responsible')
    prsn_fname = models.CharField(max_length=20,db_column='prsn_fname',verbose_name=('first name'))
    prsn_lname = models.CharField(max_length=20,db_column='prsn_lname', verbose_name=('last name' ))


    class Meta:
        managed = False
        db_table = 'v_dashboard_service'
        verbose_name = ("v_dashboard_service")
        verbose_name_plural = "v_dashboard_service"


class v_company_people(models.Model):
    from onhand.subscription.models import Subscription, CompanyPersonRole, Company

    comp = models.ForeignKey(Company, models.DO_NOTHING, db_column='comp_id', verbose_name='company')
    comp_name = models.CharField(max_length=30, db_column='comp_name', verbose_name=('name'))
    comp_phone = models.CharField(max_length=20, blank=True, null=True, db_column='comp_phone', verbose_name=('phone'))
    comp_email = models.CharField(max_length=40, blank=True, null=True, db_column='comp_email', verbose_name=('email'))
    comp_website = models.CharField(max_length=60, blank=True, null=True,db_column='comp_website', verbose_name=('website'))
    cprs_id = models.IntegerField(primary_key=True, db_column='cprs_id', verbose_name='companyperson')
    cprs_id_manager = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING, db_column='cprs_id_manager', blank=True, null=True,
                                        verbose_name='Personmanager')
    prsn_name = models.CharField(max_length=41, db_column='prsn_name', verbose_name='Name')
    prsn_fname = models.CharField(max_length=20, db_column='prsn_fname', verbose_name='First name')
    prsn_lname = models.CharField(max_length=20, db_column='prsn_lname', verbose_name='Last name')
    mobile_phone = models.CharField(max_length=20, blank=True, null=True, db_column='prsn_mobile_phone', verbose_name='mobile phone')
    office_phone = models.CharField(max_length=20, blank=True, null=True, db_column='prsn_office_phone', verbose_name='office phone')
    email = models.CharField(max_length=60, blank=True, null=True, db_column='prsn_email', verbose_name='email')
    address = models.ForeignKey(Address, models.DO_NOTHING, blank=True, null=True, db_column='addr_id', verbose_name='address')

    class Meta:
        managed = False
        db_table = 'v_company_people'
        verbose_name = "v_company_people"
        verbose_name_plural = "v_company_people"


# Get compliance services for the dashboard
'''
 # Get compliance services for the dashboard
create or replace view v_dashboard_service
as
select	cs.csrv_id		AS csrv_id,
	cs.subs_id		AS subscriber_id,
	'Service'		AS Service,
	cs.srvj_id		AS srvj_id,
	cst.ctyp_id		AS ctyp_id,
	cst.ctyp_desc		AS ctyp_desc,
	cs.basi_code		AS basi_code,
	cs.csrv_due_date	AS csrv_due_date,
	csa.csac_service_date	AS csac_service_date,
	csa.csac_price		AS csac_price,
	css.cssc_id		AS cssc_id,
	css.cssc_service_date	AS cssc_service_date,
	vas.average_price	AS average_price,
	vla.csac_price_last	AS csac_price_last,
	vla.csac_service_date_last AS csac_service_date_last,
	case
		when vas.average_price is null then null
		when csa.csac_price is not null then (csa.csac_price - vas.average_price) / csa.csac_price
		when vla.csac_price_last is not null then (vla.csac_price_last - vas.average_price) / vla.csac_price_last
		else null
	end			AS off_from_avg,
	b.basi_alert_days	AS basi_alert_days,
	case
		when csa.csac_service_date is not null then 'completed'
		when datediff(cs.csrv_due_date, curdate() ) < 0 then 'past due'
		when cs.csrv_due_date - b.basi_alert_days < curdate() then 'coming due'
		else 'current'
	end			AS due_status,
	cst.agen_code		AS agen_code,
	sj.govl_code		AS govl_code,
	cr.cres_id		AS cres_id,
	cr.cprs_id_responsible	AS cprs_id_responsible,
	cr.prsn_fname		AS prsn_fname,
	cr.prsn_lname		AS prsn_lname
from	oh_compliance_service cs
join	oh_basis b
	on cs.basi_code = b.basi_code
left join v_last_compliance_service_action vla
	on cs.srvj_id = vla.srvj_id
        and cs.subs_id = vla.subs_id
left	join v_average_service_price vas
	on cs.srvj_id = vas.srvj_id
left join oh_compliance_service_action csa
	on csa.csrv_id = cs.csrv_id
left join oh_service_jurisdiction sj
	on sj.srvj_id = cs.srvj_id
left join oh_compliance_service_type cst
	on cst.ctyp_id = sj.ctyp_id
left join oh_compliance_service_schedule css
	on css.csrv_id = cs.csrv_id
	and css.schs_code='PEND'
left join v_compliance_responsible cr
	on cr.csrv_id = cs.csrv_id;

'''
