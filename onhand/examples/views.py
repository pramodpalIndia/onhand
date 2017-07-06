from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from onhand.examples.admin import CountryExampleForm
from .models import CountryExample

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'examples/continent/change_list.html'
    form = CountryExampleForm
    context_object_name = 'result_count'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return CountryExample.objects.all()
