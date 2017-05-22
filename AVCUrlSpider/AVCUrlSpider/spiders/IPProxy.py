# -*-coding: utf-8-*-
from selenium import webdriver
import  re
import requests
import os
import datetime
import  urllib
import  redis
import  json

# 取代理Ip服务器
rconnection_Proxy = redis.Redis(host='117.122.192.50', port=6479, db=0)
# 代理IP
redis_key_proxy = "proxy:iplist"



class ProxyIP:

    def IPP(self):

        proxy1 = rconnection_Proxy.srandmember(redis_key_proxy)
        proxyjson = json.loads(proxy1)
        proxiip = proxyjson["ip"]
        return proxiip
    def session(self):
        # 随机取IP
        proxy1 = rconnection_Proxy.srandmember(redis_key_proxy)
        proxyjson = json.loads(proxy1)
        proxiip = proxyjson["ip"]
        sesson = requests.session()
        sesson.proxies = {'http': 'http://' + proxiip, 'https': 'https://' + proxiip}
        return sesson





