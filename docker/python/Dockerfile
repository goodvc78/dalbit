FROM centos:7 

# 메인테이너 정보 (옵션)
MAINTAINER goodvc <goodvc78@gmail.com>

# 환경변수 설정 (옵션)
ENV PATH /usr/local/bin:/usr/bin:$PATH

RUN yum clean all && yum update -y && yum upgrade -y && \
    yum install -y nano vi which curl git make wget unzip sudo ansible build-essential gcc gcc-c++ snappy-devel zlib-devel python python-devel python-pip && \
    yum install -y autoconf automake bison flex gperf libtool libtool-ltdl-devel m4 perl ncurses-devel texinfo && \
    yum install -y ruby ruby-devel lua lua-devel luajit luajit-devel tcl-devel perl perl-devel perl-ExtUtils-ParseXS perl-ExtUtils-XSpp perl-ExtUtils-CBuilder perl-ExtUtils-Embed && \
    yum install -y ctags the_silver_searcher && \
    yum install -y gitflow python36-devel python36-pip && \
    yum install -y mysql-devel

RUN pip3.6 install --ignore-installed --upgrade pip setuptools six supervisor psutil flake8 jedi
# RUN unlink /bin/python && \
# 	ln -s /bin/python3.6 /bin/python && \
# 	ln -s /bin/pip3.6 /bin/pip

COPY requirements.txt /requirements.txt
RUN pip3 install --upgrade pip \
    && pip3 install -r requirements.txt \
    && rm /usr/bin/mysql*
COPY uwsgi.ini /uwsgi.ini

CMD ["uwsgi", "--ini", "/uwsgi.ini"]
