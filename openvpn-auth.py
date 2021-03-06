#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,sys,time
import logging
import traceback
import django

logging.basicConfig(level=logging.WARNING, filename='/var/log/nginx/openvpn-auth.log', filemode='a')  # 'a'为追加模式,'w'为覆盖写

def return_auth_failed():
    sys.exit(1)  # 认证未通过

def return_auth_passed():
    sys.exit(0)  # 认证通过

try:
    # 将项目路径添加到系统搜寻路径当中，查找方式为从当前脚本开始，找到要调用的django项目的路径
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # 设置项目的配置文件 不做修改的话就是 settings 文件
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webserver.settings")
    django.setup()  # 加载项目配置
except Exception as e:
    msg = traceback.format_exc()
    logging.error(msg)
    return_auth_failed()

from django.contrib.auth import get_user_model

User = get_user_model()

def auth(username, raw_password):
    '''
    :param username:
    :param raw_password:
    :return:
        True -> auth passed
        False -> not passed
    '''
    # 验证用户
    try:
        user = User.objects.filter(username=username).first()
    except Exception as e:
        msg = traceback.format_exc()
        logging.error(msg)
        return False

    if not user:
        return False

    vpn = user.vpn_auth
    if vpn.check_password(raw_password):
        return True

    return False

if __name__ == '__main__':
    username = os.environ.get('username', None)
    password = os.environ.get('password', None)
    time_string = time.strftime( '%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    if username is None or password is None:
        logging.error(f'time: {time_string},error!username={username}, password={password}.')
        return_auth_failed()

    #logging.warning(f'username={username}, password={password}.')
    if not auth(username=username, raw_password=password):
        logging.warning(f'time: {time_string},auth failed.username={username}')
        return_auth_failed() # 认证未通过
    else:
        logging.warning(f'time: {time_string},auth OK!username={username}')
        return_auth_passed()
