from django.contrib import admin

from .models import Question, Choice

from django.contrib import admin
from django.contrib.admin.sites import AdminSite

admin.site.site_header = 'On hand LLC'
admin.site.site_title = 'On Hand DB Admin'
admin.site.index_title= 'On Hand  DB Site Administration'

class UserAdmin(AdminSite):
    def has_permission(self, request):
        """
        Removed check for is_staff.
        """
        return request.user.is_active

    @property
    def is_staff(self):
        return self.is_admin

user_admin_site = UserAdmin(name='usersadmin')



class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    # list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']

admin.site.register(Question, QuestionAdmin)
