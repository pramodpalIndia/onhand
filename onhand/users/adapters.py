# -*- coding: utf-8 -*-
from django.conf import settings

from onhand.provider import app_settings
from onhand.provider.adapter import DefaultAccountAdapter


from onhand.management.models import Role, Zipcode, City, NaicsLevel5
from onhand.provider.models import Person, Company, Subscription, CompanyLanguage, PersonLanguage, CompanyPersonRole
from onhand.provider.utils import url_str_to_person_pk, person_field, url_str_to_company_pk, company_field, \
    address_field, subscription_field, company_language_field, person_language_field, company_person_role_field
from onhand.users.utils import user_username, user_field
from onhand.provider.adapter import get_adapter

class AccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        # from .utils import user_username, user_email, user_field
        adapter = get_adapter(request)
        data = form.cleaned_data

        person_pk = None
        company_pk = None
        person = None
        company = None

        # Update Company Model
        company_pk_str = request.session.get('account_company', None)
        if company_pk_str:
            company_pk = url_str_to_company_pk(company_pk_str)
            company = Company.objects.get(comp_id=company_pk_str)
            if company:
                company_field(company, 'comp_name', data.get('compname'))
                company_field(company, 'comp_email', data.get('compemail'))
                company_field(company, 'comp_website', data.get('website'))
                company_field(company, 'comp_phone', data.get('phone'))
                company_field(company, 'comp_phone', data.get('phone'))
                company_field(company, 'fax', data.get('fax'))

                # Update Address for the company
                address = company.address_id
                Form_Data_addressline1 = data.get('addressline1')
                Form_Data_addressline2 = data.get('addressline2')
                Form_Data_zipcode = data.get('zipcode')
                Form_Data_cityopt = data.get('cityopt')
                Form_Data_city = data.get('city')
                city = None
                if (Zipcode.objects.filter(zipc_code=Form_Data_zipcode).exists()):
                    if (City.objects.filter(
                        zipc_code=Form_Data_zipcode).exists() and Form_Data_cityopt != 'None' and Form_Data_city):
                        if (City.objects.filter(name=Form_Data_city, zipc_code=Form_Data_zipcode).exists()):
                            city = City.objects.get(name=Form_Data_city, zipc_code=Form_Data_zipcode).city_id.__str__()
                        else:
                            city = City.objects.create(zipc_code=Zipcode.objects.get(zipc_code=Form_Data_zipcode),
                                                       name=Form_Data_city, city_is_user_added='y')
                        city_id_str = city.__str__()
                    else:
                        city_id_str = Form_Data_cityopt.city_id.__str__()
                        city = City.objects.get(city_id=city_id_str).city_id.__str__()

                if Form_Data_addressline1:
                    address_field(address, 'address_line_1', Form_Data_addressline1)
                if Form_Data_addressline2:
                    address_field(address, 'address_line_2', Form_Data_addressline2)
                if city:
                    address_field(address, 'city_id', city_id_str)

                self.populate_address(request, address)
                print('Saving Changed address for Company',address)
                address.save()

                #TODO : traverse the array list if language is more then one
                companylanguagechecklist = data.get('languagechecklist')
                if(CompanyLanguage.objects.filter(pk=company,lang_code=companylanguagechecklist).exists()):
                    companylanguage = CompanyLanguage.objects.get(pk=company,lang_code=companylanguagechecklist)
                    company_language_field(companylanguage, 'lang_code', companylanguagechecklist)
                    companylanguage.update()
                else:
                    companylanguage = adapter.new_company_language(request)
                    company_language_field(companylanguage, 'lang_code', companylanguagechecklist)
                    companylanguage.save()

            self.populate_company(request, company)
            if commit:
                company.save()

        ohsubscription_pk_str = request.session.get('ohaccount_subscription', None)
        if ohsubscription_pk_str:
            # company_pk = url_str_to_company_pk(company_pk_str)
            ohsubscription = Subscription.objects.get(pk=ohsubscription_pk_str)
            if ohsubscription:
                naicsLevel5 = NaicsLevel5.objects.get(pk= data.get('naicslevel5opt'))
                subscription_field(ohsubscription, 'naicslevel5', naicsLevel5)


        person_pk_str = request.session.get('account_person', None)
        if person_pk_str:
            person = Person.objects.get(pk=person_pk_str)
            if person:
                personlanguagechecklist = data.get('personlanguagechecklist')
                if(PersonLanguage.objects.filter(pk=person,lang_code=personlanguagechecklist).exists()):
                    personlanguage = PersonLanguage.objects.get(pk=person,lang_code=personlanguagechecklist)
                    person_language_field(personlanguage, 'lang_code',personlanguagechecklist )
                    personlanguage.update()
                else:
                    personlanguage = adapter.new_person_language(request)
                    person_language_field(personlanguage, 'lang_code', personlanguagechecklist)
                    if commit:
                        personlanguage.save()

        person_role_company_str = request.session.get('company_person_role', None)
        if person_role_company_str:
            companypersonrole = CompanyPersonRole.objects.get(pk=person_role_company_str)
            if companypersonrole:
                personrole =  data.get('personroles')
                company_person_role_field(companypersonrole, 'crol_code', personrole)
                if commit:
                    companypersonrole.save()


        username = data.get('username')
        if username:
            user_username(user, username)

        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()

        if(form == 'onhand.provider.forms.SignupForm'):
            user_field(user, 'role_code', Role.objects.get(pk='custom'))

        self.populate_username(request, user)

        if commit:
            user.save()
        return user


    def populate_username(self, request, user):
        """
        Fills in a valid username, if required and missing.  If the
        username is already present it is assumed to be valid
        (unique).
        """
        from .utils import user_username,user_field

        username = user_username(user)
        if app_settings.USER_MODEL_USERNAME_FIELD:
            user_username( user, username )
