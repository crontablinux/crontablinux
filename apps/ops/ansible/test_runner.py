from inventory import BaseInventory
from runner import AdHocRunner


host_data = [
    {
        "hostname": "testserver",
        "ip": "10.20.15.105",
        "port": 22,
        "username": "root",
        "password": "Sdftd11",
    }
]
inventory = BaseInventory(host_data)
runner = AdHocRunner(inventory)
tasks = [
    {"action": {"module": "shell", "args": "ls"}, "name": "run_cmd"},
    {"action": {"module": "shell", "args": "whoami"}, "name": "run_whoami"},
]
ret = runner.run(tasks, "all")
