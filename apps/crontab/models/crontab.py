from django.db import models
from django.utils.translation import ugettext_lazy as _


def cronexp(field):
    """Representation of cron expression."""
    return field and str(field).replace(' ', '') or '*'


# Create your models here.
class Crontab(models.Model):
    name = models.CharField('CrontabName', max_length=50, help_text='CrontabName', null=False)
    job = models.CharField('Job', max_length=50, help_text='Job', null=False)
    asset_id = models.IntegerField(_('Asset id'), null=False)
    port = models.IntegerField(default=22, verbose_name=_('Port'))
    minute = models.CharField(_('Minute'), max_length=60 * 4, default='*')
    hour = models.CharField(_('Hour'), max_length=24 * 4, default='*')
    day_of_week = models.CharField(_('Day of week'), max_length=64, default='*')
    day_of_month = models.CharField(_('Day of month'), max_length=31 * 4, default='*')
    month_of_year = models.CharField(_('Month of year'), max_length=64, default='*')
    gmt_created = models.DateTimeField('Date created', auto_now_add=True)
    gmt_modified = models.DateTimeField('Date updated', auto_now=True)
    is_deleted = models.BooleanField('Is deleted', default=False)

    class Meta:
        verbose_name = _('crontab')
        verbose_name_plural = _('crontabs')
        ordering = ['month_of_year', 'day_of_month', 'day_of_week', 'hour', 'minute']

    def __str__(self):
        return '{0} {1} {2} {3} {4} (m/h/d/dM/MY)'.format(cronexp(self.minute), cronexp(self.hour),
                                                          cronexp(self.day_of_week), cronexp(self.day_of_month),
                                                          cronexp(self.month_of_year))