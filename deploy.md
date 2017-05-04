一、换源

1、删除RHEL原有的yum

rpm -aq|grep yum|xargs rpm -e --nodeps  #删除

2、下载新的yum安装包  #这里我们使用CentOS的yum源

wget http://vault.centos.org/6.0/os/x86_64/Packages/python-iniparse-0.3.1-2.1.el6.noarch.rpm
wget http://vault.centos.org/6.0/os/x86_64/Packages/yum-metadata-parser-1.1.2-14.1.el6.x86_64.rpm
wget http://vault.centos.org/6.0/os/x86_64/Packages/yum-3.2.27-14.el6.centos.noarch.rpm
wget http://vault.centos.org/6.0/os/x86_64/Packages/yum-plugin-fastestmirror-1.1.26-11.el6.noarch.rpm

3、安装yum软件包

rpm -ivh  python-iniparse-0.3.1-2.1.el6.noarch.rpm
rpm -ivh  yum-metadata-parser-1.1.2-14.1.el6.i686.rpm
rpm -ivh  yum-3.2.27-14.el6.centos.noarch.rpm yum-plugin-fastestmirror-1.1.26-11.el6.noarch.rpm
  
注意：最后两个安装包要放在一起同时安装，否则会提示相互依赖，安装失败。
4、更改yum源  #我们使用网易的CentOS镜像源
cd /etc/yum.repos.d/
wget  http://mirrors.163.com/.help/CentOS6-Base-163.repo
vim CentOS6-Base-163.repo

# CentOS-Base.repo
#
# The mirror system uses the connecting IP address of the client and the
# update status of each mirror to pick mirrors that are updated to and
# geographically close to the client.  You should use this for CentOS updates
# unless you are manually picking other mirrors.
#
# If the mirrorlist= does not work for you, as a fall back you can try the
# remarked out baseurl= line instead.
#
#

[base]
name=CentOS-6 - Base - 163.com
baseurl=http://mirrors.163.com/centos/6/os/$basearch/
#mirrorlist=http://mirrorlist.centos.org/?release=6&arch=$basearch&repo=os
gpgcheck=1
gpgkey=http://mirror.centos.org/centos/RPM-GPG-KEY-CentOS-6

#released updates
[updates]
name=CentOS-6 - Updates - 163.com
baseurl=http://mirrors.163.com/centos/6/updates/$basearch/
#mirrorlist=http://mirrorlist.centos.org/?release=6&arch=$basearch&repo=updates
gpgcheck=1
gpgkey=http://mirror.centos.org/centos/RPM-GPG-KEY-CentOS-6

#additional packages that may be useful
[extras]
name=CentOS-6 - Extras - 163.com
baseurl=http://mirrors.163.com/centos/6/extras/$basearch/
#mirrorlist=http://mirrorlist.centos.org/?release=6&arch=$basearch&repo=extras
gpgcheck=1
gpgkey=http://mirror.centos.org/centos/RPM-GPG-KEY-CentOS-6

#additional packages that extend functionality of existing packages
[centosplus]
name=CentOS-6 - Plus - 163.com
baseurl=http://mirrors.163.com/centos/6/centosplus/$basearch/
#mirrorlist=http://mirrorlist.centos.org/?release=6&arch=$basearch&repo=centosplus
gpgcheck=1
enabled=0
gpgkey=http://mirror.centos.org/centos/RPM-GPG-KEY-CentOS-6

#contrib - packages by Centos Users
[contrib]
name=CentOS-6 - Contrib - 163.com
baseurl=http://mirrors.163.com/centos/6/contrib/$basearch/
#mirrorlist=http://mirrorlist.centos.org/?release=6&arch=$basearch&repo=contrib
gpgcheck=1
enabled=0
gpgkey=http://mirror.centos.org/centos/RPM-GPG-KEY-CentOS-65

yum clean all    #清理yum缓存
yum makecache    #将服务器上的软件包信息缓存到本地,以提高搜索安装软件的速度
yum install vim*  #测试yum是否可用

二、安装gcc,openssl

yum -y install gcc
yum install openssl
yum install openssl-devel

三、查看python的版本
python  -V

wget https://www.python.org/ftp/python/2.7.6/Python-2.7.6.tgz
tar -xvf Python-2.7.6.tgz

cd Python-2.7.6

修改编辑Modules/Setup.dist文件，将
#zlib zlibmodule.c -I$(prefix)/include -L$(exec_prefix)/lib -lz

和
# Socket module helper for socket(2)
_socket socketmodule.c timemodule.c

# Socket module helper for SSL support; you must comment out the other
# socket line above, and possibly edit the SSL variable:
SSL=/usr/local/openssl
_ssl _ssl.c \
        -DUSE_SSL -I$(SSL)/include -I$(SSL)/include/openssl \
        -L$(SSL)/lib -lssl -lcrypto

取消注释
./configure --prefix=/usr/local/python2.7
make all
make install
make clean
make distclean

查看安装后python版本
/usr/local/python2.7/bin/python2.7 -V

建立软连接
mv /usr/bin/python /usr/bin/python2.6.6
ln -s /usr/local/python2.7/bin/python2.7 /usr/bin/python 

重新检验Python 版本
python -V

vim /usr/bin/yum

# 修改 python 指向
#!/usr/bin/python2.6.6

安装 pip

1.1 pip下载
yum -y install zlib* 

wget https://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg  --no-check-certificate
chmod +x setuptools-0.6c11-py2.7.egg
sh setuptools-0.6c11-py2.7.egg

wget "https://pypi.python.org/packages/source/p/pip/pip-1.5.4.tar.gz#md5=834b2904f92d46aaa333267fb1c922bb" --no-check-certificate

tar -xzvf pip-1.5.4.tar.gz
cd pip-1.5.4
python setup.py install

1.2 mysql安装
yum install mysql-server mysql mysql-devel

wget https://pypi.python.org/packages/a5/e9/51b544da85a36a68debe7a7091f068d802fc515a3a202652828c73453cad/MySQL-python-1.2.5.zip#md5=654f75b302db6ed8dc5a898c625e030c --no-check-certificate

unzip MySQL-python-1.2.5.zip
cd MySQL-python-1.2.5
python setup.py install

yum -y install gcc-c++ lapack-devel libicu-devel texinfo-tex

pip install django==1.8.4 django-bootstrap3 django-permanent plotly numpy scipy xlrd simplejson django-celery django_crontab

service mysqld start

python manage.py migrate

mysql -u root

source Dump20170417.sql

exit

service iptables stop
nohup python manage.py runserver 0.0.0.0:8000 &
