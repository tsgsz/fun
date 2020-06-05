import redis
import logging
import os
import urllib.request
import datetime
import time
import random
import sys
import json

class AutoProxy:
    """
    Http Proxy代理类。自动获取代理ip，并存入redis。
    usage:
    proxy = AutoProxy()
    ip,port = proxy.pool_get_proxy()
    """
    #   TODO  获取余额接口。
    #   http://web.http.cnapi.cc/index/index/get_my_balance?neek=40412&appkey=3dba1eee4edbed4a57e8dd4be552a35e
    
    redis_key = {
        0: "http",  
        1: "https"
    }
    expire_time_shift = 30  # 用来弥补，本地服务器与代理接口服务器的时间差  

    proxies = [
        None
    ]
    
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
    }
    
    zhima_urls = [
        'http://http.tiqu.alicdns.com/getip3?num={0}&type=2&pro=&city=0&yys=0&port=1&time=1&ts=1&ys=1&cs=1&lb=1&sb=0&pb=4&mr=1&regions=&gm=4',
        'http://http.tiqu.alicdns.com/getip3?num={0}&type=2&pro=&city=0&yys=0&port=11&time=1&ts=1&ys=1&cs=1&lb=1&sb=0&pb=4&mr=1&regions=&gm=4'
    ]
    
    _agent = [
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    ]
    
    def __init__(self, redis_host = 'localhost', redis_port = 6379, redis_passwd = None, min_proxy_in_pool = 1, proxy_get_num = 1):
        self.logger = logging.getLogger(str(os.getpid())+' - ' + self.__class__.__name__)
        self.redis_proxy = redis.Redis(
            host = redis_host,
            port = redis_port,
            db = 0,
            password = redis_passwd
        )
        self.min_proxy_in_pool = min_proxy_in_pool # 池子里最少要求的代理数量
        self.proxy_get_num = proxy_get_num # 每次从接口获取的代理数量
        
    

    def pool_get_proxy(self, retry=3, https=0):
        """
        从redis代理池中获取一个代理
        retry: 拿不到代理时的重试次数
        https：0|1, 0HTTP  1HTTPS
        """
        #先清除过期的代理数据
        self.pool_clear_expire(https=https)
        count = self.redis_proxy.zcard(self.redis_key[https])
        if count < self.min_proxy_in_pool:
            #池子里小于min_proxy_in_pool时，自动从接口获取
            sleeptime = random.randrange(1000, 5000)            
            self.logger.info(sys._getframe().f_code.co_name+' - ' + u'代理池数量不够，考虑从芝麻获取代理。sleep毫秒：'+str(sleeptime))
            time.sleep(sleeptime/1000)
            count = self.redis_proxy.zcard(self.redis_key[https])
            if count >= self.min_proxy_in_pool:
                #数量达标了，可能是其他线程返回了.不需要再从芝麻获取了
                self.logger.info(sys._getframe().f_code.co_name+' - ' + u'代理池数量sleep之后够了。')
                return self.pool_get_proxy(retry=retry-1, https=https)    # 重新获取

            if retry > 0:
                self.get_proxy_fromzhima(https=https)
                #暂停1
                return self.pool_get_proxy(retry=retry-1, https=https)    # 重新获取
            else:
                # pass    # TODO 获取代理失败
                self.logger.error(sys._getframe().f_code.co_name+' - ' + u'从芝麻获取代理失败。')

        else:
            index = random.randint(0, count-1)
            proxy = self.redis_proxy.zrange(self.redis_key[https], index, index)
            jsonObj = eval(proxy[0])

            ip = jsonObj['ip'] 
            port = jsonObj['port'] 
            return ip, port, jsonObj

    def pool_remove_porxy(self, ip, port, expire, seconds_left, https=0):
        
        proxy = {'ip': ip, 'port': port, 'expire': expire}
        expire_stamp = self.timestringtotimestamp(expire) - self.expire_time_shift
        self.logger.info(sys._getframe().f_code.co_name + ' - ' + u'' + str(proxy) + ' seconds_left:'+str(seconds_left))    
        
        self.redis_proxy.zremrangebyscore(self.redis_key[https], expire_stamp, expire_stamp)  


    def pool_add_proxy(self, ip, port, expire, seconds_left, https=0):
        """
        将代理加入到redis中
        """
        proxy = str({'ip':ip, 'port':port, 'expire':expire})
        expire_stamp = self.timestringtotimestamp(expire) - self.expire_time_shift
                
        self.logger.info(sys._getframe().f_code.co_name + ' - ' + u'' + str(proxy) + ' seconds_left:'+str(seconds_left))    
        
        self.redis_proxy.zadd(self.redis_key[https], {proxy: expire_stamp})   
        # 坑： python redis zadd的参数，跟 标准redis语法是反的
        # 标准是 redis 127.0.0.1:6379> ZADD KEY_NAME SCORE1 VALUE1.. SCOREN VALUEN
        # python redis 是 zadd(key,value,score)
        # 数量  zcard(key)
        # 查看  ZRANGE WejoyProxyPOOL 0 10 WITHSCORES

        # 移除过期的  ZREMRANGEBYSCORE WejoyProxyPOOLHTTP 0 1523450011
    
    def pool_clear_expire(self, https=0):
        """
        移除过期的proxy。expire_stamp是当前时间戳
        """
        cur_time = datetime.datetime.today()
        expire_stamp = float(int(time.mktime(cur_time.timetuple())))
        self.redis_proxy.zremrangebyscore(self.redis_key[https], 0, expire_stamp)   
        
    def get_proxy_fromzhima(self, https=0):
        proxy_api_url = self.zhima_urls[https].format(self.proxy_get_num)
        try:
            self.logger.info(sys._getframe().f_code.co_name+' - '+u'请求代理：'+proxy_api_url)
            req = urllib.request.Request(proxy_api_url, None, self.headers)            
        except Exception as err:
            self.logger.exception(sys._getframe().f_code.co_name+' - '+u'发生错误。'+proxy_api_url)
            return
        response = urllib.request.urlopen(req)
        jsonData = response.read().decode('utf-8')
        print(jsonData)
        jsonObj = json.loads(jsonData)
        success = False
        if 'success' in jsonObj:
            success = jsonObj['success']

        if 'data' in jsonObj:
            data = jsonObj['data']
            data_count = len(data)  # data_count 为0 的时候 没有获取到代理ip            
            self.logger.info(sys._getframe().f_code.co_name+' - '+u'获取到代理ip数量'+str(len(data)))
            for proxy in data:
                ip = proxy['ip']
                port = proxy['port']
                expire_time = proxy['expire_time']                
                seconds_left = self.seconds_left(expire_time)
                self.pool_add_proxy(ip, port, expire_time,seconds_left, https=https)

    def seconds_left(self,proxy_valid_time):
        proxy_time = datetime.datetime.strptime(proxy_valid_time, "%Y-%m-%d %H:%M:%S")
        cur_time = datetime.datetime.today()
        delta = proxy_time-cur_time
        return delta.total_seconds()
    
    def timestringtotimestamp(self,timestr):
        proxy_time = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        un_time = float(int(time.mktime(proxy_time.timetuple())))
        return un_time
    
if __name__ == '__main__':
    # 试图获取列表
    proxy = AutoProxy()
    print(proxy.pool_get_proxy())