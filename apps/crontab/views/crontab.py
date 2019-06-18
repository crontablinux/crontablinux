import json
from django.shortcuts import render
from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.crontab.models import Crontab
from apps.ops.models import Adhoc
from apps.common.format_response import api_response
# Create your views here.


class CronListView(View):
    def get(self, request, *args, **kwargs):
        """
        get assets
        :return:
        """
        request_data = request.GET
        name = request_data.get('crontab_name', '')
        job = request_data.get('job', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))

        msg = ''
        query_params = Q(is_deleted=False)
        if name:
            query_params &= Q(name__startwith=name)
        if job:
            query_params &= Q(ip=job)
        if create_start:
            query_params &= Q(gmt_created__gte=create_start)
        if create_end:
            query_params &= Q(gmt_created__lte=create_end)

        if reverse:
            order_by_str = '-gmt_created'
        else:
            order_by_str = 'gmt_created'

        ansible_objects = Crontab.objects.filter(query_params).order_by(order_by_str)
        paginator = Paginator(ansible_objects, per_page)

        try:
            cron_paginator = paginator.page(page)
        except PageNotAnInteger:
            cron_paginator = paginator.page(1)
            msg = 'Page is not Integer'
        except EmptyPage:
            cron_paginator = paginator.page(paginator.num_pages)
            msg = 'Page is Empty'

        cron_result_object_list = cron_paginator.object_list
        cron_result_restful_list = []
        for cron_result_object in cron_result_object_list:
            cron_result_restful_list.append(dict(id=cron_result_object.id,
                                                 name=cron_result_object.name,
                                                 job=cron_result_object.job,
                                                 minute=cron_result_object.minute,
                                                 hour=cron_result_object.hour,
                                                 day=cron_result_object.day_of_week,
                                                 month=cron_result_object.day_of_month,
                                                 month_of_year=cron_result_object.month_of_year,
                                                 gmt_created = str(cron_result_object.gmt_created)[:19],
                                                 gmt_modified = str(cron_result_object.gmt_modified)[:19],
                                                 ))
        data = dict(value=cron_result_restful_list, per_page=per_page, page=page, total=paginator.count)
        if msg:
            return api_response(code=200, msg=msg, data=data)
        else:
            return api_response(code=200, data=data)

    def post(self, request, *args, **kwargs):
        """
        create asset
        """
        json_str = request.body.decode('utf-8')
        if not json_str:
            return api_response(code=201, msg='post args is empty', data={})

        request_data_dict = json.loads(json_str)

        msg = ''
        name = request_data_dict.get('crontab_name', '')
        job = request_data_dict.get('job', '')
        minute = request_data_dict.get('minute', '*')
        hour = request_data_dict.get('hour', '*')
        day = request_data_dict.get('day', '*')
        month = request_data_dict.get('month', '*')
        week = request_data_dict.get('week', '*')

        if not name:
            msg = 'pls input hostname'
        elif not job:
            msg = 'pls input job'
        elif Crontab.objects.filter(name=name, is_deleted=False).exists():
            msg = 'Crontab Name {} already exist'.format(name)

        if msg:
            return api_response(code=201, msg=msg, data={})

        data = dict(name=name, job=job, minute=minute, hour=hour, day_of_month=day, month_of_year=month,
                    day_of_week=week)
        new_cron = Crontab(**data)
        new_cron.save()

        new_cron.ansible
        ansible_id = new_cron.ansible_id
        data['ansible_id'] = ansible_id

        return api_response(code=200, data=data)


class CronView(View):
    def get(self, request, *args, **kwargs):
        """
        Get Asset Detail
        """
        request_data = request.GET
        cron_id = kwargs.get('cron_id')
        msg = ''

        cron_query = Crontab.objects.filter(id=cron_id)

        if not cron_query.exists():
            msg = 'crontab not exists'
            return api_response(code=201, msg=msg, data={})

        cron_obj = cron_query[0]
        ansible_id = cron_obj.ansible_id

        if ansible_id == 0:
            ansible_info = {}
        else:
            ansible_obj = Adhoc.objects.get(pk=ansible_id)
            ansible_info = dict(tasks=ansible_obj.tasks, pattern=ansible_obj.pattern, hosts=ansible_obj.hosts)

        data = dict(id=cron_obj.id, crontab_name=cron_obj.name, job=cron_obj.job, minute=cron_obj.minute,
                    hour=cron_obj.hour, day=cron_obj.day_of_month, month=cron_obj.month_of_year,
                    week=cron_obj.day_of_week, is_deleted=cron_obj.is_deleted, ansible_info=ansible_info,
                    gmt_created=str(cron_obj.gmt_created)[:19], gmt_modified=str(cron_obj.gmt_modified)[:19])

        return api_response(code=200, data=data)

    def patch(self, request, *args, **kwargs):
        """
        patch asset
        """
        json_str = request.body.decode('utf-8')
        update = False
        if not json_str:
            return api_response(code=201, msg='patch args is empty', data={})
        request_data_dict = json.loads(json_str)
        cron_id = kwargs.get('cron_id')

        cron_query = Crontab.objects.filter(pk=cron_id)
        if not cron_query.exists():
            msg = 'asset not exists'
            return api_response(code=201, msg=msg, data={})

        cron_obj = cron_query[0]

        name = request_data_dict.get('crontab_name', '')
        job = request_data_dict.get('job', '')
        minute = request_data_dict.get('minute', '')
        hour = request_data_dict.get('hour', '*')
        day = request_data_dict.get('day', '*')
        month = request_data_dict.get('month', '*')
        week = request_data_dict.get('week', '*')

        if name and cron_obj.name != name:
            cron_obj.name = name
            update = True
        if job and cron_obj.job != job:
            cron_obj.ip = job
            update = True
        if minute and cron_obj.minute != minute:
            cron_obj.minute = minute
            update = True
        if hour and cron_obj.hour != hour:
            cron_obj.hour = hour
            update = True
        if day and cron_obj.day_of_month != day:
            cron_obj.day_of_month = day
            update = True
        if month and cron_obj.month_of_year != month:
            cron_obj.month_of_year = month
            update = True
        if week and cron_obj.day_of_week != week:
            cron_obj.day_of_week = week
            update = True

        if update:
            cron_obj.save()

        data = dict(id=cron_obj.id, crontab_name=cron_obj.name, job=cron_obj.job, minute=cron_obj.minute,
                    hour=cron_obj.hour, day=cron_obj.day_of_month, month=cron_obj.month_of_year,
                    week=cron_obj.day_of_week, is_deleted=cron_obj.is_deleted,
                    gmt_created=str(cron_obj.gmt_created)[:19], gmt_modified=str(cron_obj.gmt_modified)[:19])

        return api_response(code=200, data=data)
