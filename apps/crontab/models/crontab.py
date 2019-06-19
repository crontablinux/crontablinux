from django.db import models
from apps.ops.utils import update_or_create_ansible_task
from django.utils.translation import ugettext_lazy as _

from apps.ops.models import Adhoc


class CrontabError(Exception):
    pass


def cronexp(field):
    """Representation of cron expression."""
    return field and str(field).replace(' ', '') or '*'


# Create your models here.
class Crontab(models.Model):
    name = models.CharField('CrontabName', max_length=50, help_text='CrontabName', null=False)
    job = models.CharField('Job', max_length=50, help_text='Job', null=False)
    # ansible_id = models.IntegerField('Ansible id', default=0)
    minute = models.CharField(_('Minute'), max_length=60 * 4, default='*')
    hour = models.CharField(_('Hour'), max_length=24 * 4, default='*')
    day_of_week = models.CharField(_('Day of week'), max_length=64, default='*')
    day_of_month = models.CharField(_('Day of month'), max_length=31 * 4, default='*')
    month_of_year = models.CharField(_('Month of year'), max_length=64, default='*')
    gmt_created = models.DateTimeField('Date created', auto_now_add=True)
    gmt_modified = models.DateTimeField('Date updated', auto_now=True)
    is_deleted = models.BooleanField('Is deleted', default=False)

    class Meta:
        verbose_name = _('Crontab')
        verbose_name_plural = _('Crontabs')
        ordering = ['month_of_year', 'day_of_month', 'day_of_week', 'hour', 'minute']

    def __str__(self):
        return '{0} {1} {2} {3} {4} (m/h/d/dM/MY)'.format(cronexp(self.minute), cronexp(self.hour),
                                                          cronexp(self.day_of_week), cronexp(self.day_of_month),
                                                          cronexp(self.month_of_year))

    # @property
    # def ansible(self):
    #     if not Adhoc.objects.filter(pk=self.ansible_id).exists() or self.is_deleted:
    #         asset_list = [i.asset_id for i in CrontabAsset.objects.filter(crontab_id=self.id)]
    #         if not asset_list:
    #             self.ansible_id = 0
    #             # msg = 'Crontab dont related'
    #             return
    #
    #         if self.is_deleted:
    #             state = 'absent'
    #         else:
    #             state = 'present'
    #         tasks = [{'name': self.name,
    #                  'action': {'module': 'cron', 'args': 'minute={} hour={} day={} weekday={} month={} name="{}" '
    #                                                       'job="{}" state={}'.format(self.minute,
    #                                                                                  self.hour,
    #                                                                                  self.day_of_month,
    #                                                                                  self.day_of_week,
    #                                                                                  self.month_of_year,
    #                                                                                  self.name,
    #                                                                                  self.job, state)}}]
    #
    #         new_ansible = update_or_create_ansible_task(pattern='all', tasks=tasks, hosts=asset_list)
    #         self.ansible_id = new_ansible.id
    #         self.save()
    #         return new_ansible
    #     ansible = Adhoc.objects.get(id=self.ansible_id)
    #     return ansible
    #
    # def run(self):
    #     if self.ansible:
    #         return self.ansible.run()
    #     else:
    #         return {'error': 'No ansible'}


class CrontabAsset(models.Model):
    """
    资产计划任务
    """
    asset_id = models.IntegerField('Asset id')
    crontab_id = models.IntegerField('Crontab id')

    gmt_created = models.DateTimeField('Date created', auto_now_add=True)
    gmt_modified = models.DateTimeField('Date updated', auto_now=True)
    is_deleted = models.BooleanField('Is deleted', default=False)

    class Meta:
        verbose_name = _('Crontab Asset')
        verbose_name_plural = _('Crontabs Asset')
