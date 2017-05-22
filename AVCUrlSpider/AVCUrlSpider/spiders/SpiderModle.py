# -*-coding:utf-8-*-
import  redis
class Modle:
    # 不需要的品类
    NoList = ['酸奶机', '煮蛋器', '插座', '电话机', '收录/音机', '生活电器配件', '扫地机器人','其它生活电器']
    # 取代理Ip服务器
    rconnection_Proxy = redis.Redis(host='117.122.192.50', port=6479, db=0)
    # 代理IP
    redis_key_proxy = "proxy:iplist"
    #数据存储
    redis_Server=redis.Redis(host='192.168.2.174', port=6379, db=0)
    redis_key_list="JDList:item"
    redis_key_data="Ecurl:item"
    reids_key_pageList="PageList:item"
    reids_key_wys='wys:item'
    #各电商URL入口
    JDList='https://dc.3.cn/category/get?callback=getCategoryCallback'
    #京东评论内容
    JDPLURL='https://club.jd.com/comment/skuProductPageComments.action?callback&productId={0}&score=0&sortType=5&page={1}&pageSize=10&isShadowSku=0'
    #京东评论数量
    JDPLCountURL='http://club.jd.com/comment/productCommentSummaries.action?referenceIds={0}&callback=jQuery5663852&_=1491878035537'
    #SN评论数量
    SNPLCountURL='http://review.suning.com/ajax/review_satisfy/general-{0}-{1}-----satisfy.htm?callback=satisfy'
    #SN评论内容
    SNPLURL='https://review.suning.com/ajax/review_lists/general-{0}-0000000000-total-1-default-10-----reviewList.htm?callback=reviewList'
    #GM 评论数量
    GMPLCountURL='http://ss.gome.com.cn/item/v1/d/m/store/{0}/N/15030100/150301001/null/flag/item/allStores'
    #DD 评论数量+评论内容
    DDPLCountURL ='http://product.dangdang.com/index.php?r=callback/comment-list&productId={0}'
    #YHD
    YHDPLCountURL='http://e.yhd.com/front-pe/productExperience/proExperienceAction!ajaxView_pe.do?product.id={0}'