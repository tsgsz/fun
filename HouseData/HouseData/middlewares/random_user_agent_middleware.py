import random  
import scrapy  
import json
from scrapy import signals

class RandomUserAgentMiddleware:  
    """docstring for ProxyMiddleWare""" 
    
    user_agents = [
        {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6"},
        {"User-Agent":"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11"},
        {"User-Agent":"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)"},
        {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0"},
        {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36"},
        {"User-Agent":"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},
        {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},
        {"User-Agent":"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0"},
        {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"},
        {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"},
        {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"},
        {"User-Agent":"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11"},
        {"User-Agent":"Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11"}
    ]
    
    
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
        # while 1:  
            #with open('./useragents.txt', 'r') as f:  
                #agents = f.readlines()
            #if agents:  
                #break  
            #else:  
                #time.sleep(1)  
        #agent = json.loads(random.choice(agents).strip()) 
        agent = random.choice(self.user_agents)
        return agent 