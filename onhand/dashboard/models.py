from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from onhand.subscription.models import Subscription, SubscriptionDetail


class Alert(models.Model):
    SYSTEM_ALERT = 'system_alert'
    USER_ALERT = 'user_alert'
    CUSTOMER_ALERT = 'customer_alert'

    TYPE_CHOICES = (
        (SYSTEM_ALERT, 'System Generated Alert'),
        (USER_ALERT, 'User Generated Alert'),
        (CUSTOMER_ALERT, 'Customer Generated Alert')
    )

    type = models.CharField(max_length=255, null=False, blank=False, choices=TYPE_CHOICES)
    customer = models.ForeignKey(Subscription, null=False, blank=False)
    dealer = models.ForeignKey(SubscriptionDetail, null=True, blank=True)
    data = models.TextField(null=False, blank=False, default='{}')
    dt_event = models.DateTimeField(null=True)
    is_read = models.BooleanField(null=False, blank=False, default=False)

    def __unicode__(self):
        unread = '[UNREAD] ' if not self.is_read else ''
        return str(
            '%s%s: %s on %s' % (unread, self.customer.id, self.get_type_display(), self.dt_event.strftime('%b %d, %Y')))

    class Meta:
        ordering = ('-dt_event', 'customer')
