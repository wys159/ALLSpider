# -*- coding: UTF-8 -*-
# Created by dev on 16-5-27.

import random, time
import redis, json

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.utils.project import get_project_settings
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
#from spiders import config
import traceback
# proxy_key = config.REDIS_DATA['PROXY_KEY']
# REDIS_HOST = config.REDIS_DATA['YZ_HOST']
# REDIS_PORT = config.REDIS_DATA['YZ_PORT']
# 取代理Ip服务器
rconnection_Proxy = redis.Redis(host='117.122.192.50', port=6479, db=0)
# REDIS_PORT=6479
# REDIS_HOST="host='117.122.192.50'"
# 代理IP
proxy_key = "proxy:iplist"

class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        if ua:
            request.headers.setdefault('User-Agent', ua)

    # the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    # for more user agent strings,you can find it in http://www.useragentstring.com/pages/useragentstring.php
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]


class ProxyMiddleware(object):
    settings = get_project_settings()
    while 1:
        try:
            #redisclient = redis.Redis(REDIS_HOST, REDIS_PORT)
            redisclient=rconnection_Proxy
            DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)
            break
        except Exception, error:
            print "redis connect error : {0}".format(error)
            time.sleep(60)

    def process_request(self, request, spider):
        """
        将request设置为使用代理
        """
        try:
            #self.redisclient = redis.Redis(REDIS_HOST,REDIS_PORT)
            self.redisclient = rconnection_Proxy
            proxy = self.redisclient.srandmember(proxy_key)
            proxyjson = json.loads(proxy)
            ip = proxyjson["ip"]
            request.meta['proxy'] = "http://%s" % ip if 'new_proxy' not in request.meta.keys() else request.meta['new_proxy']
            # request.meta['proxy'] = "http://117.70.174.212:44847"
            print '-' * 20
            print request.meta['proxy']
            print '-' * 20
        except Exception, ee:
            error_msg = traceback.format_exc()
            print error_msg
    def process_exception(self, request, exception, spider):
        """
        处理由于使用代理导致的连接异常 则重新换个代理继续请求
        """
        try:
            print 'error_type', exception.message
            # if isinstance(exception, self.DONT_RETRY_ERRORS):
            new_request = request.copy()
            try:
                #self.redisclient = redis.Redis(REDIS_HOST,REDIS_PORT)
                self.redisclient = rconnection_Proxy
                proxy = self.redisclient.srandmember(proxy_key)
                proxyjson = json.loads(proxy)
                ip = proxyjson["ip"]
                new_request.meta['new_proxy'] = "http://%s" % ip
            except:
                pass
            return new_request
            # else:
            #     print 'isinstance Error............'
        except Exception,e:
            error_msg = traceback.format_exc()
            print error_msg
