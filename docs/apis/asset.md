**资产相关接口**

# 获取资产列表(Get Assets list)
### URL
/api/v1.0/assets
### method
GET
### params
参数名 | 类型 | 必填 | 说明
---|---|---|---
name | varchar | 否 | 资产名称,模糊查询
ip | varchar | 否 | 资产ip
user_id | int| 否 | user id
port | int| 否 | 资产port
create_start | varchar | 否 | 创建时间起
create_end | varchar | 否 | 创建时间止
reverse | varchar | 否 | 是否按照创建时间倒序，0或者1
page| int | 否 | 页码，默认1
per_page| int | 否 | 每页个数，默认10

### 返回数据 (Response)
```
{
    "code": 200,
    "data": {
        "value": [
            {
                "id": 3,
                "name": "test2",
                "ip": "127.0.0.1",
                "port": 22,
                "user_id": 1,
                "gmt_created": "2019-06-18 03:20:40",
                "gmt_modified": "2019-06-18 03:20:40"
            }
        ],
        "per_page": 1,
        "page": 1,
        "total": 3
    }
}
```

# 新建资产(Create Asset)
### URL
/api/v1.0/assets
### method
POST
### 请求参数 (Post)
参数名 | 类型 | 必填 | 说明
---|---|---|---
name | varchar | 是 | 资产名称,模糊查询
ip | varchar | 是 | 资产ip
user_id | int| 是 | user id
port | int| 是 | 资产port
### 返回数据 (Response)
```
{
    "code": 200,
    "data": {
        "name": "test2",
        "ip": "127.0.0.2",
        "port": 22,
        "user_id": 1,
        "id": 5
    }
}
```

# 获取资产详情 (Get Asset Detail)
### URL
/api/v1.0/asset/{asset_id}

### method
GET

### 请求参数 (body)
参数名 | 类型 | 必填 | 说明
---|---|---|---
asset_id | int | 是 | 资产id

### 返回数据 (Response)
```
{
    "code": 200,
    "data": {
        "id": 1,
        "hostname": "opsa-uat",
        "ip": "10.20.3.101",
        "port": 22,
        "user_info": {
            "username": "root"
        },
        "is_deleted": false,
        "gmt_created": "2019-06-17 05:35:25",
        "gmt_modified": "2019-06-17 05:35:25"
    }
}
```

# 处理资产 (Post Asset)
### URL
api/v1.0/asset/{asset_id}
### method
patch
### 请求参数 (Body)
参数名 | 类型 | 必填 | 说明
---|---|---|---
asset_id| int| 是| 资产id
name | varchar | 是 | 资产名称,模糊查询
ip | varchar | 是 | 资产ip
user_id | int| 是 | user id
port | int| 是 | 资产port

### 返回数据 (Response)
```
{
    "code": 200,
    "data": {
        "hostname": "opsa-uat2",
        "ip": "10.20.3.101",
        "user_id": 1,
        "port": 22
    }
}
```

# 获取资产用户列表
### URL
/api/v1.0/assets/users
### method
GET
### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
name | varchar | 否 | 资产名称,模糊查询
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
                "id": 1,
                "name": "root",
                "gmt_created": "2019-06-17 02:38:08",
                "gmt_modified": "2019-06-17 05:35:39"
            }
        ],
        "per_page": 10,
        "page": 1,
        "total": 1
    }
}
```

# 新建资产用户
### URL
/api/v1.0/assets/users
### method
POST
### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
hostname | varchar | 是 | 主机名称
password | varchar| 是 | 主机密码
### 返回数据
```
{
    "code": 200,
    "data": {
        "name": "it",
        "password": 123456
    }
}
```

# 获取资产用户详情
### URL
/api/v1.0/assest/users/{user_id}

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
        "name": "it",
        "password": 123456
    }
}
```

# 处理资产用户
### URL
api/v1.0/assets/users/{asset_id}
### method
patch
### 请求参数
参数名 | 类型 | 必填 | 说明
---|---|---|---
asset_id| int| 是| 资产id
username | varchar | 否 | 用户名
password | varchar | 否 | 用户密码

### 返回数据
```
{
    "code": 200,
    "data": {
        "username": "root2",
        "is_deleted": false,
        "gmt_created": "2019-06-17 02:38:08",
        "gmt_modified": "2019-06-18 07:06:57"
    }
}
```