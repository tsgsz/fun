import random  
import scrapy
import time
from scrapy.http import HtmlResponse


class BrowserSimulateMiddleware:
    
    @classmethod
    def from_settings(cls, settings):
        return cls()
    
    """docstring for RandomProxyMiddleWare"""  
    def process_request(self, request, spider):
        pass


    def process_response(self, request, response, spider):  
        """
        三个参数:
        # request: 响应对象所对应的请求对象
        # response: 拦截到的响应对象
        # spider: 爬虫文件中对应的爬虫类 WangyiSpider 的实例对象, 可以通过这个参数拿到 WangyiSpider 中的一些属性或方法
        """

        #  对页面响应体数据的篡改, 如果是每个模块的 url 请求, 则处理完数据并进行封装
        if hasattr(spider, 'browser'):
            spider.logger.debug('使用browser')
            spider.browser.get(url=request.url)
            js = "window.scrollTo(0,document.body.scrollHeight)"
            spider.browser.execute_script(js)
            time.sleep(1)     # 等待加载,  可以用显示等待来优化.
            row_response= spider.browser.page_source
            return HtmlResponse(
                url=spider.browser.current_url,
                body=row_response,encoding="utf8",
                request=request
            )   # 参数url指当前浏览器访问的url(通过current_url方法获取), 在这里参数url也可以用request.url
                                                                                                                     # 参数body指要封装成符合HTTP协议的源数据, 后两个参数可有可无
        else:
            return response    # 是原来的主页的响应对象
