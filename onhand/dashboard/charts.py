from __future__ import unicode_literals
import psutil
from django.utils.translation import ugettext_lazy as _
from suit_dashboard.decorators import refreshable

@refreshable(refresh_time=1000)
def machine_usage_chart():
    # Retrieve RAM and CPU data
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent()

    # Green, orange, red or grey color for usage/idle
    green, orange, red, grey = '#00FF38', '#FFB400', '#FF3B00', '#EBEBEB'

    ram_color = green  # default
    if ram >= 75:
        ram_color = red
    elif ram >= 50:
        ram_color = orange

    cpu_color = green  # default
    if cpu >= 75:
        cpu_color = red
    elif cpu >= 50:
        cpu_color = orange

    # Now create a chart to display CPU and RAM usage
    chart_options = {
        'chart': {
            'type': 'bar',
            'height': 200,
        },
        'title': {
            'text': _('RAM and CPU usage')
        },
        'xAxis': {
            'categories': [_('CPU usage'), _('RAM usage')]
        },
        'yAxis': {
            'min': 0,
            'max': 100,
            'title': {
                'text': _('Percents')
            }
        },
        'tooltip': {
            'percentageDecimals': 1
        },
        'legend': {
            'enabled': False
        },
        'plotOptions': {
            'series': {
                'stacking': 'normal'
            }
        },
        'series': [{
            'name': _('CPU idle'),
            'data': [{'y': 100 - cpu, 'color': grey}, {'y': 0}],
        }, {
            'name': _('CPU used'),
            'data': [{'y': cpu, 'color': cpu_color}, {'y': 0}],
        }, {
            'name': _('RAM free'),
            'data': [{'y': 0}, {'y': 100 - ram, 'color': grey}],
        }, {
            'name': _('RAM used'),
            'data': [{'y': 0}, {'y': ram, 'color': ram_color}],
        }]
    }

    return chart_options
