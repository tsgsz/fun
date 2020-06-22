 # scrapy crawl beike -a cities=bj -s JOBDIR=crawls/beike > profile.log
 # scrapy crawl beike_region -s JOBDIR=crawls/beike > profile.log
 # scrapy crawl beike_real_estate -a cities=bj -s JOBDIR=crawls/beike_real_estate > beike_real_estate.log
 # scrapy crawl beike_community -a cities=bj -s JOBDIR=crawls/beike_community > beike_community.log
 # scrapy crawl beike_rent -a cities=bj -s JOBDIR=crawls/beike_rent > beike_rent.log
 scrapy crawl beike_2nd_house -a cities=bj -s JOBDIR=crawls/beike_house > beike_house.log
