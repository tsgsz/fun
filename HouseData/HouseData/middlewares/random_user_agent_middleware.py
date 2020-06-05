import random  
import scrapy  
import json
from scrapy import signals

class RandomUserAgentMiddleware:  
    """docstring for ProxyMiddleWare"""  
    
    def process_request(self,request, spider):  
        '''对request对象加上proxy'''  
        if len(spider.allowed_domains) >= 1:
            request.headers['Referer'] = "http://www.{0}".format(spider.allowed_domains[0])
        else:
            request.headers['Referer'] = "http://www.baidu.com"
            
        request.headers["User-Agent"] = self.get_random_agent()
        
    def process_response(self, request, response, spider):  
        '''对返回的response处理'''  
        # 如果返回的response状态不是200，重新生成当前request对象  
        if response.status != 200:  
            self.process_request(request, spider)
            return request  
        return response  

    def get_random_agent(self):  
        '''随机从文件中读取agent'''  
        while 1:  
            with open('./useragents.txt', 'r') as f:  
                agents = f.readlines()
            if agents:  
                break  
            else:  
                time.sleep(1)  
        agent = json.loads(random.choice(agents).strip()) 
        return agent 