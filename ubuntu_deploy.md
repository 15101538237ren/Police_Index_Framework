
前提 gcc,build-essential, pip已装,numpy, python 版本2.7.6

1.安装dependencies

sudo apt-get install libssl-dev libssl0.9.8 mysql-server libmysqld-dev libmysqlclient-dev

2.MySQL-python

wget https://pypi.python.org/packages/a5/e9/51b544da85a36a68debe7a7091f068d802fc515a3a202652828c73453cad/MySQL-python-1.2.5.zip#md5=654f75b302db6ed8dc5a898c625e030c --no-check-certificate

unzip MySQL-python-1.2.5.zip
cd MySQL-python-1.2.5
python setup.py install

3.
sudo apt-get install Python-scipy python-numpy python-matplotlib

4.
pip install django==1.8.4 django-bootstrap3 django-permanent plotly xlrd

5.
sudo service mysql start

mysql -uroot