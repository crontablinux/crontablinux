import json
from django.db import models
from apps.ops.ansible.inventory import CrontabInventory
from apps.ops.ansible.runner import AdHocRunner
from apps.ops.ansible.exceptions import AnsibleError
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class Adhoc(models.Model):
    """
        _tasks: [{'name': 'task_name', 'action': {'module': '', 'args': ''}, 'other..': ''}, ]
        _hosts: ["host_id1", "host_id2"]
        pattern: Even if we set _hosts, We only use that to make inventory,
                 We also can set `patter` to run task on match hosts
    """
    _tasks = models.TextField(verbose_name=_('Tasks'))
    pattern = models.CharField(max_length=64, default='{}', verbose_name=_('Pattern'))
    _hosts = models.TextField(blank=True, verbose_name=_('Hosts'))
    gmt_created = models.DateTimeField('Date created', auto_now_add=True)
    gmt_modified = models.DateTimeField('Date updated', auto_now=True)
    is_deleted = models.BooleanField('Is deleted', default=False)

    class Meta:
        verbose_name = _('Adhoc')
        verbose_name_plural = _('Adhoc')

    @property
    def tasks(self):
        try:
            return json.loads(self._tasks)
        except:
            return []

    @tasks.setter
    def tasks(self, item):
        if item and isinstance(item, list):
            self._tasks = json.dumps(item)
        else:
            raise SyntaxError('Tasks should be a list: {}'.format(item))

    @property
    def hosts(self):
        try:
            return json.loads(self._hosts)
        except:
            return []

    @hosts.setter
    def hosts(self, item):
        if item and isinstance(item, list):
            self._hosts = json.dumps(item)
        else:
            raise SyntaxError('Hosts should be a list: {}'.format(item))

    @property
    def inventory(self):
        inventory = CrontabInventory(host=self.hosts)
        return inventory

    def run(self):
        runner = AdHocRunner(inventory=self.inventory)
        try:
            result = runner.run(tasks=self.tasks, pattern=self.pattern)
            return result.results_raw, result.results_summary
        except AnsibleError as err:
            raise AnsibleError('Ansible err {}: {}'.format(err, self.tasks))
