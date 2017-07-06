from django.contrib import admin
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.forms import TextInput, ModelForm, Textarea, Select, ModelChoiceField
from reversion.admin import VersionAdmin
from import_export.admin import ImportExportModelAdmin
from suit_ckeditor.widgets import CKEditorWidget
from suit_redactor.widgets import RedactorWidget
from onhand.compliance.models import ComplianceService, ServiceJurisdiction, V_Service_jurisdiction
from suit.admin import SortableTabularInline, SortableModelAdmin, \
    SortableStackedInline
from suit.widgets import SuitDateWidget, SuitSplitDateTimeWidget, \
    EnclosedInput, LinkedSelect, AutosizedTextarea
from django_select2.forms import HeavySelect2Widget, ModelSelect2Mixin
# from django_select2.models import
# from django_select2.models import AutoModelSelect2Field, AutoHeavySelect2Widget
from mptt.admin import MPTTModelAdmin

# Register your models here.
from onhand.management.models import Country, State, County


class StateExampleFilter(SimpleListFilter):
    """
    List filter example that shows only referenced(used) values
    """
    title = 'State'
    parameter_name = 'State'

    def lookups(self, request, model_admin):
        # You can use also "CountryExample" instead of "model_admin.model"
        # if this is not direct relation
        states = set([c.stat_code for c in model_admin.model.objects.all()])
        return [(c.stat_code, c.stat_name) for c in states]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(State__id__exact=self.value())
        else:
            return queryset

class CountyExampleFilter(SimpleListFilter):
    """
    List filter example that shows only referenced(used) values
    """
    title = 'County'
    parameter_name = 'County'

    def lookups(self, request, model_admin):
        # You can use also "CountryExample" instead of "model_admin.model"
        # if this is not direct relation
        counties = set([c.cont_id for c in model_admin.model.objects.all()])
        return [(c.cont_id, c.name) for c in counties]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(County__id__exact=self.value())
        else:
            return queryset

# Inlines for KitchenSink
class CountryInlineForm(ModelForm):
    class Meta:
        model = Country
        widgets = {
            'ctry_code': Select(attrs={'class': 'input-small'}),
        }
        fields = []

class CountryInline(SortableTabularInline):
    model = Country
    form = CountryInlineForm
    extra = 1
    verbose_name_plural = 'Country (Tabular inline)'


class StateInline(SortableStackedInline):
    model = State
    extra = 1
    verbose_name_plural = 'States (Stacked inline)'


class ServiceJurisdictionForm(ModelForm):
    class Meta:
        widgets = {
            'ctry_code' : Select,
            'stat_code': Select,
            'cont_id': Select,
            'multiple2': TextInput(attrs={'class': 'input-small'}),
            'date': AdminDateWidget(attrs={'class': 'vDateField input-small'}),
            'date_widget': SuitDateWidget,
            'datetime_widget': SuitSplitDateTimeWidget,
            'textfield': AutosizedTextarea(attrs={'rows': '2'}),
            'linked_foreign_key': LinkedSelect,

            'enclosed1': EnclosedInput(append='icon-plane',
                                       attrs={'class': 'input-medium'}),
            'enclosed2': EnclosedInput(prepend='icon-envelope',
                                       append='<input type="button" '
                                              'class="btn" value="Send">',
                                       attrs={'class': 'input-medium'}),
        }

    class stat_code(ModelChoiceField):
        def label_from_instance(self, obj):
            print( "My Object #%i" ) % obj.id
            return "My Object #%i" % obj.id

    def __init__(self, *args, **kwargs):
        super(ServiceJurisdictionForm, self).__init__(*args, **kwargs)
        # access object through self.instance...
        print( self.fields)
        self.fields['cont_id'].queryset = County.objects.filter(state= 'FL')






class ServiceJurisdictionAdmin(admin.ModelAdmin):
    raw_id_fields = ()
    form = ServiceJurisdictionForm
    # inlines = (FridgeInline, MicrowaveInline)
    # inlines = (CountryInline, StateInline)
    search_fields = ['ctyp_id']
    # radio_fields = {"horizontal_choices": admin.HORIZONTAL,
    #                 'vertical_choices': admin.VERTICAL}
    # list_editable = ('boolean', )
    list_filter = ('cont_name',CountyExampleFilter)
    # readonly_fields = ('readonly_field',)
    # raw_id_fields = ('raw_id_field',)
    # fields = []
    list_display = (
        'ctyp_id', 'govl_code', 'cont_name',  'stat_name', 'ctry_name' )
    fieldsets = [
        # (None, {'fields': ['name', 'help_text', 'textfield',
        #                    ('multiple_in_row', 'multiple2'),
        #                    'file', 'readonly_field']}),

        # ('Date and time', {
        #     'description': 'Improved date/time widgets (SuitDateWidget, '
        #                    'SuitSplitDateTimeWidget) . Uses original JS.',
        #     'fields': ['date_widget', 'datetime_widget']}),

        ('Foreign key relations',
         {'description': 'Original select and linked select feature',
          'fields': [ 'ctry_code', 'stat_code','cont_id']}),

        (None, {'fields': ['govl_code', 'ctyp_id', 'srvj_help_text']}),

        # ('EnclosedInput widget',
        #  {
        #      'description': 'Supports Twitter Bootstrap prepended, '
        #                     'appended inputs',
        #      'fields': ['enclosed1', 'enclosed2']}),
        #
        # ('Boolean and choices',
        #  {'fields': ['boolean', 'boolean_with_help', 'choices',
        #              'horizontal_choices', 'vertical_choices']}),
        #
        # ('Collapsed settings', {
        #     'classes': ('collapse',),
        #     'fields': ['hidden_checkbox', 'hidden_choice']}),
        # ('And one more collapsable', {
        #     'classes': ('collapse',),
        #     'fields': ['hidden_charfield', 'hidden_charfield2']}),

    ]

    def get_formsets(self, request, obj=None):
        """
        Set extra=0 for inlines if object already exists
        """
        for inline in self.get_inline_instances(request):
            formset = inline.get_formset(request, obj)
            if obj:
                formset.extra = 0
            yield formset


admin.site.register(V_Service_jurisdiction, ServiceJurisdictionAdmin)
