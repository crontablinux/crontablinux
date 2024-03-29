import os
import sys
import time
import signal
import threading
import argparse
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
COMMON_DIR = os.path.join(BASE_DIR, 'common')


all_services = ['gunicorn', 'celery']


try:
    from config import Config as CONFIG
except ImportError:
    print("Could not find config file, 'cp config_example.py config.py'")
    # quit with error
    sys.exit(1)


try:
    os.makedirs(os.path.join(BASE_DIR, "data", "logs"))
    os.makedirs(os.path.join(BASE_DIR, "tmp"))
except:
    pass

os.environ["PYTHONIOENCODING"] = "UTF-8"
HTTP_HOST = CONFIG.HTTP_BIND_HOST or '127.0.0.1'
HTTP_PORT = CONFIG.HTTP_LISTEN_PORT or 8080
LOG_LEVEL = CONFIG.LOG_LEVEL
LOG_DIR = os.path.join(BASE_DIR, "data", "logs")
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
DEBUG = CONFIG.DEBUG or False
START_TIMEOUT = 15
WORKERS = 4
DAEMON = False


def check_database_connection():
    for i in range(60):
        print("Check database connection ...")
        code = subprocess.call("/usr/bin/python3 manage.py showmigrations", shell=True)
        if code == 0:
            print("Database connect success")
            return
        time.sleep(1)
    print("Connection database failed, exist")
    sys.exit(10)


def make_migrations():
    print("Check database structure change ...")
    subprocess.call('/usr/bin/python3 manage.py makemigrations', shell=True)
    print("Migrate model change to database ...")
    subprocess.call('/usr/bin/python3 manage.py migrate', shell=True)


def prepare():
    check_database_connection()
    make_migrations()


def parse_services(service):
    if service == 'all':
        return all_services
    else:
        return [service]


def get_pid_file_path(service):
    return os.path.join(TMP_DIR, '{}.pid'.format(service))


def get_log_file_path(service):
    return os.path.join(LOG_DIR, '{}.log'.format(service))


def get_pid(service):
    pid_file = get_pid_file_path(service)
    if os.path.isfile(pid_file):
        with open(pid_file) as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
    return 0


def check_pid(pid):
    """ Check for the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def is_running(service, unlink=True):
    pid_file = get_pid_file_path(service)

    if os.path.isfile(pid_file):
        with open(pid_file, 'r') as f:
            pid = get_pid(service)
            if check_pid(pid):
                return True

            if unlink:
                os.unlink(pid_file)
    return False


def start_gunicorn():
    print("\n- Start Api Export Server")
    prepare()
    service = 'gunicorn'
    bind = '{}:{}'.format(HTTP_HOST, HTTP_PORT)
    pid_file = get_pid_file_path(service)
    log_file = get_log_file_path(service)
    log_format = '%(h)s %(t)s "%(r)s" %(s)s %(b)s '

    cmd = [
        'gunicorn', 'crontablinux.wsgi',
        '-b', bind,
        '-k', 'gthread',
        '--threads', '10',
        '-w', str(WORKERS),
        '--max-requests', '4096',
        '--access-logformat', log_format,
        '-p', pid_file,
    ]

    if DAEMON:
        cmd.extend([
            '--access-logfile', log_file,
            '--daemon',
        ])
    else:
        cmd.extend([
            '--access-logfile', '-'
        ])

    if DEBUG:
        cmd.append('--reload')
    p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    return p


def start_celery():
    print("\n- Start Celery as Distributed Task Queue")
    # To do: Must set this environment, otherwise not no ansible result return
    os.environ.setdefault('PYTHONOPTIMIZE', '1')

    if os.getuid() == 0:
        os.environ.setdefault('C_FORCE_ROOT', '1')

    service = 'celery'
    pid_file = get_pid_file_path(service)

    cmd = [
        'celery', 'worker',
        '-A', 'tasks',
        '-l', LOG_LEVEL.lower(),
        '--pidfile', pid_file,
        '--autoscale', '20,4',
    ]

    if DAEMON:
        cmd.extend([
            '--logfile', os.path.join(LOG_DIR, 'celery.log'),
            '--detach',
        ])
    p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    return p


def start_service(serices):
    print(time.ctime())

    serices_handler = {
        'gunicorn': start_gunicorn,
        'celery': start_celery,
    }

    services_set = parse_services(serices)
    processes = []
    for i in services_set:
        if is_running(i):
            show_service_status(i)
            continue
        func = serices_handler.get(i)
        p = func()
        processes.append(p)

    now = int(time.time())
    for i in services_set:
        while not is_running(i):
            if int(time.time()) - now < START_TIMEOUT:
                time.sleep(1)
                continue
            else:
                print("Error: {} start error".format(i))
                stop_multi_services(services_set)
                return

    stop_event = threading.Event()

    if not DAEMON:
        signal.signal(signal.SIGTERM, lambda x, y: stop_event.set())
        while not stop_event.is_set():
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                stop_event.set()
                break

        print("Stop services")
        for p in processes:
            p.terminate()

        for i in services_set:
            stop_service(i)
    else:
        print()
        show_service_status(serices)


def show_service_status(service):
    service_set = parse_services(service)
    for ns in service_set:
        if is_running(ns):
            pid = get_pid(ns)
            print("{} is running: {}".format(ns, pid))
        else:
            print("{} is stopped".format(ns))


def stop_multi_services(services):
    for s in services:
        stop_service(s, sig=9)


def stop_service(s, sig=15):
    services_set = parse_services(s)
    for s in services_set:
        if not is_running(s):
            show_service_status(s)
            continue
        print("Stop service: {}".format(s))
        pid = get_pid(s)
        os.kill(pid, sig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
            opsa service control tools;
            Exmaple: \r\n
            %(prog)s start all -d
        """)
    parser.add_argument(
        'action', type=str, choices=("start", "stop", "restart", "status"), help="Action to run"
    )
    parser.add_argument(
        'service', type=str, default="all", nargs="?", choices=("all", "gunicorn", "celery"),
        help="The service to start",
    )
    parser.add_argument('-d', '--daemon', nargs="?", const=1)
    parser.add_argument('-w', '--worker', type=int, nargs="?", const=4)

    args = parser.parse_args()
    if args.daemon:
        DAEMON = True

    if args.worker:
        WORKERS = args.worker

    action = args.action
    srv = args.service

    if action == "start":
        start_service(srv)
    elif action == "stop":
        stop_service(srv)
    elif action == "restart":
        DAEMON = True
        stop_service(srv)
        time.sleep(5)
        start_service(srv)
    else:
        show_service_status(srv)