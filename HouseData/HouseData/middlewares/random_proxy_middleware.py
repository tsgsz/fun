import random  
import scrapy  
from scrapy import signals
from ..proxies import AutoProxy

class RandomProxyMiddleware:
    
    def __init__(self, proxy):
        self.auto_proxy = proxy
    
    @classmethod
    def from_settings(cls, settings):
        proxy = AutoProxy(
            redis_host = settings['REDIS_HOST'],
            redis_port = settings['REDIS_PORT'],
            redis_passwd = settings['REDIS_PASSWD'],
            min_proxy_in_pool = settings['MIN_PROXY_IN_POOL'],
            proxy_get_num = settings['PROXY_GET_NUM']
        )
        
        return cls(proxy)
    
    """docstring for RandomProxyMiddleWare"""  
    def process_request(self, request, spider):  
        '''对request对象加上proxy'''  
        proxy = self.get_random_proxy()  
        request.meta['proxy'] = proxy   


    def process_response(self, request, response, spider):  
        '''对返回的response处理'''  
        # 如果返回的response状态不是200，重新生成当前request对象  
        if response.status != 200:  
            proxy = self.get_random_proxy()  
            print("this is response ip:"+proxy)  
            # 对当前reque加上代理  
            request.meta['proxy'] = proxy   
            return request  
        return response  

    def get_random_proxy(self):  
        '''随机从文件中读取proxy'''  
        ip, port, _ = self.auto_proxy.pool_get_proxy(1)
        proxy = "http://%(host)s:%(port)s" % {
            "host" : ip,
            "port" : port,
        }
        return proxy