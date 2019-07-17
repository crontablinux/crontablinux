import os
from celery import Celery
from typing import List


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.prod')
import django
django.setup()


app = Celery('crontablinux')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

from django.db.models import Q
from apps.ops.utils import update_or_create_ansible_task
from apps.asset.models import Asset
from apps.crontab.models import CrontabAsset, Crontab

@app.task
def test_task(a, b):
    print('a:', a)
    print('b:', b)
    print(a+b)


@app.task
def update_asset_crontabs_tasks(host_id: int, cron_id: int=0, pattern: str='all', status: str='', tasks_name: str=None):
    """
    :param host_obj: Asset
    :param tasks_name:
    :return:
    """
    msg = ''

    if host_id is None:
        msg = 'hosts should`t be empty'
    elif tasks_name is None:
        msg = 'name should`t be empty'

    if msg:
        return msg

    query_params = Q(asset_id=host_id)

    if cron_id != 0:
        query_params &= Q(crontab_id=cron_id)

    crontab_asset_query = CrontabAsset.objects.filter(query_params)

    if not crontab_asset_query.exists():
        msg = 'No Crontab exec to this asset'
        return msg

    crontab_list = []
    for i in range(crontab_asset_query.count()):
        obj = crontab_asset_query[i]
        if obj.crontab_id in crontab_list:
            msg = 'crontab asset relative is not normal'
            return msg
        crontab_list.append(obj.crontab_id)

    crontab_query = Crontab.objects.filter(id__in=crontab_list)

    tasks = []
    hosts = [host_id]

    for i in range(crontab_asset_query.count()):
        obj = crontab_asset_query[i]
        crontab_id = obj.crontab_id
        crontab_obj = crontab_query.get(id=crontab_id)

        if crontab_obj.is_deleted or obj.is_deleted or status == 2:
            state = 'absent'
        else:
            state = 'present'

        minute = crontab_obj.minute
        hour = crontab_obj.hour
        day = crontab_obj.day_of_month
        week = crontab_obj.day_of_week
        month = crontab_obj.month_of_year
        name = crontab_obj.name
        job = crontab_obj.job

        task = {'name': crontab_obj.name,
                'action': {'module': 'cron', 'args': 'minute={} hour={} day={} weekday={} month={} name="{}" job="{}" '
                                                     'state={}'.format(minute, hour, day, week, month, name, job,
                                                                       state)}}
        tasks.append(task)

    ansible_obj = update_or_create_ansible_task(pattern=pattern, tasks=tasks, hosts=hosts, name=tasks_name)
    results_raw, results_summary = ansible_obj.run()
    if status == 1 and results_summary['success']:
        for i in range(crontab_asset_query.count()):
            obj = crontab_asset_query[i]
            obj.status = status
            obj.save()
    else:
        for i in range(crontab_asset_query.count()):
            obj = crontab_asset_query[i]
            obj.status = 2
            obj.save()

    return results_raw, results_summary


# @app.task
# def update_crontab_tasks(crontab_id: int, pattern: str='all', tasks_name: str=None):
#     """
#     :param host_obj: Asset
#     :param tasks_name:
#     :return:
#     """
#     msg = ''
#
#     if crontab_id is None:
#         msg = 'crontab_id should`t be empty'
#     elif tasks_name is None:
#         msg = 'name should`t be empty'
#
#     if msg:
#         return msg
#
#     crontab_asset_query = CrontabAsset.objects.filter(crontab_id=crontab_id)
#
#     if not crontab_asset_query.exists():
#         msg = 'No Crontab exec to this asset'
#         return msg
#
#     hosts = []
#     for obj in crontab_asset_query:
#         if obj.crontab_id not in hosts:
#             hosts.append(obj.asset_id)
#
#     tasks = []
#
#     crontab_obj = Crontab.objects.get(id=crontab_id)
#
#     if crontab_obj.is_deleted:
#         state = 'absent'
#     else:
#         state = 'present'
#
#     minute = crontab_obj.minute
#     hour = crontab_obj.hour
#     day = crontab_obj.day_of_month
#     week = crontab_obj.day_of_week
#     month = crontab_obj.month_of_year
#     name = crontab_obj.name
#     job = crontab_obj.job
#
#     task = {'name': crontab_obj.name,
#             'action': {'module': 'cron', 'args': 'minute={} hour={} day={} weekday={} month={} name="{}" job="{}" '
#                                                  'state={}'.format(minute, hour, day, week, month, name, job,
#                                                                    state)}}
#     tasks.append(task)
#
#     ansible_obj = update_or_create_ansible_task(pattern=pattern, tasks=tasks, hosts=hosts, name=tasks_name)
#     return ansible_obj
