from django.utils.translation import ugettext_lazy as _
from apps.ops.models import Adhoc
from typing import List


def update_or_create_ansible_task(name: str, hosts: List, tasks: List, pattern: str='all'):
    ansible_obj, ok = Adhoc.objects.update_or_create(name=name)
    update = False

    if ok:
        ansible_obj.hosts = hosts
        ansible_obj.tasks = tasks
        ansible_obj.pattern = pattern
        update = True
    else:
        if ansible_obj.tasks != tasks:
            ansible_obj.tasks = tasks
            update = True
        if ansible_obj.hosts != hosts:
            ansible_obj.hosts = hosts
            update = True

    if update:
        ansible_obj.save()

    return ansible_obj

