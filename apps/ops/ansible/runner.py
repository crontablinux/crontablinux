import os
from collections import namedtuple
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.playbook.play import Play
import ansible.constants as C

from apps.ops.ansible.callback import AdHocResultCallback
from apps.ops.ansible.exceptions import AnsibleError

C.HOST_KEY_CHECKING = False
Options = namedtuple('Options', [
    'listtags', 'listtasks', 'listhosts', 'syntax', 'connection',
    'module_path', 'forks', 'remote_user', 'private_key_file', 'timeout',
    'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
    'scp_extra_args', 'become', 'become_method', 'become_user',
    'verbosity', 'check', 'extra_vars', 'playbook_path', 'passwords',
    'diff', 'gathering', 'remote_tmp',
])


def get_default_options():
    options = Options(
        listtags=False,
        listtasks=False,
        listhosts=False,
        syntax=False,
        timeout=30,
        connection='ssh',
        module_path='',
        forks=10,
        remote_user='root',
        private_key_file=None,
        ssh_common_args="",
        ssh_extra_args="",
        sftp_extra_args="",
        scp_extra_args="",
        become=None,
        become_method=None,
        become_user=None,
        verbosity=None,
        extra_vars=[],
        check=False,
        playbook_path='/etc/ansible/',
        passwords=None,
        diff=False,
        gathering='implicit',
        remote_tmp='/tmp/.ansible'
    )
    return options


class AdHocRunner:
    """
    ADHoc Runner 接口
    """
    results_callback_class = AdHocResultCallback
    results_callback = None
    loader_class = DataLoader
    variable_manager_class = VariableManager
    options = get_default_options()

    def __init__(self, inventory=None, options=None):
        """
        :param inventory: like ansible.cfg
        :param options: like inventory
        """
        if options:
            self.options = options
        C.RETRY_FILES_ENABLED = False
        self.inventory = inventory
        self.loader = self.loader_class()
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)

    def get_result_callback(self):
        return self.__class__.results_callback_class()

    def check_pattern(self, pattern):
        if not pattern:
            raise AnsibleError("Pattern {} is not valid".format(pattern))
        if not self.inventory.list_hosts('all'):
            raise AnsibleError("Inventory is empty.")
        if not self.inventory.list_hosts(pattern):
            raise AnsibleError(
                "pattern: %s  dose not match any hosts." % pattern
            )

    @staticmethod
    def check_module_args(module_name, module_args=''):
        if module_name in C.MODULE_REQUIRE_ARGS and not module_args:
            err = "No argument passed to {} module".format(module_name)
            raise AnsibleError(err)

    def clean_tasks(self, tasks):
        cleaned_tasks = []
        for task in tasks:
            self.check_module_args(task['action']['module'], task['action']['args'])
            cleaned_tasks.append(task)
        return cleaned_tasks

    def run(self, tasks, pattern, play_name="Ansible Ad-hoc", gather_facts='no', file_obj=None):
        """
        :param tasks: [{'action': {'module': 'shell', 'args': 'ls'}, ...}, ]
        :param pattern: all, *, other
        :param play_name: The play name
        :param gather_facts:
        :param file_obj:
        :return:
        """
        self.check_pattern(pattern)
        self.results_callback = self.get_result_callback()
        cleaned_tasks = self.clean_tasks(tasks)

        play_source = dict(
            name=play_name,
            hosts=pattern,
            gather_facts=gather_facts,
            tasks=cleaned_tasks
        )

        play = Play().load(
            play_source,
            variable_manager=self.variable_manager,
            loader=self.loader
        )

        tqm = TaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            stdout_callback=self.results_callback,
            passwords=self.options.passwords
        )

        print("Get matched hosts: {}".format(
            self.inventory.get_matched_hosts(pattern)
        ))

        try:
            tqm.run(play)
            return self.results_callback
        except Exception as e:
            raise AnsibleError(e)
        finally:
            tqm.cleanup()
            self.loader.cleanup_all_tmp_files()
