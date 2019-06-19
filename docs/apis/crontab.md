# 获取Crontab列表
### URL
/api/v1.0/cron
### method
GET
### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
name | varchar | 否 | cron名称,模糊查询
job | varchar | 否 | job名称
create_start | varchar | 否 | 创建时间起
create_end | varchar | 否 | 创建时间止
reverse | varchar | 否 | 是否按照创建时间倒序，0或者1
page| int | 否 | 页码，默认1
per_page| int | 否 | 每页个数，默认10

### 返回数据
```
{
    "code": 200,
    "data": {
        "value": [
            {
                "id": 7,
                "name": "test6",
                "job": "ls /tmp2",
                "minute": "*/3",
                "hour": "*",
                "day": "*",
                "month": "*",
                "month_of_year": "*",
                "gmt_created": "2019-06-18 10:14:54",
                "gmt_modified": "2019-06-18 10:14:54"
            }
        ],
        "per_page": 1,
        "page": 1,
        "total": 6
    }
}
```

# 新建Crontab
### URL
/api/v1.0/cron
### method
POST
### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
name | varchar | yes | cron名称,模糊查询
job | varchar | yes | job名称
minute | varchar | no | 分钟
hour | varchar | no | 小时
day | varchar | no | 天
month | varchar | no | 月
week | varchar | no | 周
### 返回数据
```
Ansible_id:0 表示没有资产匹配
{
    "code": 200,
    "data": {
        "name": "test6",
        "job": "ls /tmp2",
        "minute": "*/3",
        "hour": "*",
        "day_of_month": "*",
        "month_of_year": "*",
        "day_of_week": "*",
        "ansible_id": 0
    }
}
```

# 获取Crontab详情
### URL
/api/v1.0/cron/{cron_id}

### method
GET

### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
user_id | int | 是 | 资产用户id

### 返回数据
```
{
    "code": 200,
    "data": {
        "id": 2,
        "crontab_name": "test2",
        "job": "ls /tmp",
        "minute": "*",
        "hour": "*",
        "day": "*",
        "month": "*",
        "week": "*",
        "is_deleted": true,
        "ansible_info": {
            "tasks": [
                {
                    "name": "test2",
                    "action": {
                        "module": "cron",
                        "args": "minute=* hour=* day=* weekday=* month=* name=\"test2\" job=\"ls /tmp\" state=absent"
                    }
                }
            ],
            "pattern": "all",
            "hosts": [
                1
            ]
        },
        "gmt_created": "2019-06-17 08:35:38",
        "gmt_modified": "2019-06-17 08:43:33"
    }
}
```

# 处理Crontab
### URL
api/v1.0/assets/users/{asset_id}
### method
patch
### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
name | varchar | yes | cron名称,模糊查询
job | varchar | yes | job名称
minute | varchar | no | 分钟
hour | varchar | no | 小时
day | varchar | no | 天
month | varchar | no | 月
week | varchar | no | 周

### 返回数据
```
{
    "code": 200,
    "data": {
        "id": 2,
        "crontab_name": "test234",
        "job": "ls /tmp",
        "minute": "*",
        "hour": "*",
        "day": "*",
        "month": "*",
        "week": "*",
        "is_deleted": true,
        "gmt_created": "2019-06-17 08:35:38",
        "gmt_modified": "2019-06-18 11:11:24"
    }
}
```

# 获取CrontabAsset列表
### URL
/api/v1.0/cron/assets
### method
GET
### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
is_deleted | bool | 否 | 是否删除
asset_id | int | 否 | 资产id
crontab_id | int | 否 | 计划任务id
create_start | varchar | 否 | 创建时间起
create_end | varchar | 否 | 创建时间止
reverse | varchar | 否 | 是否按照创建时间倒序，0或者1
page| int | 否 | 页码，默认1
per_page| int | 否 | 每页个数，默认10

### 返回数据
```
{
    "code": 200,
    "data": {
        "value": [
            {
                "id": 4,
                "asset_id": 3,
                "crontab_id": 1,
                "is_deleted": false,
                "gmt_created": "2019-06-19 03:43:52",
                "gmt_modified": "2019-06-19 03:43:52"
            }
        ],
        "per_page": 1,
        "page": 1,
        "total": 4
    }
}
```

# 新建CrontabAsset
### URL
/api/v1.0/cron/assets
### method
POST
### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
asset_id | int | 否 | 资产id
crontab_id | int | 否 | 计划任务id
### 返回数据
```
{
    "code": 200,
    "data": {
        "asset_id": 5,
        "crontab_id": 1
    }
}
```

# 获取CrontabAsset详情
### URL
/api/v1.0/cron/assets/{cron_asset_id}

### method
GET

### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
cron_asset_id | int | 是 | 资产计划任务关联id

### 返回数据
```
{
    "code": 200,
    "data": {
        "asset_id": 5,
        "crontab_id": 1
    }
}
```

# 处理CrontabAsset
### URL
api/v1.0/cron/assets/{asset_id}
### method
patch
### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
asset_id | int | 否 | 资产id
crontab_id | int | 否 | 计划任务id

### 返回数据
```
{
    "code": 200,
    "data": {
        "id": 1,
        "asset_id": 1,
        "crontab_id": 1,
        "is_deleted": false,
        "gmt_created": "2019-06-17 05:35:53",
        "gmt_modified": "2019-06-19 05:43:47"
    }
}
```