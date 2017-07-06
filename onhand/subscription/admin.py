# import django
# from django.contrib import admin
#
# from onhand.provider.adapter import get_adapter
# from .models import Person, Company
#
#
# class PersonAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'email')
#     list_filter = ('first_name', 'last_name')
#     search_fields = []
#     raw_id_fields = ('first_name','last_name')
#
#     def __init__(self, *args, **kwargs):
#         super(PersonAdmin, self).__init__(*args, **kwargs)
#         # if not self.search_fields and django.VERSION[:2] < (1, 7):
#         self.search_fields = self.get_search_fields(None)
#
#     def get_search_fields(self, request):
#         base_fields = get_adapter(request).get_person_search_fields()
#         return ['email'] + list(map(lambda a: 'person__' + a, base_fields))
#
#
# class CompanyAdmin(admin.ModelAdmin):
#     list_display = ('email_address', 'created', 'sent', 'key')
#     list_filter = ('sent',)
#     raw_id_fields = ('email_address',)
#
#
# admin.site.register(Person, PersonAdmin)
# admin.site.register(Company, CompanyAdmin)
