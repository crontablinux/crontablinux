from ansible.inventory.host import Host
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from apps.ops.ansible.exceptions import AnsibleError
from typing import List

from apps.asset.models import Asset, AssetUser


class BaseHost(Host):
    def __init__(self, host_data):
        """
        :param host_data: {"hostname": "", "ip": "", "port": "", "username": "", "password": ""}
        """
        self.host_data = host_data
        hostname = host_data.get('hostname') or host_data.get('ip')
        port = host_data.get('port') or 22
        super().__init__(hostname, port)
        self.__set_required_variables()

    def __set_required_variables(self):
        host_data = self.host_data
        self.set_variable('host_key_checking', False)
        self.set_variable('ansible_host', host_data['ip'])

        if not host_data.get('username'):
            raise AnsibleError('ansible host dont have hostname')

        self.set_variable('ansible_user', host_data['username'])

        if not host_data.get('password'):
            raise AnsibleError('ansible host dont have password')

        self.set_variable('ansible_ssh_pass', host_data['password'])

    def __repr__(self):
        return self.name


class BaseInventory(InventoryManager):
    """
    class for Ansible Inventory object
    """
    loader_class = DataLoader
    variable_manager_class = VariableManager
    host_manager_class = BaseHost

    def __init__(self, host_list=None):
        """
        :param host_list: [{"hostname": "", "ip": "", "port": "", "username": "", "password": ""}]
        """
        self.host_list = host_list or []
        self.host_len = len(host_list)
        assert isinstance(host_list, list)
        self.loader = self.loader_class()
        self.variable_manager = self.variable_manager_class()
        super().__init__(self.loader)

    def parse_host(self):
        for i in range(self.host_len):
            host_data = self.host_list[i]
            host = self.host_manager_class(host_data=host_data)
            self.hosts[host_data['hostname']] = host
            self.groups['ungrouped'].add_host(host)
            self.groups['all'].add_host(host)

    def parse_sources(self, cache=False):
        self.parse_host()

    def get_matched_hosts(self, pattern):
        return self.get_hosts(pattern)


class CrontabInventory(BaseInventory):
    """
        CrontabInventory set inventory with host id list
    """
    def __init__(self, host: List):
        self.host_list = []
        self.convert_to_ansible(host=host)
        host_list = self.host_list

        super().__init__(host_list=host_list)

    def convert_to_ansible(self, host: List):
        assets_query = Asset.objects.filter(pk__in=host)
        assets_len = assets_query.count()
        user_ids = list()
        host_list = self.host_list

        for i in range(assets_len):
            asset = assets_query[i]
            if asset.user_id not in user_ids:
                user_ids.append(asset.user_id)

        user_query = AssetUser.objects.filter(pk__in=user_ids)

        for i in range(assets_len):
            tmp = {}
            asset = assets_query[i]
            hostname = asset.name
            ip = asset.ip
            port = asset.port
            user_obj = user_query.get(pk=asset.user_id)
            username = user_obj.name
            password = user_obj.password
            tmp["hostname"] = hostname
            tmp["ip"] = ip
            tmp["port"] = port
            tmp["username"] = username
            tmp["password"] = password
            host_list.append(tmp)

        self.host_list = host_list








