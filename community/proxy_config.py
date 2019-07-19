# -*- coding: utf-8 -*-
import os

# ./crawler_dockerstore/community
thisFileDir = os.path.split(os.path.realpath(__file__))[0]
# we have to modify the tail if we change the dir of this python file
# print thisFileDir
tail = 29
rootPath = thisFileDir[0:-tail]
if rootPath[-1] != "/":
    message = "Error root path [%s]\n\tPlease check whether you changed the path of current file" % rootPath
    # raise Exception(message)
# print rootPath

data_root_path = rootPath
# print rootPath

proxy_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
}
proxy_base_url = "http://www.xicidaili.com/nn/"
page_target_url = "https://store.docker.com/api/content/v1/products/search?q=%2B&source=community&type=image%2Cbundle&page=3&page_size=100"
target_docker_name = "microsoft/dotnet"

target_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Cache-Control': 'max-age=0',
    # 'Connection': 'keep-alive',
    # 'Cookie': 'ajs_user_id=null; ajs_group_id=null; _ga=GA1.2.517667667.1526523301; ajs_anonymous_id=%22513f05e7-2732-4124-aa74-3dfbee43c418%22; _mkto_trk=id:929-FJL-178&token:_mch-docker.com-1526523307626-79689; _gid=GA1.2.215116819.1526888391; mp_82c8a87cfaa9219dff0e89ef744d8357_mixpanel=%7B%22distinct_id%22%3A%20%221636be2346c860-00d080ff043e37-33657f07-13c680-1636be2346d3cd%22%2C%22mp_lib%22%3A%20%22Segment%3A%20web%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%7D',
    'DNT': '1',
    'Host': 'store.docker.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
}

proxy_path = rootPath + "data/dockerstore/community/proxy/json/proxy.json"