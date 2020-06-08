import scrapy
import time
import random

from scrapy.downloadermiddlewares.retry import RetryMiddleware as SysRetry


class RetryMiddleware(SysRetry):

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            time.sleep(random.randint(10, 20))
            spider.logger.warning('返回值异常, 进行重试...')
            return self._retry(request, reason, spider) or response
        return response


    def process_exception(self, request, exception, spider):
        #if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
        if not request.meta.get('dont_retry', False):
            time.sleep(random.randint(3, 5))
            
            spider.logger.warning('连接异常, 进行重试...')
            spider.logger.info('异常如下:', exception)
            
            return self._retry(request, exception, spider)
