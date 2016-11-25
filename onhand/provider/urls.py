from django.conf.urls import url

from onhand.provider.views import validate_discount_code,validate_zipcode, validateselectedonhandplan, account_inactive, \
    get_naiclevel
from . import views

urlpatterns = [
    url(r"^accounts/signup/$", views.signup, name="account_signup"),
    url(r'^validate_discount_code/$', validate_discount_code, name="validate_discount_code"),
    url(r'^ajax_getcityfromzip/$', validate_zipcode, name="getcityfromzip"),
    url(r'^ajax_getselectedonhandplan/$', validateselectedonhandplan, name="validateselectedonhandplan"),
    url(r'^ajax_getnaiclevel/$', get_naiclevel, name="getnaiclevel"),
    # url(r"^accounts/inactive/$", views.AccountInactiveView.as_view, name="account_inactive"),
    url(r"^accounts/inactive/$", account_inactive, name="account_inactive"),

]
