from django.db import models
from django.utils.translation import ugettext_lazy as _


class AssetUser(models.Model):
    name = models.CharField('Username', max_length=50, help_text='Username', null=False)
    _password = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Password'))
    gmt_created = models.DateTimeField('Date created', auto_now_add=True)
    gmt_modified = models.DateTimeField('Date updated', auto_now=True)
    is_deleted = models.BooleanField('Is deleted', default=False)

    @property
    def password(self):
        if self._password:
            return self._password

    @password.setter
    def password(self, password_raw):
        if password_raw:
            self._password = password_raw
        else:
            raise SyntaxError("Password shouldn`t be empty")
