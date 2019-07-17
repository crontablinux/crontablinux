import json
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.asset.models import Asset, AssetUser
from apps.crontab.models import Crontab, CrontabAsset
from apps.common.format_response import api_response

from tasks import update_asset_crontabs_tasks
# Create your views here.


class AssetListView(View):
    def get(self, request, *args, **kwargs):
        """
        获取资产列表
        :return:
        """
        request_data = request.GET
        name = request_data.get('hostname', '')
        ip = request_data.get('ip', '')
        user_id = request_data.get('user_id', '')
        port = request_data.get('port', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))

        msg = ''
        query_params = Q(is_deleted=False)
        if name:
            query_params &= Q(name__startwith=name)
        if ip:
            query_params &= Q(ip=ip)
        if user_id:
            query_params &= Q(user_id=user_id)
        if port:
            query_params &= Q(port=port)
        if create_start:
            query_params &= Q(gmt_created__gte=create_start)
        if create_end:
            query_params &= Q(gmt_created__lte=create_end)

        if reverse:
            order_by_str = '-gmt_created'
        else:
            order_by_str = 'gmt_created'

        asset_objects = Asset.objects.filter(query_params).order_by(order_by_str)
        asset_count = asset_objects.count() if asset_objects.count() else 1
        paginator = Paginator(asset_objects, per_page if per_page != 0 else asset_count)

        try:
            asset_paginator = paginator.page(page)
        except PageNotAnInteger:
            asset_paginator = paginator.page(1)
            msg = 'Page is not Integer'
        except EmptyPage:
            asset_paginator = paginator.page(paginator.num_pages)
            msg = 'Page is Empty'

        asset_result_object_list = asset_paginator.object_list
        asset_result_restful_list = []
        for asset_result_object in asset_result_object_list:
            user_id = asset_result_object.user_id
            user_obj = AssetUser.objects.get(id=user_id)
            user_info = dict(user_name = user_obj.name, user_id = user_obj.id)
            asset_result_restful_list.append(dict(id=asset_result_object.id,
                                                  name=asset_result_object.name,
                                                  ip=asset_result_object.ip,
                                                  port=asset_result_object.port,
                                                  user_info=user_info,
                                                  gmt_created = str(asset_result_object.gmt_created)[:19],
                                                  gmt_modified = str(asset_result_object.gmt_modified)[:19],
                                                  ))
        data = dict(value=asset_result_restful_list, per_page=per_page, page=page, total=paginator.count)
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
        name = request_data_dict.get('hostname', '')
        ip = request_data_dict.get('ip', '')
        port = request_data_dict.get('port', '')
        user_id = int(request_data_dict.get('user_id', ''))

        if not name:
            msg = 'pls input hostname'
        elif not ip:
            msg = 'pls input ip'
        elif not port:
            msg = 'pls input port'
        elif not user_id:
            msg = 'pls input user'
        elif not AssetUser.objects.filter(pk=user_id, is_deleted=False).exists():
            msg = 'the asset user dont exist'
        elif Asset.objects.filter(ip=ip, port=port, is_deleted=False).exists():
            msg = 'Asset ip: {} Port: {} already exist'.format(ip, port)

        if msg:
            return api_response(code=201, msg=msg, data={})

        data = dict(name=name, ip=ip, port=port, user_id=user_id)
        new_asset = Asset(**data)
        new_asset.save()
        data['id'] = new_asset.id

        return api_response(code=200, data=data)


class AssetView(View):
    def get(self, request, *args, **kwargs):
        """
        Get Asset Detail
        """
        request_data = request.GET
        asset_id = kwargs.get('asset_id')
        msg = ''

        asset_obj = get_object_or_404(Asset, pk=asset_id)
        user_id = asset_obj.user_id

        user_obj = AssetUser.objects.get(pk=user_id)
        user_info = dict(username=user_obj.name)

        data = dict(id=asset_obj.id, hostname=asset_obj.name, ip=asset_obj.ip, port=asset_obj.port, user_info=user_info,
                    is_deleted=asset_obj.is_deleted, gmt_created=str(asset_obj.gmt_created)[:19],
                    gmt_modified=str(asset_obj.gmt_modified)[:19])

        return api_response(code=200, data=data)

    def patch(self, request, *args, **kwargs):
        """
        patch asset
        """
        json_str = request.body.decode('utf-8')
        update = False
        if not json_str:
            return api_response(code=201, msg='post args is empty', data={})
        request_data_dict = json.loads(json_str)
        asset_id = kwargs.get('asset_id')

        asset_obj = get_object_or_404(Asset, pk=asset_id)

        name = request_data_dict.get('hostname', '')
        ip = request_data_dict.get('ip', '')
        user_id = request_data_dict.get('user_id', '')
        port = request_data_dict.get('port', '')
        is_deleted = request_data_dict.get('is_deleted', False)

        if name and asset_obj.name != name:
            asset_obj.name = name
            update = True
        if ip and asset_obj.ip != ip:
            asset_obj.ip = ip
            update = True
        if user_id and asset_obj.user_id != user_id:
            asset_obj.user_id = user_id
            update = True
        if port and asset_obj.port != port:
            asset_obj.port = port
            update = True
        if asset_obj.is_deleted != is_deleted:
            asset_obj.is_deleted = is_deleted
            update = True

        if update:
            asset_obj.save()

        data = dict(hostname=asset_obj.name, ip=asset_obj.ip, user_id=asset_obj.user_id, port=asset_obj.port,
                    is_deleted=asset_obj.is_deleted)
        return api_response(code=200, data=data)


class AssetCrons(View):
    def get(self, request, *args, **kwargs):
        """
        Get Asset crontabs
        """
        request_data = request.GET
        asset_id = kwargs.get('asset_id')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))

        msg = ''
        crontab_asset_objs = CrontabAsset.objects.filter(asset_id=asset_id, is_deleted=False)
        crontab_ids = [i.crontab_id for i in crontab_asset_objs]
        query_params = Q(is_deleted=False)
        query_params &= Q(id__in=crontab_ids)

        if reverse:
            order_by_str = '-gmt_created'
        else:
            order_by_str = 'gmt_created'

        crontab_objs = Crontab.objects.filter(query_params).order_by(order_by_str)
        paginator = Paginator(crontab_objs, per_page)

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
            crontab_asset_obj = crontab_asset_objs.get(crontab_id=cron_result_object.id)
            cron_result_restful_list.append(dict(id=cron_result_object.id,
                                                 name=cron_result_object.name,
                                                 job=cron_result_object.job,
                                                 time="{} {} {} {} {}".format(
                                                     cron_result_object.minute,
                                                     cron_result_object.hour,
                                                     cron_result_object.day_of_month,
                                                     cron_result_object.month_of_year,
                                                     cron_result_object.day_of_week
                                                 ),
                                                 asset_id=asset_id,
                                                 status=crontab_asset_obj.status,
                                                 gmt_created=str(cron_result_object.gmt_created)[:19],
                                                 gmt_modified=str(cron_result_object.gmt_modified)[:19],
                                                 ))
        data = dict(value=cron_result_restful_list, per_page=per_page, page=page, total=paginator.count)
        if msg:
            return api_response(code=200, msg=msg, data=data)
        else:
            return api_response(code=200, data=data)

    def post(self, request, *args, **kwargs):
        """
        Update Asset Cron
        """
        asset_id = kwargs.get('asset_id')
        asset_obj = get_object_or_404(Asset, pk=asset_id)
        asset_name = asset_obj.name
        task_name = "{} update crontabs".format(asset_name)
        task = update_asset_crontabs_tasks.delay(host_id=asset_id, tasks_name=task_name)
        data = {"task": task.id}
        return api_response(code=200, data=data)


class AssetCron(View):
    def patch(self, request, *args, **kwargs):
        """
        Update Asset Cron
        """
        asset_id = kwargs.get('asset_id')
        cron_id = kwargs.get('cron_id')
        asset_obj = get_object_or_404(Asset, pk=asset_id)
        cron_obj = get_object_or_404(Crontab, pk=cron_id)
        asset_crontab_obj = get_object_or_404(CrontabAsset, asset_id=asset_id, crontab_id=cron_id)
        json_str = request.body.decode('utf-8')
        update = False
        if not json_str:
            return api_response(code=201, msg='post args is empty', data={})
        request_data_dict = json.loads(json_str)
        status = request_data_dict.get('status', '')

        if status and asset_crontab_obj.status != status:
            asset_crontab_obj.status = 3
            update = True

        if update:
            asset_name = asset_obj.name
            cron_name = cron_obj.name
            task_name = "{} update crontab {}".format(asset_name, cron_name)
            asset_crontab_obj.save()
            task = update_asset_crontabs_tasks.delay(host_id=asset_id, tasks_name=task_name, cron_id=cron_id,
                                                     status=status)
            data = {"task": task.id}
        else:
            data = {'msg': 'nothing change'}
        return api_response(code=200, data=data)
