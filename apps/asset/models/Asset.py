from django.db import models
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class Asset(models.Model):
    name = models.CharField('Hostname', max_length=50, help_text='Hostname', null=False)
    ip = models.GenericIPAddressField(max_length=32, verbose_name=_('IP'), db_index=True)
    user_id = models.IntegerField(_('User id'), null=False)
    port = models.IntegerField(default=22, verbose_name=_('Port'))
    gmt_created = models.DateTimeField('Date created', auto_now_add=True)
    gmt_modified = models.DateTimeField('Date updated', auto_now=True)
    is_deleted = models.BooleanField('Is deleted', default=False)

    class Meta:
        verbose_name = _('Asset')
        verbose_name_plural = _('Asset')
