## 1 环境搭建(CentOS7)
### 1.1 安装python和Git
请自行安装python3.6和Git。
使用Git拉取代码： 
```
git clone https://github.com/evobstore/webserver.git
```
### 1.2 安装python虚拟环境和包管理工具pipenv
使用pip命令安装pipenv。  
```pip3 install pipenv```
### 1.3  使用pipenv搭建python虚拟环境
在代码工程根目录下，即文件Pipfile同目录下运行命令：  
```pipenv install```
### 1.4 数据库安装
请自行安装mysql数据库。
根据自己的情况修改webserver/settings.py文件中有关数据库的配置示例代码
```
# Mysql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
        'NAME': 'xxx',       # 数据的库名，事先要创建之
        'HOST': 'localhost',    # 主机
        'PORT': '3306',         # 数据库使用的端口
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
    },
    'metadata': {
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'NAME': 'metadata',  # 数据的库名，事先要创建之
        'USER': 'xxx',  # 数据库用户名
        'PASSWORD': 'xxx',  # 密码
        'HOST': '127.0.0.1',  # 主机
        'PORT': '3306',  # 数据库使用的端口
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
    },
}
```
### 1.5 ceph配置和依赖库安装
与ceph的通信默认使用官方librados的python包python36-rados，python36-rados的rpm包安装成功后，python包会自动安装到
系统python3第三方扩展包路径下（/usr/lib64/python3.6/site-packages/），然后需要把路径下的python包文
件rados-2.0.0-py3.6.egg-info和rados.cpython-36m-x86_64-linux-gnu.so复制到你的虚拟python环境*/site-packages/下。
```
wget http://download.ceph.com/rpm-nautilus/el7/x86_64/librados2-14.2.1-0.el7.x86_64.rpm
wget http://download.ceph.com/rpm-nautilus/el7/x86_64/python36-rados-14.2.1-0.el7.x86_64.rpm
yum localinstall -y librados2-14.2.1-0.el7.x86_64.rpm python36-rados-14.2.1-0.el7.x86_64.rpm
```
ceph的配置：   
```
CEPH_RADOS = {
    'CLUSTER_NAME': 'ceph',
    'USER_NAME': 'client.objstore',
    'CONF_FILE_PATH': '/etc/ceph/ceph.conf',
    'KEYRING_FILE_PATH': '/etc/ceph/ceph.client.admin.keyring',
    'POOL_NAME': ('poolname1', 'poolname1'),
}
```

### 1.6 security_settings.py
在settings.py文件最后导入了security_settings.py（项目中缺少），security_settings.py中定义了一些安全敏感信息，请自行添加此文件，并根据自己情况参考settings.py中例子完成配置。

## 2 运行webserver
### 2.1 激活python虚拟环境  
```pipenv shell```
### 2.2 数据库迁移
django用户管理、验证、session等使用mysql(sqlite3)数据库，需要数据库迁移创建对应的数据库表,在项目根目录下运行如下命令完成数据库迁移。  
```
python manage.py migrate
```
### 2.3 运行web服务
在代码工程根目录下，即文件Pipfile同目录下运行命令：  
```python manage.py runserver 0.0.0.0:8000```   
如果一切正常，打开浏览器输入url(主机IP:8000, 如：127.0.0.1：8000)即可查看站点;
### 2.4 开机自启服务
移动iharbor.service、iharbor_ftp.service两个文件到 /usr/lib/systemd/system/ 目录下
```
systemctl daemon-reload
systemctl enable iharbor
systemctl enable iharbor_ftp
```


