# -*- coding: utf-8 -*-

import scrapy
import re
import time
import  json
import threading
import traceback
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from AVCUrlSpider.items import  JDSpiderItem,JDSpiderPageItem
from AVCUrlSpider.spiders.SpiderModle import Modle
from scrapy_redis.spiders import RedisCrawlSpider
import sys
mutex = threading.Lock()
class ListSpider(RedisCrawlSpider):
    name = "AVCUrlSpider"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
    }
    redis_key = 'SNList:item'
    #redis_key = 'PageList:item'
    def make_requests_from_url(self, redis_data):
        #重redis中读取的数据，序列化
        data = json.loads(redis_data)
        url = data['URL']
        DS = data['URLWeb']
        Cateroy = data['Category']
        #pageNum=data['pageNum']
        l_data = {'urlpage': url, 'ec': DS, 'Caterry': Cateroy}
        try:
            if 'JD' in DS:
                return Request(url, callback=self.JDPage, headers=self.headers,dont_filter=True, meta=l_data)

            elif 'SN' in DS:
                return Request(url, callback=self.SNPage, headers=self.headers,dont_filter=True, meta=l_data)

            elif 'YMX' in DS:
                return Request(url, callback=self.YMXPage, headers=self.headers,dont_filter=True, meta=l_data)
            elif 'GM' in DS:
                return Request(url, callback=self.GMPage, headers=self.headers, dont_filter=True, meta=l_data)
            elif 'DD' in DS:
                return Request(url, callback=self.DDPage, headers=self.headers, dont_filter=True, meta=l_data)
            elif 'YHD' in DS:
                return Request(url, callback=self.YHDPage, headers=self.headers, dont_filter=True, meta=l_data)
        except Exception, e:
            print u"错识信息" + e.message
            print data
    #京东页面数
    def JDPage(self,response):
        index=0
        try:
            spurl = response.url
            plheaders = {"Referer": "" + spurl + ""}
            url=response.meta['urlpage']
            #获取页数
            html = response.body
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            #html = str(html).encode('utf-8')

            if html:
                NumPage = re.search(r'<span class="fp-text">[\s\S]*?<i>(\d+?)</i>', str(html), re.S).group(1).encode(
                    'utf-8')
                print NumPage
                if NumPage is None:
                    NumPage = str(0)
            #循环翻页
            #for i in range(1,int(NumPage)+1):
            for i in range(1, int(NumPage)+1):
                urlpage= url+'&page='+str(i)

                print  u'当前品类url:'+urlpage
                time.sleep(1)
                yield Request(urlpage, callback=self.JDUrlparse,headers=plheaders,dont_filter=True,  meta={'pageurl': urlpage, 'JDCaterry': response.meta['Caterry'],
                                        'ec': response.meta['ec']})

                #yield pageitem

        except Exception,e:
            print '可能连接超时，详情：'+e.message
    #京东URL
    def JDUrlparse(self, response):
        print '开始URl加工\033[0;31;0m Time：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            time.time())) + '\033[0m'
        try:

            spurl = response.url

            attrheaders = {"Referer": "" + spurl + ""}
            #time.sleep(1)
            pageurl=response.meta['pageurl']
            html = response.body
            # 判断当前页面编码格式
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            #html = str(html).encode('utf-8')
            # 第一步在取出页面内所有该品类的店铺的URL
            com = re.compile(
                r'<div class="p-img"[\s\S]*?<a target="_blank" href="(//item.jd.com/[\s\S]*?\.html)" >',
                re.S)
            itemUrl = re.findall(com, html)
            if len(itemUrl) == 0:
                com = re.compile(
                    r'<div class="p-img"[\s\S]*?<a target="_blank" href="(//item.jd.com/[\s\S]*?\.html)">',
                    re.S)
                itemUrl = re.findall(com, html)
            #mutex.acquire()
            print u'以下店铺URL来源'+pageurl
            #进入当前店铺
            if itemUrl is not None:
                for spurl in itemUrl:
                    if 'item.jd.com' not in spurl:
                        continue
                    url = 'http:' + spurl
                    #url='http://item.jd.com/11096365781.html'
                    #url='http://item.jd.com/1744432298.html'
                    print '当前店铺url：'+url
                    fo=open('333.txt','a')
                    fo.write(url+'\n')
                    fo.close()
                    yield Request(url, callback=self.JDProductAttrubuteSpider,headers=attrheaders,dont_filter=True,
                                  meta={'dpurl': url, 'JDCaterry': response.meta['JDCaterry'],
                                        'ec': response.meta['ec']})
                    #yield  item
                    # 取页面数，进行多页加载
            #mutex.release()

        except Exception, e:
            error=traceback.format_exc()
            print u"不知道什么错误：%s" % error
     # 第二步进入店铺内采集所需属性
    #京东各属性字段
    def JDProductAttrubuteSpider(self,response):
        try:

            index=0

            #测试有没有漏URl
            fo=open('444.txt','a')
            fo.write(response.url+'\n')
            fo.close()
            Url =response.url
            JDCateroy = response.meta['JDCaterry']
            #获取页面源码
            html = response.body
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode(mm)
            #转换源码的编码格式
            pageSource = html.encode('utf-8')
            if u'进口电器'==JDCateroy:
                JDCateroy=''
            #开始获取各属性值
            if pageSource is not None:
                # 商品名称 有可能分几种情况
                spname = re.search(r'<div class="sku-name">([\s\S]*?</)div>', pageSource,re.S)
                if spname is not None:
                    spname = spname.group(1).lstrip().rstrip()
                    if '<img' in spname :
                        spname=re.search(r'/>([\s\S]*?)</',spname,re.S)
                        if spname is not None:
                            spname=spname.group(1).lstrip().rstrip()
                    else:
                        if '自营' in spname:
                            onaem=re.search(r'/span>([\s\S]*?)</',spname,re.S)
                            if onaem is not None:
                                spname=onaem.group(1).strip()
                    spname = spname.replace('</', '').strip()
                else:
                    spname=''
                #规范品类名
                if  (JDCateroy==u'取暖电器') and ((u'暖器' in spname) or (u'暖气' in spname)):
                    JDCateroy=u'电暖器'

                #品牌
                sppingpai = re.search(r'<dt>品牌</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                if sppingpai is not None:
                    sppingpai = sppingpai.group(1).strip()
                if sppingpai is None or sppingpai == u'其他':
                    sppingpai = re.search(
                        r'<ul id="parameter-brand"[\s\S]*?<li title=[\s\S].*?<a href[\s\S].*?>([\s\S]*?)</a>',
                        pageSource, re.S)
                    if sppingpai is not None:
                        sppingpai = sppingpai.group(1).strip()

                    else:
                        sppingpai = ''
                #型号
                spxinghao = re.search(r'<dt>型号</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                if spxinghao is None:
                    spxinghao=re.search(r'<dt>产品型号</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                if spxinghao is not None:
                    spxinghao = spxinghao.group(1).strip()
                else:
                    spxinghao = ''
                #旗舰店
                spShop=re.search(r'<div class="popbox-inner"[\s\S]*?<div class="mt">[\s\S]*?<h3>[\s\S]*?<a[\s\S].*?title="([\s\S].*?)"',pageSource,re.S)
                if spShop is None:
                    spShop=re.search(r'<div class="name"[\s\S]*?<a[\s\S]*?>([\s\S].*?)</a>', pageSource, re.S)

                if spShop is not None:
                    spShop = spShop.group(1).strip()
                    if ('旗舰店' not in spShop) and ('专营店' not in spShop) and ('专卖店' not in spShop) and ('专区' not in spShop) and ('家电馆' not in spShop)  :
                        spShop = ''
                else:
                    spShop = ''
                #item['spShop'] = spShop
                #print  spShop
                #累计评价
                #取出商品
                item = JDSpiderItem()
                item['ec'] = response.meta['ec']
                item['urls'] =Url
                item['spleibie'] =JDCateroy
                item['spName'] =  spname
                item['sppingpai'] =  sppingpai
                item['spxinghao'] =  spxinghao
                item['spShop'] = spShop
                item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
                yield  item
                # productplNum=re.search(r'(\d+)',response.url,re.S).group(1)
                # #productplNum=int(productplNum)
                # PJNumURL = Modle.JDPLCountURL.format(productplNum)
                # yield Request(PJNumURL, callback=self.JDplNum, headers=attrheaders, dont_filter=True,
                #               meta={'plurl': Url, 'JDCaterry': response.meta['JDCaterry'],
                #                     'SpShop': spShop,'spname':spname,'sppingpai':sppingpai,'spxinghao':spxinghao,'ec':response.meta['ec']})
                print 'oo=====================存储成功=============================oo'
            else:
                print '页面加载内容为空：%s' % Url
        except Exception,e:
            fo = open('log.txt', 'a')
            fo.write(response.url+ '\n')
            fo.write(str(e)+'\n')
            fo.close()
            index+=1
            print "不知道什么的错,可能代理问题，换个再尝试重新获取 %s" % e

    #京东评论数
    def JDplNum(self,response):
        item = JDSpiderItem()
        item['ec'] = response.meta['ec']
        item['urls'] = response.meta['plurl']
        item['spleibie']=response.meta['JDCaterry']
        item['spName'] = response.meta['spname']
        item['sppingpai'] = response.meta['sppingpai']
        item['spxinghao'] = response.meta['spxinghao']
        item['spShop'] = response.meta['SpShop']
        item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
        pageSource=response.body
        mm = response.encoding
        if 'gb' in str(mm) or 'GB' in str(mm):
            pageSource = pageSource.decode('GBK')

        jsonHtml = pageSource.replace("jQuery5663852(", "")
        JDPLhtml = jsonHtml[:-2]
        # 序列化所获取的内容
        jsonPL = json.loads(JDPLhtml)
        PJNum = jsonPL['CommentsCount'][0]['CommentCount']
        #PJNum=PJNum.replace(',','')
        item['spplNum']=PJNum
        print ' JDPJ end:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            time.time()))
        yield item
    #SN页数
    def SNPage(self,response):
       # pageNum = response.meta['pageNum']
        #attrheaders = {"Referer":str(spurl),"Host":"review.suning.com","Connection":"keep-alive"}
        #
        attrheaders={
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
    }
        #spurl = response.url
        #plheaders = {"Referer": "" + spurl + ""}
        #获取URL
        url = response.meta['urlpage']
        # 获取页数
        html = response.body
        mm = response.encoding
        if 'gb' in str(mm) or 'GB' in str(mm):
            html = html.decode('GBK')
        # html = str(html).encode('utf-8')

        if html:
            NumPage = re.search(r'<i id="pageThis">[\s\S]*?</i>(\/[\s\S]*?)</span>', html, re.S).group(
                1).encode('utf-8')
            print NumPage
            if NumPage is None:
                NumPage = 0
            NumPage=NumPage.replace('/','')
        pageNum=int(NumPage)
        for i in range(0, pageNum):

            list = str(url).split('-')
            if len(list) > 1:
                list[2] = str(i)+'.html'
                urlpage = '-'.join(list)
            elif 'ch=3' in url:
                urlpage = url + '&cp=' + str(i)
            elif 'cityId={cityId}' in url:
                urlpage = str(url).replace('cityId={cityId}', '&iy=0&cp=') + str(i)
            fo = open('sn33.txt', 'a')
            fo.write(urlpage + '\n')
            fo.close()
            print  u'开始URl:'+urlpage +u'第'+ str(i)+ u'页'
            time.sleep(1)
            yield Request(urlpage, callback=self.SNUrlparse, headers=attrheaders , dont_filter=True,
                      meta={'dpurl': urlpage, 'Caterry': response.meta['Caterry'],
                            'ec': response.meta['ec']})
    #苏宁电商
    def SNUrlparse(self,response):
        print '开始URl加工\033[0;31;0m Time：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            time.time())) + '\033[0m'
        try:

            spurl = response.url
            #attrheaders =  {"Referer":str(spurl),"Host":"review.suning.com","Connection":"keep-alive"}
            attrheaders = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip,deflate",
                "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
                "Connection": "keep-alive",
                "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
            }
            html = response.body
            #print html
            # 判断当前页面编码格式
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            # html = str(html).encode('utf-8')
            # 第一步在取出页面内所有该品类的店铺的URL
            com = re.compile(
                r'<div class="img-block"[\s\S]*?<a target="_blank"[\s\S].*?href="(//product.suning.com/[\s\S]*?\.html)" name=[\s\S]*?>',
                re.S)
            itemUrl = re.findall(com, html)
            print u'以下店铺URL来源' + spurl

            if itemUrl is not None:
                for spurl in itemUrl:
                    url = 'http:' + spurl
                    # url=' http://item.jd.com/10672650590.html'
                    if '-' in url:
                        start=url.find('-')
                        url=url[0:start]+'.html'
                    print '当前店铺url：' + url
                    fo = open('sn1.txt', 'a')
                    fo.write(url + '\n')
                    fo.close()
                    yield Request(url, callback=self.SNProductAttrubuteSpider, headers=attrheaders, dont_filter=True,
                                  meta={'dpurl': url, 'Cateroy': response.meta['Caterry'],
                                        'ec': response.meta['ec']})
                    # yield  item
                    # 取页面数，进行多页加载
                    # mutex.release()

        except Exception, e:
            error = traceback.format_exc()
            print u"不知道什么错误：%s" % error
    def SNProductAttrubuteSpider(self,response):
        try:
            index = 0
            item = JDSpiderItem()
            # 测试有没有漏URl
            fo = open('sn2.txt', 'a')
            fo.write(response.url + '\n')
            fo.close()
            Url = response.url
            SNCateroy = response.meta['Cateroy']

            #attrheaders =  {"Referer":str(Url),"Host":"review.suning.com","Connection":"keep-alive"}
            attrheaders = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
            "Connection": "keep-alive",
            "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
        }
            # time.sleep(1)
            html = response.body
            mm = response.encoding
            # if 'gb' in str(mm) or 'GB' in str(mm):
            html = html.decode(mm)
            pageSource = html.encode('utf-8')
            # print  pageSource
            # if len(pageSource)<50:
            #     index+=1
            #     continue

            # 开始获取各属性值
            if pageSource is not None:
                # 商品名称 有可能分几种情况
                spname = re.search(r'<h1 id="itemDisplayName">([\s\S]*?<)/h1>', pageSource, re.S)
                if spname is not None:
                    spname = spname.group(1).lstrip().rstrip()
                    if '<img' in spname:
                        spname = re.search(r'/>([\s\S]*?)</', spname, re.S)
                        if spname is not None:
                            spname = spname.group(1).lstrip().rstrip()
                    else:
                        if '自营' in spname:
                            spname = re.search(r'</span>([\s\S].*?)<', spname, re.S)
                            spname = spname.group(1).strip()
                    spname = spname.replace('</', '').replace('<','').strip()
                else:
                    spname = ''
                # item['spName']=spname
                # print   spname
                if (SNCateroy == u'取暖电器') and ((u'暖器' in spname) or (u'暖气' in spname)):
                    SNCateroy = u'电暖器'
                if u'热水器' in SNCateroy:
                    SNCateroy='热水器'
                item['spleibie'] = SNCateroy
                # 品牌
                sppingpai = re.search(r'<div class="name-inner">[\s\S].*?<span>品牌</span>[\s\S]*?<td class="val"><a href=[\s\S].*?>([\s\S]*?)</a>', pageSource, re.S)
                if sppingpai is None:
                    sppingpai = re.search(
                        r'<ul id="parameter-brand"[\s\S]*?<li title=[\s\S].*?<a href[\s\S].*?>([\s\S]*?)</a>', pageSource,
                        re.S)
                if sppingpai is not None:
                    sppingpai = sppingpai.group(1).strip()

                else:
                    sppingpai = ''
                # item['sppingpai']=sppingpai
                # print  sppingpai
                # 型号
                spxinghao = re.search(r'<div class="name-inner">[\s\S].*?<span>型号</span>[\s\S]*?<td class="val">([\s\S]*?)</td>', pageSource, re.S)
                if spxinghao is None:
                    spxinghao = re.search(r'<div class="name-inner">[\s\S].*?<span>产品型号</span>[\s\S]*?<td class="val">([\s\S]*?)</td>', pageSource, re.S)
                if spxinghao is not None:
                    spxinghao = spxinghao.group(1).strip()
                else:
                    spxinghao = ''
                # item['spxinghao'] = spxinghao
                # print spxinghao
                # 旗舰店
                spShop = re.search(
                    r'<strong id="curShopName">[\s\S].*?<a[\s\S].*?>([\s\S].*?)</a>',
                    pageSource, re.S)
                if spShop is None:
                    spShop = re.search(r'<div class="name"[\s\S]*?<a[\s\S]*?>([\s\S].*?)</a>', pageSource, re.S)

                if spShop is not None:
                    spShop = spShop.group(1).strip()
                    # if ('旗舰店' not in spShop) and ('专营店' not in spShop) and ('专卖店' not in spShop) and (
                    #     '专区' not in spShop) and ('家电馆' not in spShop):
                    #     spShop = ''
                else:
                    spShop = ''
                # item['spShop'] = spShop
                # print  spShop
                # 累计评价
                # 取出商品
                # pruductplNumlist=str(response.url).split('/')
                # pruductplNumlist[4]='000000000'+pruductplNumlist[4].replace('.html','')
                #
                # #productplNum = re.search(r'(\d+)', response.url, re.S).group(1)
                # # productplNum=int(productplNum)
                # PJNumURL = Modle.SNPLCountURL.format(pruductplNumlist[4],pruductplNumlist[3])
                # fo = open('sn41.txt', 'a')
                # fo.write(PJNumURL + '\n')
                # fo.close()
                # yield Request(PJNumURL, callback=self.SNplNum, headers=attrheaders, dont_filter=True,
                #               meta={'plurl': Url, 'JDCaterry': SNCateroy,
                #                     'SpShop': spShop, 'spname': spname, 'sppingpai': sppingpai, 'spxinghao': spxinghao,
                #                     'ec': response.meta['ec']})
                item = JDSpiderItem()
                item['ec'] = response.meta['ec']
                item['urls'] = Url
                item['spleibie'] = SNCateroy
                item['spName'] = spname
                item['sppingpai'] = sppingpai
                item['spxinghao'] = spxinghao
                item['spShop'] = spShop
                item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
                yield item

                print 'oo=====================存储成功=============================oo'
            else:
                print '页面加载内容为空：%s' % Url
        except Exception, e:
            index += 1
            print "不知道什么的错,可能代理问题，换个再尝试重新获取 %s" % e
    def SNplNum(self,response):
        fo = open('sn4.txt', 'a')
        fo.write(response.url + '\n')
        fo.close()
        item = JDSpiderItem()
        item['ec'] = response.meta['ec']
        item['urls'] = response.meta['plurl']
        item['spleibie'] = response.meta['JDCaterry']
        item['spName'] = response.meta['spname']
        item['sppingpai'] = response.meta['sppingpai']
        item['spxinghao'] = response.meta['spxinghao']
        item['spShop'] = response.meta['SpShop']
        item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
        try:
            pageSource = response.body
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                pageSource = pageSource.decode('GBK')

            jsonHtml = pageSource.replace("satisfy(", "")
            JDPLhtml = jsonHtml[:-1]
            # 序列化所获取的内容
            jsonPL = json.loads(JDPLhtml)
            PJNum = jsonPL['reviewCounts'][0]['totalCount']
            # PJNum=PJNum.replace(',','')
            item['spplNum'] = PJNum
            print ' JDPJ end:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                time.time()))
            yield item
        except Exception,e:
            print e.message

    # YMX页面数
    def YMXPage(self, response):
        index = 0
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
            "Connection": "keep-alive",
            "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
        }
        try:
            spurl = response.url
            plheaders = {"Referer": "" + spurl + ""}
            url = response.meta['urlpage']
            # 获取页数
            html = response.body
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            # html = str(html).encode('utf-8')
            NumPage = re.search(r'<span class="pagnDisabled">(\d+?)</span>', html, re.S)
            if NumPage is not None:
                NumPage = NumPage.group(
                    1).encode('utf-8')
            else:
                com = re.compile(
                    r'<span class="pagnLink">[\s\S]*?<a[\s\S].*?>(\d+?)</a></span>',
                    re.S)
                itemUrl = re.findall(com, html)
                if itemUrl is not None:
                    NumPage = itemUrl[(len(itemUrl) - 1)]
            # NumPage = NumPage.replace('/', '')
            # print NumPage
            if NumPage is None:
                NumPage = 0
                print NumPage
                if NumPage is None:
                    NumPage = str(0)
            # for i in range(1,int(NumPage)+1):
            list=url.split('&')

            for i in range(1, int(NumPage) + 1):
            #for i in range(1, 2):
                if len(list) < 3:
                    list.insert(1, 'page=' + str(i))

                else:
                    list[1]='page=' + str(i)
                urlpage = '&'.join(list)
                print  u'当前品类url:' + urlpage
                time.sleep(1)
                yield Request(urlpage, callback=self.YMXUrlparse, headers=headers, dont_filter=True,
                              meta={'pageurl': urlpage, 'Category': response.meta['Caterry'],
                                    'ec': response.meta['ec']})

                # yield pageitem

        except Exception, e:
            print '可能连接超时，详情：' + e.message
            # 京东URL

    def YMXUrlparse(self, response):
        print '开始URl加工\033[0;31;0m Time：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            time.time())) + '\033[0m'
        try:

            spurl = response.url

            attrheaders = {"Referer": "" + spurl + ""}
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip,deflate",
                "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
                "Connection": "keep-alive",
                "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
            }
            # time.sleep(1)
            pageurl = response.meta['pageurl']
            html = response.body
            # 判断当前页面编码格式
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            # html = str(html).encode('utf-8')
            # 第一步在取出页面内所有该品类的店铺的URL
            com = re.compile(
                r'<div class="a-section a-spacing-none a-inline-block s-position-relative"><a class="a-link-normal a-text-normal" target="_blank" href="([\s\S]*?)"><img',
                re.S)
            itemUrl = re.findall(com, html)
            # if len(itemUrl) == 0:
            #     com = re.compile(
            #         r' ',
            #         re.S)
            #     itemUrl = re.findall(com, html)
            # mutex.acquire()
            print u'以下店铺URL来源' + pageurl

            if itemUrl is not None:
                for spurl in itemUrl:
                    url = spurl
                    #url='https://www.amazon.cn/%E6%89%8B%E6%9C%BA-%E9%80%9A%E8%AE%AF/dp/B019W3ZG7C'
                    if 'http' in url:
                        print '当前店铺url：' + url
                        yield Request(url, callback=self.YMXProductAttrubuteSpider, headers=headers, dont_filter=True,
                                      meta={'dpurl': url, 'Category': response.meta['Category'],
                                            'ec': response.meta['ec']})
                    # yield  item
                    # 取页面数，进行多页加载
                    # mutex.release()

        except Exception, e:
            error = traceback.format_exc()
            print u"不知道什么错误：%s" % error
            # 第二步进入店铺内采集所需属性
            # 京东各属性字段

    def YMXProductAttrubuteSpider(self, response):
        try:

            index = 0
            Url = response.url
            Category = response.meta['Category']
            attrheaders = {"Referer": "" + Url + ""}
            # time.sleep(1)
            html = response.body
            mm = response.encoding
            # if 'gb' in str(mm) or 'GB' in str(mm):
            html = html.decode(mm)
            pageSource = html.encode('utf-8')
            # 开始获取各属性值
            if pageSource is not None:
                # 商品名称 有可能分几种情况
                spname = re.search(r'<span id="productTitle" class="a-size-large">([\s\S]*?)</span>', pageSource, re.S)
                if spname is not None:

                    spname = spname.group(1).lstrip().rstrip().decode('utf-8')

                else:
                    spname = ''
                if (Category == u'取暖电器') and ((u'暖器' in spname) or (u'暖气' in spname)):
                    Category = u'电暖器'
                # 品牌
                sppingpai = re.search(r'<a id="brand" class="a-link-normal"[\s\S]*?>([\s\S]*?)</a>', pageSource, re.S)
                if sppingpai is not None:
                    sppingpai = sppingpai.group(1).strip().decode('utf-8')
                else:
                    sppingpai = ''
                # 型号
                spxinghao = re.search(r"<td class='label'>型号</td><td class='value'>([\s\S]*?)</td>", pageSource, re.S)
                if spxinghao is None:
                    spxinghao = re.search(r'<li><b>型号:</b>([\s\S]*?)</li>', pageSource, re.S)
                if spxinghao is not None:
                    spxinghao = spxinghao.group(1).strip()
                else:
                    spxinghao = ''
                # 旗舰店
                spShop = '亚马逊'
                # 累计评价
                # 取出商品
                # productplNum = re.search(r'<span id="acrCustomerReviewText" class="a-size-base">([\s\S]*?)条商品评论</span>', pageSource, re.S)
                # if productplNum is not  None:
                #     PJNum=productplNum.group(1).strip()
                # else:
                #     PJNum='0'
                item = JDSpiderItem()
                item['ec'] = response.meta['ec']
                item['urls'] =Url
                item['spleibie'] = Category
                item['spName'] = spname.encode('utf-8')
                item['sppingpai'] = sppingpai
                item['spxinghao'] = spxinghao
                item['spShop'] = spShop
                #item['spplNum']=PJNum
                item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
                yield  item
                print 'oo=====================存储成功=============================oo'
            else:
                print '页面加载内容为空：%s' % Url
        except Exception, e:
            index += 1
            print "不知道什么的错,可能代理问题，换个再尝试重新获取 %s" % e
            # if index>ErroNum:
            #     print "经过多试尝试，没有成功，有可能是其他问题"
            # 京东评论数

    # GM页面数
    def GMPage(self, response):
        index = 0
        try:
            spurl = response.url
            plheaders = {"Referer": "" + spurl + ""}
            url = response.meta['urlpage']
            # 获取页数
            html = response.body
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            # html = str(html).encode('utf-8')
            NumPage = re.search(r'<span class="min-pager-number" id="min-pager-number">([\s\S]*?)</span>', html, re.S)
            if NumPage is None:
                NumPage = re.search(r'<span id="min-pager-number" class="min-pager-number">([\s\S]*?)</span>', html,
                                    re.S)
            if NumPage is not None:
                NumPage = NumPage.group(
                    1).encode('utf-8')
                list=NumPage.split('/')
                NumPage=list[len(list)-1]
            else:
                NumPage = 1
            for i in range(1, int(NumPage) + 1):
            #for i in range(1,  2):
                urlpage = url+'?page=' + str(i)
                print  u'当前品类url:' + urlpage
                #time.sleep(1)
                yield Request(urlpage, callback=self.GMUrlparse, headers=plheaders, dont_filter=True,
                              meta={'pageurl': urlpage, 'Category': response.meta['Caterry'],
                                    'ec': response.meta['ec']})

                # yield pageitem

        except Exception, e:
            print '可能连接超时，详情：' + e.message
            # 京东URL

    def GMUrlparse(self, response):
        print '开始URl加工\033[0;31;0m Time：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            time.time())) + '\033[0m'
        try:

            spurl = response.url
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip,deflate",
                "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
                "Connection": "keep-alive",
                "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
            }

            attrheaders = {"Referer": "" + spurl + ""}
            # time.sleep(1)
            pageurl = response.meta['pageurl']
            html = response.body
            # 判断当前页面编码格式
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            # html = str(html).encode('utf-8')
            # 第一步在取出页面内所有该品类的店铺的URL
            com = re.compile(
                r'<a class="emcodeItem item-link"  href="([\s\S]*?)" title',
                re.S)
            itemUrl = re.findall(com, html)
            # if len(itemUrl) == 0:
            #     com = re.compile(
            #         r' ',
            #         re.S)
            #     itemUrl = re.findall(com, html)
            # mutex.acquire()
            print u'以下店铺URL来源' + pageurl
            #itemUrl=['http://item.gome.com.cn/9134115681-1123080118.html']
            if itemUrl is not None:
                for spurl in itemUrl:
                    url = spurl
                    #url='http://item.gome.com.cn/9134115681-1123080118.html'
                    print '当前店铺url：' + url
                    yield Request(url, callback=self.GMProductAttrubuteSpider, headers=headers, dont_filter=True,
                                  meta={'dpurl': url, 'Category': response.meta['Category'],
                                        'ec': response.meta['ec']})
                    # yield  item
                    # 取页面数，进行多页加载
                    # mutex.release()

        except Exception, e:
            error = traceback.format_exc()
            print u"不知道什么错误：%s" % error
            # 第二步进入店铺内采集所需属性
            # 京东各属性字段

    def GMProductAttrubuteSpider(self, response):
        try:

            index = 0
            Url = response.url
            Cateroy = response.meta['Category']
            attrheaders = {"Referer": "" + Url + ""}
            # time.sleep(1)
            html = response.body
            mm = response.encoding
            # if 'gb' in str(mm) or 'GB' in str(mm):
            html = html.decode(mm)
            pageSource = html.encode('utf-8')
            # 开始获取各属性值
            if pageSource is not None:
                # 商品名称 有可能分几种情况
                spname = re.search(r'<div class="hgroup">[\s\S]*?<h1>([\s\S]*?)</h1>', pageSource, re.S)
                if spname is not None:
                    spname = spname.group(1).lstrip().rstrip()
                    # if '<img' in spname:
                    #     spname = re.search(r'/>([\s\S]*?)</', spname, re.S)
                    #     if spname is not None:
                    #         spname = spname.group(1).lstrip().rstrip()
                    # else:
                    #     if '自营' in spname:
                    #         spname = re.search(r'/span>([\s\S]*?)</', spname, re.S)
                    #         spname = spname.group(1).strip()
                    spname = spname.replace('</', '').strip()
                else:
                    spname = ''
                # item['spName']=spname
                # print   spname
                if (Cateroy == u'取暖电器') and ((u'暖器' in spname) or (u'暖气' in spname)):
                    Cateroy = u'电暖器'
                # 品牌
                sppingpai = re.search(r'<span class="specinfo">品牌</span><span>([\s\S].*?)</span>', pageSource, re.S)
                # if sppingpai is None:
                #     sppingpai = re.search(
                #         r'<ul id="parameter-brand"[\s\S]*?<li title=[\s\S].*?<a href[\s\S].*?>([\s\S]*?)</a>',
                #         pageSource, re.S)
                if sppingpai is not None:
                    sppingpai = sppingpai.group(1).strip()
                else:
                    sppingpai = ''
                # 型号
                spxinghao = re.search(r'<span class="specinfo">型号</span><span>([\s\S].*?)</span>', pageSource, re.S)
                if spxinghao is None:
                    spxinghao = re.search(r'<<span class="specinfo">产品型号</span><span>([\s\S].*?)</span>', pageSource, re.S)
                if spxinghao is not None:
                    spxinghao = spxinghao.group(1).strip()
                else:
                    spxinghao = ''
                # 旗舰店
                spShop = re.search(
                    r'<h2 class="fix-storesname shops-name" id="store_live800_wrap">[\s\S]*?<a class="name"[\s\S]*? href=[\s\S].*? target="_blank">([\s\S].*?)</a>',
                    pageSource, re.S)
                if spShop is None:
                    spShop = re.search(r'<h2 id="store_live800_wrap" class="fix-storesname shops-name">[\s\S]*?<a class="name"[\s\S]*? href=[\s\S].*? target="_blank">([\s\S].*?)</a>', pageSource, re.S)

                if spShop is not None:
                    spShop = spShop.group(1).strip()
                    if ('旗舰店' not in spShop) and ('专营店' not in spShop) and ('专卖店' not in spShop) and (
                                '专区' not in spShop) and ('家电馆' not in spShop):
                        spShop = '国美自营'
                else:
                    spShop=''
                # 累计评价
                # 取出商品
                #
                # productplList=Url.split('/')
                # productplNum=productplList[3].replace('.html','').replace('-','/')
                # # productplNum=int(productplNum)
                # PJNumURL = Modle.GMPLCountURL.format(productplNum)
                # yield Request(PJNumURL, callback=self.GMplNum, headers=attrheaders, dont_filter=True,
                #               meta={'plurl': Url, 'Category': response.meta['Category'],
                #                     'SpShop': spShop, 'spname': spname, 'sppingpai': sppingpai, 'spxinghao': spxinghao,
                #                     'ec': response.meta['ec']})
                item = JDSpiderItem()
                item['ec'] = response.meta['ec']
                item['urls'] = Url
                item['spleibie'] = Cateroy
                item['spName'] = spname
                item['sppingpai'] = sppingpai
                item['spxinghao'] = spxinghao
                item['spShop'] = spShop
                # item['spplNum']=PJNum
                item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
                yield item
                print 'oo=====================存储成功=============================oo'
            else:
                print '页面加载内容为空：%s' % Url
        except Exception, e:
            index += 1
            print "不知道什么的错,可能代理问题，换个再尝试重新获取 %s" % e
            # if index>ErroNum:
            #     print "经过多试尝试，没有成功，有可能是其他问题"
            # 京东评论数

    def GMplNum(self, response):
        item = JDSpiderItem()
        item['ec'] = response.meta['ec']
        item['urls'] = response.meta['plurl']
        item['spleibie'] = response.meta['Category']
        item['spName'] = response.meta['spname']
        item['sppingpai'] = response.meta['sppingpai']
        item['spxinghao'] = response.meta['spxinghao']
        item['spShop'] = response.meta['SpShop']
        item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
        pageSource = response.body
        mm = response.encoding
        if 'gb' in str(mm) or 'GB' in str(mm):
            pageSource = pageSource.decode('GBK')

        try:
            jsonHtml = pageSource.replace("allStores(", "")
            JDPLhtml = jsonHtml[:-1]
            # 序列化所获取的内容
            jsonPL = json.loads(JDPLhtml)
            PJNum = jsonPL['result']['appraise']['comments']
            # PJNum=PJNum.replace(',','')
            item['spplNum'] = PJNum
            print ' PJ end:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                time.time()))
            yield item
        except Exception,e:
            print e

    # DD页面数
    def DDPage(self, response):
        index = 0
        try:
            spurl = response.url
            plheaders = {"Referer": "" + spurl + ""}
            url = response.meta['urlpage']
            # 获取页数
            html = response.body
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            # html = str(html).encode('utf-8')
            NumPage = re.search(r'<span class="or">\d+</span><span>\/(\d+?)</span>', html, re.S)
            if NumPage is not None:
                NumPage = NumPage.group(
                    1).encode('utf-8')
            if NumPage is None:
                NumPage = 1
            list = url.split('/')
            pg = list[3]

            for i in range(1, int(NumPage) + 1):
                list[3]='pg'+str(i)+'-'+pg
                urlpage = '/'.join(list)
                print  u'当前品类url:' + urlpage
                time.sleep(1)
                yield Request(urlpage, callback=self.DDUrlparse, headers=plheaders, dont_filter=True,
                              meta={'pageurl': urlpage, 'Category': response.meta['Caterry'],
                                    'ec': response.meta['ec']})

                # yield pageitem

        except Exception, e:
            print '可能连接超时，详情：' + e.message


    def DDUrlparse(self, response):
        print '开始URl加工\033[0;31;0m Time：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            time.time())) + '\033[0m'
        try:

            spurl = response.url

            attrheaders = {"Referer": "" + spurl + ""}
            attrheaders = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip,deflate",
                "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
                "Connection": "keep-alive",
                "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
            }
            # time.sleep(1)
            pageurl = response.meta['pageurl']
            html = response.body
            # 判断当前页面编码格式
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            # html = str(html).encode('utf-8')
            # 第一步在取出页面内所有该品类的店铺的URL
            com = re.compile(
                r'<p class="name" name="title" ><a title="[\s\S].*?href="([\s\S]*?)" name',
                re.S)
            itemUrl = re.findall(com, html)
            if len(itemUrl) == 0:
                com = re.compile(
                    r'<p class="name" name="title"><a title="[\s\S].*?href="([\s\S]*?)" name',
                    re.S)
                itemUrl = re.findall(com, html)
            # mutex.acquire()
            print u'以下店铺URL来源' + pageurl

            if itemUrl is not None:
                for spurl in itemUrl:
                    url = spurl.encode('utf-8')
                    #url='http://product.dangdang.com/1054323595.html'
                    print '当前店铺url：' + url
                    yield Request(url, callback=self.DDProductAttrubuteSpider, headers=attrheaders, dont_filter=True,
                                  meta={'dpurl': url, 'Category': response.meta['Category'],
                                        'ec': response.meta['ec']})
                    # yield  item
                    # 取页面数，进行多页加载
                    # mutex.release()

        except Exception, e:
            error = traceback.format_exc()
            print u"不知道什么错误：%s" % error
            # 第二步进入店铺内采集所需属性
            # 京东各属性字段

    def DDProductAttrubuteSpider(self, response):
        try:

            index = 0
            Url = response.url
            Category = response.meta['Category']
            attrheaders = {"Referer": "" + Url + ""}
            # time.sleep(1)
            html = response.body
            mm = response.encoding
            # if 'gb' in str(mm) or 'GB' in str(mm):
            html = html.decode(mm)
            pageSource = html.encode('utf-8')
            # 开始获取各属性值
            if pageSource is not None:
                # 商品名称 有可能分几种情况
                spname = re.search(r'<div class="name_info" ddt-area="001">[\s\S]*?<h1 title="([\s\S].*?)">', pageSource, re.S)
                if spname is not None:
                    spname = spname.group(1).lstrip().rstrip()
                    # if '<img' in spname:
                    #     spname = re.search(r'/>([\s\S]*?)</', spname, re.S)
                    #     if spname is not None:
                    #         spname = spname.group(1).lstrip().rstrip()
                    # else:
                    #     if '自营' in spname:
                    #         spname = re.search(r'/span>([\s\S]*?)</', spname, re.S)
                    #         spname = spname.group(1).strip()
                    # spname = spname.replace('</', '').strip()
                else:
                    spname = ''
                # item['spName']=spname
                # print   spname
                if (Category == u'取暖电器') and ((u'暖器' in spname) or (u'暖气' in spname)):
                    Category = u'电暖器'
                # 品牌
                sppingpai = re.search(r"<li>品牌：<a target='_blank'[\S\s].*?>([\s\S].*?)</a>", pageSource, re.S)
                if sppingpai is None:
                    sppingpai = re.search(
                        r'<li>品牌：<a target="_blank"[\S\s].*?>([\s\S].*?)</a>',
                        pageSource, re.S)
                if sppingpai is not None:
                    sppingpai = sppingpai.group(1).strip()

                else:
                    sppingpai = ''
                # 型号
                spxinghao = re.search(r'<li>型号：([\s\S].*?)</li>', pageSource, re.S)
                if spxinghao is None:
                    spxinghao = re.search(r'<dt>产品型号</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                if spxinghao is not None:
                    spxinghao = spxinghao.group(1).strip()
                else:
                    spxinghao = ''
                # 旗舰店
                spShop = re.search(r'<a href=[\s\S].*? target="_blank" title="([\s\S].*?") dd_name="店铺名称">([\s\S]*?)</a>',
                    pageSource, re.S)
                if spShop is not None:
                    spShop = spShop.group(2).strip()
                    if ('旗舰店' not in spShop) and ('专营店' not in spShop) and ('专卖店' not in spShop) and (
                                '专区' not in spShop) and ('家电馆' not in spShop):
                        spShop = ''
                else:
                    spShop = ''
                # 累计评价
                # 取出商品
                # productplNum = re.search(r'<a href=[\s\S].*?id="comm_num_down" dd_name="评论数">(\d+?)</a>',
                #                          pageSource, re.S)
                # if productplNum is not None:
                #     PJNum = productplNum.group(1).strip()
                # else:
                #     PJNum=0
                item = JDSpiderItem()
                item['ec'] = response.meta['ec']
                item['urls'] = Url
                item['spleibie'] = Category
                item['spName'] = spname
                item['sppingpai'] = sppingpai
                item['spxinghao'] = spxinghao
                item['spShop'] = spShop
                #item['spplNum'] = PJNum
                item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
                yield item
                # else:
                #     productplNum = re.search(r'(\d+)', response.url, re.S).group(1)
                #     # productplNum=int(productplNum)
                #     PJNumURL = Modle.DDPLCountURL.format(productplNum)
                #     yield Request(PJNumURL, callback=self.DDplNum, headers=attrheaders, dont_filter=True,
                #                   meta={'plurl': Url, 'Category': response.meta['Category'],
                #                         'SpShop': spShop, 'spname': spname, 'sppingpai': sppingpai, 'spxinghao': spxinghao,
                #                         'ec': response.meta['ec']})
                print 'oo=====================存储成功=============================oo'
            else:
                print '页面加载内容为空：%s' % Url
        except Exception, e:
            index += 1
            print "不知道什么的错,可能代理问题，换个再尝试重新获取 %s" % e
            # if index>ErroNum:
            #     print "经过多试尝试，没有成功，有可能是其他问题"
            # 京东评论数

    def DDplNum(self, response):
        item = JDSpiderItem()
        item['ec'] = response.meta['ec']
        item['urls'] = response.meta['plurl']
        item['spleibie'] = response.meta['Category']
        item['spName'] = response.meta['spname']
        item['sppingpai'] = response.meta['sppingpai']
        item['spxinghao'] = response.meta['spxinghao']
        item['spShop'] = response.meta['SpShop']
        item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
        pageSource = response.body
        mm = response.encoding
        if 'gb' in str(mm) or 'GB' in str(mm):
            pageSource = pageSource.decode('GBK')

        jsonHtml = pageSource.replace("jQuery5663852(", "")
        JDPLhtml = jsonHtml[:-2]
        # 序列化所获取的内容
        jsonPL = json.loads(JDPLhtml)
        PJNum = jsonPL['CommentsCount'][0]['CommentCount']
        # PJNum=PJNum.replace(',','')
        item['spplNum'] = PJNum
        print ' PJ end:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            time.time()))
        yield item

        # DD页面数
        def DDXPage(self, response):
            index = 0
            try:
                spurl = response.url
                plheaders = {"Referer": "" + spurl + ""}
                url = response.meta['urlpage']
                # 获取页数
                html = response.body
                mm = response.encoding
                if 'gb' in str(mm) or 'GB' in str(mm):
                    html = html.decode('GBK')
                # html = str(html).encode('utf-8')
                NumPage = re.search(r'<span class="pagnDisabled">(\d+?)</span>', html, re.S)
                if NumPage is not None:
                    NumPage = NumPage.group(
                        1).encode('utf-8')
                else:
                    com = re.compile(
                        r'<span class="pagnLink">[\s\S]*?<a[\s\S].*?>(\d+?)</a></span>',
                        re.S)
                    itemUrl = re.findall(com, html)
                    if itemUrl is not None:
                        NumPage = itemUrl[(len(itemUrl) - 1)]
                # NumPage = NumPage.replace('/', '')
                # print NumPage
                if NumPage is None:
                    NumPage = 0
                    print NumPage
                    if NumPage is None:
                        NumPage = str(0)
                # for i in range(1,int(NumPage)+1):
                list = url.split('&')

                for i in range(1, int(NumPage) + 1):
                    if len(list) < 3:
                        list.insert(1, 'page=' + str(i))

                    else:
                        list[1] = 'page=' + str(i)
                    urlpage = '&'.join(list)
                    print  u'当前品类url:' + urlpage
                    time.sleep(1)
                    yield Request(urlpage, callback=self.YMXUrlparse, headers=plheaders, dont_filter=True,
                                  meta={'pageurl': urlpage, 'Category': response.meta['Caterry'],
                                        'ec': response.meta['ec']})

                    # yield pageitem

            except Exception, e:
                print '可能连接超时，详情：' + e.message
                # 京东URL

        def DDUrlparse(self, response):
            print '开始URl加工\033[0;31;0m Time：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                time.time())) + '\033[0m'
            try:

                spurl = response.url

                attrheaders = {"Referer": "" + spurl + ""}
                # time.sleep(1)
                pageurl = response.meta['pageurl']
                html = response.body
                # 判断当前页面编码格式
                mm = response.encoding
                if 'gb' in str(mm) or 'GB' in str(mm):
                    html = html.decode('GBK')
                # html = str(html).encode('utf-8')
                # 第一步在取出页面内所有该品类的店铺的URL
                com = re.compile(
                    r'',
                    re.S)
                itemUrl = re.findall(com, html)
                if len(itemUrl) == 0:
                    com = re.compile(
                        r' ',
                        re.S)
                    itemUrl = re.findall(com, html)
                # mutex.acquire()
                print u'以下店铺URL来源' + pageurl

                if itemUrl is not None:
                    for spurl in itemUrl:
                        url = 'http:' + spurl
                        # url=' http://item.jd.com/10672650590.html'
                        print '当前店铺url：' + url
                        yield Request(url, callback=self.JDProductAttrubuteSpider, headers=attrheaders,
                                      dont_filter=True,
                                      meta={'dpurl': url, 'Category': response.meta['Category'],
                                            'ec': response.meta['ec']})
                        # yield  item
                        # 取页面数，进行多页加载
                        # mutex.release()

            except Exception, e:
                error = traceback.format_exc()
                print u"不知道什么错误：%s" % error
                # 第二步进入店铺内采集所需属性
                # 京东各属性字段

        def DDProductAttrubuteSpider(self, response):
            try:

                index = 0
                Url = response.url
                JDCateroy = response.meta['Category']
                attrheaders = {"Referer": "" + Url + ""}
                # time.sleep(1)
                html = response.body
                mm = response.encoding
                # if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode(mm)
                pageSource = html.encode('utf-8')
                # 开始获取各属性值
                if pageSource is not None:
                    # 商品名称 有可能分几种情况
                    spname = re.search(r'<div class="sku-name">([\s\S]*?</)div>', pageSource, re.S)
                    if spname is not None:
                        spname = spname.group(1).lstrip().rstrip()
                        if '<img' in spname:
                            spname = re.search(r'/>([\s\S]*?)</', spname, re.S)
                            if spname is not None:
                                spname = spname.group(1).lstrip().rstrip()
                        else:
                            if '自营' in spname:
                                spname = re.search(r'/span>([\s\S]*?)</', spname, re.S)
                                spname = spname.group(1).strip()
                        spname = spname.replace('</', '').strip()
                    else:
                        spname = ''
                    # item['spName']=spname
                    # print   spname
                    if (JDCateroy == u'取暖电器') and ((u'暖器' in spname) or (u'暖气' in spname)):
                        JDCateroy = u'电暖器'
                    # 品牌
                    sppingpai = re.search(r'<dt>品牌</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                    if sppingpai is None:
                        sppingpai = re.search(
                            r'<ul id="parameter-brand"[\s\S]*?<li title=[\s\S].*?<a href[\s\S].*?>([\s\S]*?)</a>',
                            pageSource, re.S)
                    if sppingpai is not None:
                        sppingpai = sppingpai.group(1).strip()

                    else:
                        sppingpai = ''
                    # 型号
                    spxinghao = re.search(r'<dt>型号</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                    if spxinghao is None:
                        spxinghao = re.search(r'<dt>产品型号</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                    if spxinghao is not None:
                        spxinghao = spxinghao.group(1).strip()
                    else:
                        spxinghao = ''
                    # 旗舰店
                    spShop = re.search(
                        r'<div class="popbox-inner"[\s\S]*?<div class="mt">[\s\S]*?<h3>[\s\S]*?<a[\s\S].*?title="([\s\S].*?)"',
                        pageSource, re.S)
                    if spShop is None:
                        spShop = re.search(r'<div class="name"[\s\S]*?<a[\s\S]*?>([\s\S].*?)</a>', pageSource, re.S)

                    if spShop is not None:
                        spShop = spShop.group(1).strip()
                        if ('旗舰店' not in spShop) and ('专营店' not in spShop) and ('专卖店' not in spShop) and (
                                    '专区' not in spShop) and ('家电馆' not in spShop):
                            spShop = ''
                    else:
                        spShop = ''
                    # 累计评价
                    # 取出商品

                    productplNum = re.search(r'(\d+)', response.url, re.S).group(1)
                    # productplNum=int(productplNum)
                    PJNumURL = Modle.JDPLCountURL.format(productplNum)
                    yield Request(PJNumURL, callback=self.JDplNum, headers=attrheaders, dont_filter=True,
                                  meta={'plurl': Url, 'Category': response.meta['Category'],
                                        'SpShop': spShop, 'spname': spname, 'sppingpai': sppingpai,
                                        'spxinghao': spxinghao,
                                        'ec': response.meta['ec']})
                    print 'oo=====================存储成功=============================oo'
                else:
                    print '页面加载内容为空：%s' % Url
            except Exception, e:
                index += 1
                print "不知道什么的错,可能代理问题，换个再尝试重新获取 %s" % e
                # if index>ErroNum:
                #     print "经过多试尝试，没有成功，有可能是其他问题"
                # 京东评论数

        def DDplNum(self, response):
            item = JDSpiderItem()
            item['ec'] = response.meta['ec']
            item['urls'] = response.meta['plurl']
            item['spleibie'] = response.meta['Category']
            item['spName'] = response.meta['spname']
            item['sppingpai'] = response.meta['sppingpai']
            item['spxinghao'] = response.meta['spxinghao']
            item['spShop'] = response.meta['SpShop']
            item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
            pageSource = response.body
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                pageSource = pageSource.decode('GBK')

            jsonHtml = pageSource.replace("jQuery5663852(", "")
            JDPLhtml = jsonHtml[:-2]
            # 序列化所获取的内容
            jsonPL = json.loads(JDPLhtml)
            PJNum = jsonPL['CommentsCount'][0]['CommentCount']
            # PJNum=PJNum.replace(',','')
            item['spplNum'] = PJNum
            print ' PJ end:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                time.time()))
            yield item

    # YHD页面数
    def YHDPage(self, response):
        index = 0
        try:
            spurl = response.url
            plheaders = {"Referer": "" + spurl + ""}
            url = response.meta['urlpage']
            # 获取页数
            html = response.body
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            # html = str(html).encode('utf-8')
            NumPage = re.search(r'<div class="select_page_num">[\s\S]*?</span>([\s\S]*?)<', html, re.S)
            if NumPage is not None:
                NumPage = NumPage.group(
                    1).encode('utf-8')
                NumPage=NumPage.replace('/','')
            if NumPage is None:
                NumPage = 1
            for i in range(1, int(NumPage) + 1):
                #urlpage = spurl + '#page=' + str(i) + "&sort=1"
                list = spurl.split('/')
                if len(list) > 5:
                    nexturl = 'http://list.yhd.com/' + list[
                        3] + '/b/a-s1-v4-p' + str(i) + '-price-d0-f0-m1-rt0-pid-mid0-' + list[4] + '/'
                else:
                    nexturl = 'http://list.yhd.com/' + list[
                        3] + '/b/a-s1-v4-p' + str(i)  + '-price-d0-f0-m1-rt0-pid-mid0-k'
                urlpage=nexturl
                print  u'当前品类url:' + urlpage
                time.sleep(1)
                yield Request(urlpage, callback=self.YHDUrlparse, headers=plheaders, dont_filter=True,
                              meta={'pageurl': urlpage, 'Category': response.meta['Caterry'],
                                    'ec': response.meta['ec']})

                # yield pageitem

        except Exception, e:
            print '可能连接超时，详情：' + e.message


    def YHDUrlparse(self, response):
        print '开始URl加工\033[0;31;0m Time：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            time.time())) + '\033[0m'
        try:

            spurl = response.url

            attrheaders = {"Referer": "" + spurl + ""}
            # time.sleep(1)
            pageurl = response.meta['pageurl']
            attrheaders = {"Referer": "" + pageurl + ""}
            html = response.body
            # 判断当前页面编码格式
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode('GBK')
            # html = str(html).encode('utf-8')
            # 第一步在取出页面内所有该品类的店铺的URL
            com = re.compile(
                r'<p class="proName clearfix">[\s\S]*?href="([\s\S]*?)" target="_blank"',
                re.S)
            itemUrl = re.findall(com, html)
            if len(itemUrl) == 0:
                com = re.compile(
                    r'<a id="pdlink2[\s\S].*?href="([\s\S].*?)" target="_blank" name',
                    re.S)
            itemUrl = re.findall(com, html)
            if len(itemUrl)<55:
                re1=re.compile(
                r'<input id="promoProductsIdList" type="hidden" value="([\s\S].*?)"',
                re.S)
                itemUrl1 = re.findall(re1, html)
            itemUrl.extend(itemUrl1)
            print u'以下店铺URL来源' + pageurl

            if itemUrl is not None:
                for spurl11 in itemUrl:
                    url = spurl11
                    #url = 'http://item.yhd.com/item/46399835'
                    print '当前店铺url：' + url
                    yield Request(url, callback=self.YHDProductAttrubuteSpider, headers=attrheaders, dont_filter=True,
                                  meta={'dpurl': url, 'Category': response.meta['Category'],
                                        'ec': response.meta['ec']})
                    # yield  item
                    # 取页面数，进行多页加载
                    # mutex.release()

        except Exception, e:
            error = traceback.format_exc()
            print u"不知道什么错误：%s" % error
            # 第二步进入店铺内采集所需属性
            # 京东各属性字段

    def YHDProductAttrubuteSpider(self, response):
        try:

            index = 0
            Url = response.url
            Category = response.meta['Category']
            attrheaders = {"Referer": "" + Url + ""}
            # time.sleep(1)
            html = response.body
            mm = response.encoding
            # if 'gb' in str(mm) or 'GB' in str(mm):
            html = html.decode(mm)
            pageSource = html.encode('utf-8')
            # 开始获取各属性值
            if pageSource is not None:
                # 商品名称 有可能分几种情况
                spname = re.search(r'<h1 class="mh" id="productMainName" >([\s\S].*?)</h1>',
                                   pageSource, re.S)
                if spname is not None:
                    spname = spname.group(1).lstrip().rstrip()
                    # if '<img' in spname:
                    #     spname = re.search(r'/>([\s\S]*?)</', spname, re.S)
                    #     if spname is not None:
                    #         spname = spname.group(1).lstrip().rstrip()
                    # else:
                    #     if '自营' in spname:
                    #         spname = re.search(r'/span>([\s\S]*?)</', spname, re.S)
                    #         spname = spname.group(1).strip()
                    # spname = spname.replace('</', '').strip()
                else:
                    spname = ''
                # item['spName']=spname
                # print   spname
                if (Category == u'取暖电器') and ((u'暖器' in spname) or (u'暖气' in spname)):
                    Category = u'电暖器'
                # 品牌
                sppingpai = re.search(r'<dd title="品牌：([\s\S].*?)" >', pageSource, re.S)
                if sppingpai is None:
                    sppingpai = re.search(
                        r'<dd title="品牌：([\s\S].*?)">',
                        pageSource, re.S)
                if sppingpai is not None:
                    sppingpai = sppingpai.group(1).strip()

                else:
                    sppingpai = ''
                # 型号
                spxinghao = re.search(r'<dd title="型号：([\s\S].*?)" >', pageSource, re.S)
                if spxinghao is None:
                    spxinghao = re.search(r'<dd title="产品型号：([\s\S].*?)" >', pageSource, re.S)
                if spxinghao is not None:
                    spxinghao = spxinghao.group(1).strip()
                else:
                    spxinghao = ''
                # 旗舰店
                spShop = re.search(
                    r'<strong title="([\s\S].*?)">',
                    pageSource, re.S)
                if spShop is not None:
                    spShop = spShop.group(1).strip()
                    if ('旗舰店' not in spShop) and ('专营店' not in spShop) and ('专卖店' not in spShop) and (
                                '专区' not in spShop) and ('家电馆' not in spShop)and ('馆' not in spShop):
                        spShop = ''
                else:
                    spShop = ''
                # 累计评价
                # 取出商品
                # productplNum = re.search(r'(\d+)', response.url, re.S).group(1)
                # # productplNum=int(productplNum)
                # PJNumURL = Modle.YHDPLCountURL.format(productplNum)
                # yield Request(PJNumURL, callback=self.YHDplNum, headers=attrheaders, dont_filter=True,
                #               meta={'plurl': Url, 'Category': response.meta['Category'],
                #                     'SpShop': spShop, 'spname': spname, 'sppingpai': sppingpai, 'spxinghao': spxinghao,
                #                     'ec': response.meta['ec']})

                item = JDSpiderItem()
                item['ec'] = response.meta['ec']
                item['urls'] = Url
                item['spleibie'] = Category
                item['spName'] = spname
                item['sppingpai'] = sppingpai
                item['spxinghao'] = spxinghao
                item['spShop'] = spShop
                # item['spplNum'] = PJNum
                item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
                yield item
                print 'oo=====================存储成功=============================oo'
            else:
                print '页面加载内容为空：%s' % Url
        except Exception, e:
            index += 1
            print "不知道什么的错,可能代理问题，换个再尝试重新获取 %s" % e
            # if index>ErroNum:
            #     print "经过多试尝试，没有成功，有可能是其他问题"
            # 京东评论数

    def YHDplNum(self, response):
        item = JDSpiderItem()
        item['ec'] = response.meta['ec']
        item['urls'] = response.meta['plurl']
        item['spleibie'] = response.meta['Category']
        item['spName'] = response.meta['spname']
        item['sppingpai'] = response.meta['sppingpai']
        item['spxinghao'] = response.meta['spxinghao']
        item['spShop'] = response.meta['SpShop']
        item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
        pageSource = response.body
        mm = response.encoding
        if 'gb' in str(mm) or 'GB' in str(mm):
            pageSource = pageSource.decode('GBK')

        jsonHtml = pageSource.replace("jQuery5663852(", "")
        JDPLhtml = jsonHtml[:-2]
        # 序列化所获取的内容
        jsonPL = json.loads(JDPLhtml)
        PJNum = jsonPL['CommentsCount'][0]['CommentCount']
        # PJNum=PJNum.replace(',','')
        item['spplNum'] = PJNum
        print ' PJ end:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            time.time()))
        yield item

        # DD页面数
        def DDXPage(self, response):
            index = 0
            try:
                spurl = response.url
                plheaders = {"Referer": "" + spurl + ""}
                url = response.meta['urlpage']
                # 获取页数
                html = response.body
                mm = response.encoding
                if 'gb' in str(mm) or 'GB' in str(mm):
                    html = html.decode('GBK')
                # html = str(html).encode('utf-8')
                NumPage = re.search(r'<span class="pagnDisabled">(\d+?)</span>', html, re.S)
                if NumPage is not None:
                    NumPage = NumPage.group(
                        1).encode('utf-8')
                else:
                    com = re.compile(
                        r'<span class="pagnLink">[\s\S]*?<a[\s\S].*?>(\d+?)</a></span>',
                        re.S)
                    itemUrl = re.findall(com, html)
                    if itemUrl is not None:
                        NumPage = itemUrl[(len(itemUrl) - 1)]
                # NumPage = NumPage.replace('/', '')
                # print NumPage
                if NumPage is None:
                    NumPage = 0
                    print NumPage
                    if NumPage is None:
                        NumPage = str(0)
                # for i in range(1,int(NumPage)+1):
                list = url.split('&')

                for i in range(1, int(NumPage) + 1):
                    if len(list) < 3:
                        list.insert(1, 'page=' + str(i))

                    else:
                        list[1] = 'page=' + str(i)
                    urlpage = '&'.join(list)
                    print  u'当前品类url:' + urlpage
                    time.sleep(1)
                    yield Request(urlpage, callback=self.YMXUrlparse, headers=plheaders, dont_filter=True,
                                  meta={'pageurl': urlpage, 'Category': response.meta['Caterry'],
                                        'ec': response.meta['ec']})

                    # yield pageitem

            except Exception, e:
                print '可能连接超时，详情：' + e.message
                # 京东URL

        def DDUrlparse(self, response):
            print '开始URl加工\033[0;31;0m Time：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                time.time())) + '\033[0m'
            try:

                spurl = response.url

                attrheaders = {"Referer": "" + spurl + ""}
                # time.sleep(1)
                pageurl = response.meta['pageurl']
                html = response.body
                # 判断当前页面编码格式
                mm = response.encoding
                if 'gb' in str(mm) or 'GB' in str(mm):
                    html = html.decode('GBK')
                # html = str(html).encode('utf-8')
                # 第一步在取出页面内所有该品类的店铺的URL
                com = re.compile(
                    r'',
                    re.S)
                itemUrl = re.findall(com, html)
                if len(itemUrl) == 0:
                    com = re.compile(
                        r' ',
                        re.S)
                    itemUrl = re.findall(com, html)
                # mutex.acquire()
                print u'以下店铺URL来源' + pageurl

                if itemUrl is not None:
                    for spurl in itemUrl:
                        url = 'http:' + spurl
                        # url=' http://item.jd.com/10672650590.html'
                        print '当前店铺url：' + url
                        yield Request(url, callback=self.JDProductAttrubuteSpider, headers=attrheaders,
                                      dont_filter=True,
                                      meta={'dpurl': url, 'Category': response.meta['Category'],
                                            'ec': response.meta['ec']})
                        # yield  item
                        # 取页面数，进行多页加载
                        # mutex.release()

            except Exception, e:
                error = traceback.format_exc()
                print u"不知道什么错误：%s" % error
                # 第二步进入店铺内采集所需属性
                # 京东各属性字段

        def DDProductAttrubuteSpider(self, response):
            try:

                index = 0
                Url = response.url
                JDCateroy = response.meta['Category']
                attrheaders = {"Referer": "" + Url + ""}
                # time.sleep(1)
                html = response.body
                mm = response.encoding
                # if 'gb' in str(mm) or 'GB' in str(mm):
                html = html.decode(mm)
                pageSource = html.encode('utf-8')
                # 开始获取各属性值
                if pageSource is not None:
                    # 商品名称 有可能分几种情况
                    spname = re.search(r'<div class="sku-name">([\s\S]*?</)div>', pageSource, re.S)
                    if spname is not None:
                        spname = spname.group(1).lstrip().rstrip()
                        if '<img' in spname:
                            spname = re.search(r'/>([\s\S]*?)</', spname, re.S)
                            if spname is not None:
                                spname = spname.group(1).lstrip().rstrip()
                        else:
                            if '自营' in spname:
                                spname = re.search(r'/span>([\s\S]*?)</', spname, re.S)
                                spname = spname.group(1).strip()
                        spname = spname.replace('</', '').strip()
                    else:
                        spname = ''
                    # item['spName']=spname
                    # print   spname
                    if (JDCateroy == u'取暖电器') and ((u'暖器' in spname) or (u'暖气' in spname)):
                        JDCateroy = u'电暖器'
                    # 品牌
                    sppingpai = re.search(r'<dt>品牌</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                    if sppingpai is None:
                        sppingpai = re.search(
                            r'<ul id="parameter-brand"[\s\S]*?<li title=[\s\S].*?<a href[\s\S].*?>([\s\S]*?)</a>',
                            pageSource, re.S)
                    if sppingpai is not None:
                        sppingpai = sppingpai.group(1).strip()

                    else:
                        sppingpai = ''
                    # 型号
                    spxinghao = re.search(r'<dt>型号</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                    if spxinghao is None:
                        spxinghao = re.search(r'<dt>产品型号</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                    if spxinghao is not None:
                        spxinghao = spxinghao.group(1).strip()
                    else:
                        spxinghao = ''
                    # 旗舰店
                    spShop = re.search(
                        r'<div class="popbox-inner"[\s\S]*?<div class="mt">[\s\S]*?<h3>[\s\S]*?<a[\s\S].*?title="([\s\S].*?)"',
                        pageSource, re.S)
                    if spShop is None:
                        spShop = re.search(r'<div class="name"[\s\S]*?<a[\s\S]*?>([\s\S].*?)</a>', pageSource, re.S)

                    if spShop is not None:
                        spShop = spShop.group(1).strip()
                        if ('旗舰店' not in spShop) and ('专营店' not in spShop) and ('专卖店' not in spShop) and (
                                    '专区' not in spShop) and ('家电馆' not in spShop):
                            spShop = ''
                    else:
                        spShop = ''
                    # 累计评价
                    # 取出商品

                    productplNum = re.search(r'(\d+)', response.url, re.S).group(1)
                    # productplNum=int(productplNum)
                    PJNumURL = Modle.JDPLCountURL.format(productplNum)
                    yield Request(PJNumURL, callback=self.JDplNum, headers=attrheaders, dont_filter=True,
                                  meta={'plurl': Url, 'Category': response.meta['Category'],
                                        'SpShop': spShop, 'spname': spname, 'sppingpai': sppingpai,
                                        'spxinghao': spxinghao,
                                        'ec': response.meta['ec']})
                    print 'oo=====================存储成功=============================oo'
                else:
                    print '页面加载内容为空：%s' % Url
            except Exception, e:
                index += 1
                print "不知道什么的错,可能代理问题，换个再尝试重新获取 %s" % e
                # if index>ErroNum:
                #     print "经过多试尝试，没有成功，有可能是其他问题"
                # 京东评论数

        def DDplNum(self, response):
            item = JDSpiderItem()
            item['ec'] = response.meta['ec']
            item['urls'] = response.meta['plurl']
            item['spleibie'] = response.meta['Category']
            item['spName'] = response.meta['spname']
            item['sppingpai'] = response.meta['sppingpai']
            item['spxinghao'] = response.meta['spxinghao']
            item['spShop'] = response.meta['SpShop']
            item['writeTime'] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
            pageSource = response.body
            mm = response.encoding
            if 'gb' in str(mm) or 'GB' in str(mm):
                pageSource = pageSource.decode('GBK')

            jsonHtml = pageSource.replace("jQuery5663852(", "")
            JDPLhtml = jsonHtml[:-2]
            # 序列化所获取的内容
            jsonPL = json.loads(JDPLhtml)
            PJNum = jsonPL['CommentsCount'][0]['CommentCount']
            # PJNum=PJNum.replace(',','')
            item['spplNum'] = PJNum
            print ' PJ end:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                time.time()))
            yield item

"""
    def JDProductAttrubuteSpider(self, url2, JDEc, JDCateroy):
        try:
            print ' JDProductAttrubuteSpider end:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                time.time()))

            # for url2 in itemUrl:
            urlsWeb = "http:" + url2
            # urlsWeb='https://item.jd.hk/2256138.html'
            print urlsWeb
            index = 0
            ErroNum=2
            # 请求失败有可能是代理问题，还可以再请求几次
            while index < ErroNum:
                try:
                    session = self.Proxy()
                    # urlsWeb='http://item.jd.com/1643103810.html'
                    html = session.get(urlsWeb, timeout=10)
                    time.sleep(3)
                    pageSource = html.text
                    pageSource = str(pageSource)
                    # print  pageSource
                    if len(pageSource) < 50:
                        index += 1
                        continue
                    if '进口电器' == JDCateroy:
                        JDCateroy = ''

                    # 开始获取各属性值
                    if pageSource is not None:
                        # 商品名称 有可能分几种情况
                        spname = re.search(r'<div class="sku-name">([\s\S]*?</)div>', pageSource, re.S)
                        if spname is not None:
                            spname = spname.group(1).lstrip().rstrip()
                            if '<img' in spname:
                                spname = re.search(r'/>([\s\S]*?)</', spname, re.S)
                                if spname is not None:
                                    spname = spname.group(1).lstrip().rstrip()

                            else:
                                if '自营' in spname:
                                    spname = re.search(r'/span>([\s\S]*?)</', spname, re.S)
                                    spname = spname.group(1).strip()
                            spname = spname.replace('</', '').strip()
                        else:
                            spname = ''
                        # print   spname
                        if (JDCateroy == '取暖电器') and (('暖器' in spname) or ('暖气' in spname)):
                            JDCateroy = '电暖器'
                        # 品牌
                        sppingpai = re.search(r'<dt>品牌</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                        if sppingpai is None:
                            sppingpai = re.search(
                                r'<ul id="parameter-brand"[\s\S]*?<li title=[\s\S].*?<a href[\s\S].*?>([\s\S]*?)</a>',
                                pageSource, re.S)
                        if sppingpai is not None:
                            sppingpai = sppingpai.group(1).strip()

                        else:
                            sppingpai = ''
                        # print  sppingpai
                        # 型号
                        spxinghao = re.search(r'<dt>型号</dt><dd>([\s\S]*?)</dd>', pageSource, re.S)
                        if spxinghao is not None:
                            spxinghao = spxinghao.group(1).strip()
                        else:
                            spxinghao = ''
                        # print spxinghao
                        # 旗舰店
                        spShop = re.search(
                            r'<div class="popbox-inner"[\s\S]*?<div class="mt">[\s\S]*?<h3>[\s\S]*?<a[\s\S].*?title="([\s\S].*?)"',
                            pageSource, re.S)

                        if spShop is None:
                            spShop = re.search(r'<div class="name"[\s\S]*?<a[\s\S]*?>([\s\S].*?)</a>', pageSource,
                                               re.S)

                        if spShop is not None:
                            spShop = spShop.group(1).strip()
                            if ('旗舰店' not in spShop) and ('专营店' not in spShop) and ('专卖店' not in spShop) and (
                                '专区' not in spShop):
                                spShop = ''
                        else:
                            spShop = ''
                        # print  spShop
                        # 累计评价
                        # # 取出商品
                        # productNum = re.search(r'(\d+)', urlsWeb, re.S).group(1)
                        # productNum = int(productNum)
                        # plNum = self.JDPJ(productNum)

                        #mutex.acquire()
                        # 输出
                        # print ' Time：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                        #     time.time())) + '\t\tReport：' + str_name + 'Test Read  spName:\033[0;36;0m%s\033[0m  sppingpai：\033[0;35;0m%s\033[0m xinghao: %s;splum %s;cateroy: %s;urlWeb: %s;JDEc: %s ,spShop: %s Information' % (
                        #     spname, sppingpai, spxinghao, plNum, JDCateroy, urlsWeb, JDEc, spShop)
                        # 释放锁
                        #mutex.release()
                        result={'cateroy':JDCateroy,'spname':spname,'spxinghao':spxinghao,'sppingpai':sppingpai,'spec':JDEc}
                        return result

                        # # 实例化存储
                        # redisData = RedisD(spname, sppingpai, spxinghao, spShop, plNum, JDCateroy, urlsWeb, JDEc)
                        # redisData.SaveRedis()
                        print 'oo=====================存储成功============================='
                        break
                except Exception, e:
                     index += 1
                     print "不知道什么的错,可能代理问题，换个再尝试重新获取 %s" % e
                     if index > ErroNum:
                        print "经过多试尝试，没有成功，有可能是其他问题"


        except Exception, e:
            print e
        print ' JDProductAttrubuteSpider end:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            time.time()))
"""




