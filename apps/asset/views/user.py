import json
from django.shortcuts import render
from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.asset.models import AssetUser
from apps.common.format_response import api_response
# Create your views here.


class AssetUserListView(View):
    def get(self, request, *args, **kwargs):
        """
        获取资产用户列表
        :return:
        """
        request_data = request.GET
        name = request_data.get('username', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))

        msg = ''
        query_params = Q(is_deleted=False)
        if name:
            query_params &= Q(name__startwith=name)
        if create_start:
            query_params &= Q(gmt_created__gte=create_start)
        if create_end:
            query_params &= Q(gmt_created__lte=create_end)

        if reverse:
            order_by_str = '-gmt_created'
        else:
            order_by_str = 'gmt_created'

        user_objects = AssetUser.objects.filter(query_params).order_by(order_by_str)
        paginator = Paginator(user_objects, per_page)

        try:
            user_paginator = paginator.page(page)
        except PageNotAnInteger:
            user_paginator = paginator.page(1)
            msg = 'Page is not Integer'
        except EmptyPage:
            user_paginator = paginator.page(paginator.num_pages)
            msg = 'Page is Empty'

        user_result_object_list = user_paginator.object_list
        user_result_restful_list = []
        for user_result_object in user_result_object_list:
            user_result_restful_list.append(dict(id=user_result_object.id,
                                                 name=user_result_object.name,
                                                 gmt_created = str(user_result_object.gmt_created)[:19],
                                                 gmt_modified = str(user_result_object.gmt_modified)[:19],
                                                 ))
        data = dict(value=user_result_restful_list, per_page=per_page, page=page, total=paginator.count)
        if msg:
            return api_response(code=200, msg=msg, data=data)
        else:
            return api_response(code=200, data=data)

    def post(self, request, *args, **kwargs):
        """
        create asset user
        """
        json_str = request.body.decode('utf-8')
        if not json_str:
            return api_response(code=201, msg='post args is empty', data={})

        request_data_dict = json.loads(json_str)

        msg = ''
        name = request_data_dict.get('hostname', '')
        pwd = request_data_dict.get('password', '')

        if not name:
            msg = 'pls input hostname'
        elif not pwd:
            msg = 'pls input password'
        elif AssetUser.objects.filter(name=name, is_deleted=False).exists():
            msg = 'AssetUser name: {} already exist'.format(name)

        if msg:
            return api_response(code=201, msg=msg, data={})

        data = dict(name=name, password=pwd)
        new_asset = AssetUser(**data)
        new_asset.save()

        return api_response(code=200, data=data)


class AssetUserView(View):
    def get(self, request, *args, **kwargs):
        """
        Get Asset Detail
        """
        request_data = request.GET
        user_id = kwargs.get('user_id')
        msg = ''

        user_query = AssetUser.objects.filter(pk=user_id)

        if not user_query.exists():
            msg = 'asset not exists'
            return api_response(code=201, msg=msg, data={})

        user_obj = user_query[0]

        data = dict(id=user_obj.id, username=user_obj.name, is_deleted=user_obj.is_deleted,
                    gmt_created=str(user_obj.gmt_created)[:19], gmt_modified=str(user_obj.gmt_modified)[:19])

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
        user_id = kwargs.get('user_id')

        user_query = AssetUser.objects.filter(pk=user_id)
        if not user_query.exists():
            msg = 'asset not exists'
            return api_response(code=201, msg=msg, data={})

        user_obj = user_query[0]

        name = request_data_dict.get('username', '')
        pwd = request_data_dict.get('password', '')

        if name and user_obj.name != name:
            user_obj.name = name
            update = True
        if pwd and user_obj.password != pwd:
            user_obj.password = pwd
            update = True

        if update:
            user_obj.save()

        data = dict(username=user_obj.name, password=user_obj.password, is_deleted=user_obj.is_deleted,
                    gmt_created=str(user_obj.gmt_created)[:19], gmt_modified=str(user_obj.gmt_modified)[:19])
        return api_response(code=200, data=data)
