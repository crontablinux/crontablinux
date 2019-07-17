# Each instruction creates a new layer of the image.
FROM ubuntu:16.04

WORKDIR /ops/crontablinux
COPY . .
ENV LANG='C.UTF-8' LC_ALL='C.UTF-8' TZ='Asia/Shanghai'
RUN printf "nameserver 8.8.8.8\nnameserver 8.8.4.4\nnameserver 114.114.114.114\n" > /etc/resolv.conf \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && find . -name '*.pyc' -exec rm {} \; \
    && sed -i s@archive.ubuntu.com@mirrors.aliyun.com@g /etc/apt/sources.list \
    && sed -i s@us.archive.ubuntu.com@mirrors.aliyun.com@g /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    iputils-ping \
    python3 \
    python3-pip \
    libffi6 \
    libffi-dev \
    aria2 \
    xz-utils \
    gcc \
    python3-dev \
    python3-setuptools \
    libmysqlclient20 \
    libmysqlclient-dev \
    libjpeg8-dev \
    libjpeg8 \
    libfreetype6-dev \
    libfreetype6 \
    && apt-get -y install $(cat requirements/deb_requirements.txt) \
    && apt-get -y -o Dpkg::Options::="--force-confmiss" install --reinstall netbase \
    && pip3 install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements/requirement.txt \
    && python3 -m compileall -b . \
    && find ./apps -name '*.py' -exec rm {} \; \
    && find . -name "pycache" |xargs rm -rf \
    && apt-get purge -y \
    libffi-dev \
    aria2 \
    xz-utils \
    gcc \
    python3-dev \
    libmysqlclient-dev \
    libjpeg8-dev \
    libfreetype6-dev \
    && apt-get purge --auto-remove -y \
    && apt-get autoclean -y \
    && rm -rf /var/lib/apt/lists/* \
    && cp config_example.py config.py \
    && export PYTHONPATH=${PYTHONPATH}:/ops/crontablinux

# RUN python3 manage.py makemigrations
# RUN python3 manage.py migrate
# RUN python3 createsuperuser.py

EXPOSE 8000
VOLUME /ops/crontablinux
CMD ["/usr/bin/python3", "cron.py", "start", "gunicorn"]
