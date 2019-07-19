# -*- coding: utf-8 -*-
import re
from threading import Thread

import requests
import time
# from BeautifulSoup import *
from bs4 import BeautifulSoup
import json

from datetime import datetime
import threading
import crawler_config
import os
from logging_initialize import *
import mysql_helper
import proxy_helper
import proxy_config

def get_html(url, params=None, post_data=None):
    """
    get the html by url and params
    :param url: is target url
    :param params: is a dict of params and they have been encoded
    :param post_data: the data(dict) for post, this param will be None when Get method
    :return: a text of html
    """
    headers = proxy_config.target_headers
    proxies = proxy_helper.get_available_random_proxy()
    if params is not None:
        url += "?"
        for key in params.keys():
            url += "%s=%s&" % (str(key), str(params[key]))
        url = url[0:-1]
    if post_data is not None:
        html = requests.post(url, data=post_data, proxies=proxies)
    else:
        # print "url: [%s]" % url
        # print "proxies: %s" % proxies
        # logging.info("target url: [%s], proxies: [%s]" % (url, proxies))
        html = requests.get(url, proxies=proxies, headers=headers)
    # print "url: [%s]\nhtml.text: [%s]" % (url, html.text.encode("utf-8"))
    return html.text


def get_json_data(url, params=None, post_data=None):
    """
    get the json data by url and params(Note: just for the url whose response is a json)
    :param url: is target url
    :param params: is a dict of params has been encoded
    :param post_data: the data(dict) for post, this param will be None when Get method
    :return: a string of json
    """
    json_data = get_html(url, params=params, post_data=post_data)
    # why while statement？
    # because the url have no response sometimes(network or some errors of server)
    # RetryTimes = crawler_config.retry_times
    while json_data is None or json_data == "":
        # RetryTimes -= 1
        # if RetryTimes < 0:
        #     logging.error("Thread: [%s] Retry url: [%s], params: [%s] fail, RetryTimes: [%d]", thread_name, url, params, crawler_config.retry_times)
        #     json_data = None
        #     break
        thread_name = threading.current_thread
        logging.warning("Thread: [%s] Retry url: [%s], params: [%s] post_data: [%s]", thread_name, url, params, post_data)
        print "Warnning: Retry %s" % url
        time.sleep(2)
        json_data = get_html(url, params=params, post_data=post_data)
    # if json_data is None:
    #     thread_name = threading.current_thread
    #     logging.warning("Thread: [%s] Error url: [%s], params: [%s]", thread_name, url, params)
    json_data = json_data.encode("utf-8")
    return json_data


def get_time():
    """
    :return: the localtime at present
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def get_tags_github(docker_github_url):
    """
    get tags from github by url
    :param docker_github_url: the url of docker in github [url format: "https://github.com/dotnet/dotnet-docker"]
    :return: a list of tags
    """
    html = requests.get(docker_github_url).text
    if str(html) == "Not Found":
        return None
    # print html
    soup = BeautifulSoup(html)
    # get the list of divs, the first element is grandpa of tags
    xml_divs_grandpa_li = soup.findAll('div',  {
        'class': "select-menu-list select-menu-tab-bucket js-select-menu-tab-bucket",
        'data-tab-filter': 'tags'
    })
    if xml_divs_grandpa_li.__len__() == 0:
        return None
    # get the parent of tags
    xml_div_parent = xml_divs_grandpa_li[0].find('div')
    # get the tags
    if xml_div_parent is None:
        return None
    xml_tags = xml_div_parent.findAll('a')
    tags = list()
    for xml_tag in xml_tags:
        # get the name of tag
        tag = xml_tag.getText()
        tags.append(tag)
    return tags


def get_versions2dockerfiles_urls_github(docker_github_url):
    """
    get urls of dockerfiles from github
    :param docker_github_url: the url of docker in github [url format: "https://github.com/dotnet/dotnet-docker"]
    :return: a dict <tag, url>
    """
    tags = get_tags_github(docker_github_url)
    dockerfile_urls = dict()
    for tag in tags:
        dockerfile_url = os.path.join(docker_github_url, "blob", tag, "Dockerfile")
        tag_page_url = os.path.join(docker_github_url, "tree", tag)
        urls = {"dockerfile_url": dockerfile_url, "tag_page_url": tag_page_url}
        dockerfile_urls[tag] = urls
    return dockerfile_urls

# def get_docker_tags_urls_github(docker_github_url):
#     """
#     get urls of tags from github
#     :param docker_github_url: the url of docker in github [url format: "https://github.com/dotnet/dotnet-docker"]
#     :return: a dict <tag, url>
#     """
#     tags = get_tags_github(docker_github_url)
#     tag_urls = dict()
#     for tag in tags:
#         tag_url = "%s/%s/%s" % (docker_github_url, "tree", tag)
#         tag_urls[tag] = tag_url
#     return tag_urls
#


def get_link_url(docker_name):
    """
    get the link of target docker named docker_name(format: microsoft/dotnet)
    :param docker_name: is name of target docker
    :return: the link of target docker, generally, the link is a github url
    """
    url = os.path.join(crawler_config.community_docker_base_url, docker_name, crawler_config.auto_build_suffix)
    json_data = get_json_data(url)
    data = json.loads(json_data)
    github_url = data["repo_web_url"]
    return github_url


def get_docker_names(names_path):
    """
    get the names of dockers in the file
    :param names_path: the path of docker names
    :return: a list of docker names
    """
    with open(names_path, "r") as fp:
        docker_names = json.load(fp)
        return list(docker_names)


def get_all_docker_names():
    """
    get all docker names
    :return: a list of all docker names
    """
    return get_docker_names(crawler_config.all_docker_names_json_path)


def get_new_docker_names():
    """
    get new docker names
    :return: a list of new docker names
    """
    return get_docker_names(crawler_config.new_docker_names_json_path)


def get_updated_docker_names():
    """
    get new docker names
    :return: a list of new docker names
    """
    return get_docker_names(crawler_config.updated_docker_names_json_path)


def get_modified_docker_names():
    """
    get modified docker names(including new and updated docker names)
    :return: a list of modified docker names
    """
    # Notice: extend will return None for any list
    # extend can merge a list to another list but return None
    # print get_new_docker_names().extend(get_updated_docker_names())
    # print get_updated_docker_names().extend(get_new_docker_names())
    return get_updated_docker_names() + get_new_docker_names()


def write_object_to_file(file_name, target_object):
    """
    write the object to file with json(if the file exists, this function will overwrite it)
    :param file_name: the name of new file
    :param target_object: the target object for writing
    :return: True if success else False
    """
    dirname = os.path.dirname(file_name)
    find_and_create_dirs(dirname)
    try:
        with open(file_name, "w") as f:
            json.dump(target_object, f, skipkeys=False, ensure_ascii=False, check_circular=True, allow_nan=True, cls=None, indent=True, separators=None, encoding="utf-8", default=None, sort_keys=False)
    except Exception, e:
        message = "Write [%s...] to file [%s] error: json.dump error" % (str(target_object)[0:10], file_name)
        logging.error("%s\n\t%s" % (message, e.message))
        return False
    else:
        # logging.info(get_time() + ": Write " + self.docker_save_path + doc_file_name + ".json")
        logging.info("Write %s" % file_name)
        return True


# def write_tags_string_to_file(file_name, tags_str):
#     """
#     write the object to file with json(if the file exists, this function will overwrite it)
#     :param file_name: the name of new file
#     :param target_object: the target object for writing
#     :return: True if success else False
#     """
#     dirname = os.path.dirname(file_name)
#     find_and_create_dirs(dirname)
#     try:
#         with open(file_name, "w") as f:
#             f.write(tags_str)
#     except Exception, e:
#         message = "Write tags [%s] to file [%s] error" % (tags_str, file_name)
#         logging.error("%s\n\t%s" % (message, e.message))
#         return False
#     else:
#         # logging.info(get_time() + ": Write " + self.docker_save_path + doc_file_name + ".json")
#         logging.info("Write %s" % file_name)
#         return True


def format_page(raw_page):
    """
    format the raw page
    :param raw_page: raw page
    :return: formatted page
    """
    page = dict()
    page["count"] = raw_page["count"]
    raw_summaries = raw_page["summaries"]
    docker_names = list()
    for raw_summary in raw_summaries:
        docker_names.append(raw_summary["name"])
    page["docker_names"] = docker_names
    return page


def convert_raw_time2ints(time_str):
    if time_str is None:
        logging.warning("time_str: %s is illegal, set to default: [%s]'", time_str, crawler_config.default_time_of_docker_or_version)
        time_str = crawler_config.default_time_of_docker_or_version

    num_strs = re.split("-|T|:|\.|Z", str(time_str), 7)
    nums = list()
    # print time_str, num_strs
    for i in range(0, 7):
        try:
            if num_strs[i] == '':
                logging.warning("time_str: %s --> nums_strs: %s --> [%d] is ''", time_str, num_strs, i)
                num_strs[i] = '0'
            num = int(num_strs[i])
            nums.append(num)
        except IndexError:
            logging.error("time_str: %s --> nums_strs: %s is illegal for index[%d]", time_str, num_strs, i)
    # print nums
    # return datetime(nums[0], nums[1], nums[2], nums[3], nums[4], nums[5])
    return nums


def convert_ints2datetime(nums):
    return datetime(nums[0], nums[1], nums[2], nums[3], nums[4], nums[5], nums[6])


def format_docker(raw_docker):
    """
    format the raw docker
    :param raw_docker:
    :return: formatted docker
    """
    docker = dict()
    if "is_automated" not in raw_docker:
        logging.warning("docker [%s] has no attribute ['is_automated'], it's not a docker", raw_docker)
        return None
    docker["is_automated"] = raw_docker["is_automated"]
    docker["last_updated"] = convert_raw_time2ints(raw_docker["last_updated"])
    docker["short_description"] = raw_docker["description"]
    docker["full_description"] = raw_docker["full_description"]
    # print docker["full_description"]
    return docker


def format_docker_remain_all_info(raw_docker):
    """
    format the raw docker, remain all info of raw_docker
    :param raw_docker:
    :return: formatted docker
    """
    # docker = dict()
    if "is_automated" not in raw_docker:
        logging.warning("docker [%s] has no attribute ['is_automated'], it's not a docker", raw_docker)
        return None
    # docker["is_automated"] = raw_docker["is_automated"]
    raw_docker["last_updated"] = convert_raw_time2ints(raw_docker["last_updated"])
    # docker["short_description"] = raw_docker["description"]
    # docker["full_description"] = raw_docker["full_description"]
    raw_docker["short_description"] = raw_docker["description"]
    return raw_docker


def format_dockerfile(raw_dockerfile):
    """
    TODO: format the raw dockerfile
    :param raw_dockerfile: raw dockerfile
    :return: formatted dockerfile
    """
    return raw_dockerfile


def format_docker_versions(raw_docker_versions):
    """
    format the row docker versions
    :param raw_docker_versions: raw docker versions
    :return: formatted dockerfile
    """
    docker_versions = list()
    for raw_docker_version in raw_docker_versions:
        docker_version = dict()
        docker_version["name"] = raw_docker_version["name"]
        docker_version["full_size"] = raw_docker_version["full_size"]
        # if raw_docker_version["last_updated"] is None:
        #     raise Exception(docker_version)
        docker_version["last_updated"] = convert_raw_time2ints(raw_docker_version["last_updated"])
        docker_versions.append(docker_version)
    return docker_versions


def format_docker_tags(raw_docker_tags):
    """
    format the raw docker tags
    :param raw_docker_tags: raw docker tags
    :return: formatted docker tags(make sure the docker tags is a dict)
    """
    # docker_tags = raw_docker_tags
    return raw_docker_tags



# def get_all_docker_names(docker_name_path):
#     """
#     TODO: get all docker names from file
#     :param docker_name_path: the path of docker names
#     :return: a list of docker names
#     """
#     return list()


def get_community_docker_url(docker_name):
    """
    get community docker url
    :param docker_name: the name of target docker name
    :return: a string of url
    """
    url = os.path.join(crawler_config.community_docker_base_url, docker_name)
    return url


def get_community_dockerfile_url(docker_name):
    """
    get community dockerfile url
    :param docker_name: the name of target docker name
    :return: a string of url
    """
    url = os.path.join(crawler_config.community_docker_base_url, docker_name, "dockerfile")
    return url


def get_community_docker_versions_url(docker_name):
    """
    get community docker versions url
    :param docker_name: the name of target docker name
    :return: a string of url
    """
    url = os.path.join(crawler_config.community_docker_base_url, docker_name, "tags")
    return url


def get_community_dockerfile(docker_name):
    """
    get dockerfile from remote and format it
    :param docker_name: the name of target docker
    :return: object of dockerfile(loaded by json) formatted
    """
    dockerfile_url = get_community_dockerfile_url(docker_name)
    json_dockerfile = get_json_data(dockerfile_url)
    if check_json_format(json_dockerfile) is False:
        logging.error("dockerfile [%s] can not be got by url, json String: [%s]", docker_name, json_dockerfile)
        return None
    raw_dockerfile = json.loads(json_dockerfile)
    dockerfile = format_dockerfile(raw_dockerfile)
    return dict(dockerfile)


def check_json_format(raw_msg):
    """
    check a msg if could be decoded by json
    :param raw_msg: the raw msg
    :return:
    """
    if isinstance(raw_msg, str):
        try:
            json.loads(raw_msg, encoding='utf-8')
        except ValueError:
            return False
        return True
    else:
        return False


def get_community_docker(docker_name):
    """
    get docker from remote and format it
    :param docker_name: the name fo target docker
    :return: object of docker formatted
    """
    docker_url = get_community_docker_url(docker_name)
    json_docker = get_json_data(docker_url)
    if check_json_format(json_docker) is False:
        logging.error("docker [%s] can not be got by url, json String: [%s]", docker_name, json_docker)
        return None
    raw_docker = json.loads(json_docker)
    docker = format_docker_remain_all_info(raw_docker)
    return docker


def get_community_docker_versions(docker_name):
    """
    get docker version from remote and format it
    :param docker_name: the name fo target docker
    :return: a list of docker versions formatted
    """
    docker_versions_url = get_community_docker_versions_url(docker_name)
    page_size = 100
    page = 0
    params = {
        "page": page,
        "page_size": page_size
    }
    # /?page=1&page_size=250
    raw_docker_versions = list()
    while True:
        params["page"] += 1
        json_docker_versions_page = get_json_data(docker_versions_url, params)
        if check_json_format(json_docker_versions_page) is False:
            logging.error("docker versions[%s] can not be got by url, json String:[%s]", docker_name, json_docker_versions_page)
            continue
        raw_docker_versions_page = dict(json.loads(json_docker_versions_page))
        # print raw_docker_versions_page
        if "results" not in raw_docker_versions_page.keys():
            # there is no any version now
            break
        for raw_docker_version in raw_docker_versions_page["results"]:
            raw_docker_versions.append(raw_docker_version)
        if raw_docker_versions_page["results"].__len__() != page_size:
            break
    # print docker_name
    # print raw_docker_versions
    docker_versions = format_docker_versions(raw_docker_versions)
    return docker_versions


def get_old_community_docker_updated_time(docker_name):
    """
    get old docker
    :param docker_name: the name of target docker
    :return: object of docker(loaded by json)
    """
    # read data from database
    return mysql_helper.get_docker_database(docker_name)


def find_and_create_dirs(dir_name):
    """
    find dir, create it if it doesn't exist
    :param dir_name: the name of dir
    :return: the name of dir
    """
    if os.path.exists(dir_name) is False:
        os.makedirs(dir_name)
    return dir_name


def get_all_old_docker_names(i=None):
    """
    get all old docker names from database
    :return: a list of all old docker names
    """
    path = crawler_config.all_docker_names_json_path + str(i)
    # path = os.path.join(crawler_config.dockers_json_dir, fname)
    if os.path.exists(path) is False:
        return list()
    with open(path, 'r') as f:
        docker_names = json.load(f)
    # return docker
    return docker_names
    # return mysql_helper.get_all_docker_names()


def generate_docker_fname(docker_name):
    """
    generate the name of file for docker
    :param docker_name: the docker name
    :return: a string of docker_name replaced "/" by some string(such as "#")
    """
    replaced_name = str(docker_name).replace("/", "#")
    fname = "%s.json" % replaced_name
    return fname


def generate_dockerfile_fname(docker_name, timestamp=None):
    """
    generate the name of file for dockerfile
    :param docker_name: the docker name
    :param timestamp: the timestamp of current updating
    :return: a string of docker_name replaced "/" by some string(such as "#")
    """
    # get_time()
    if timestamp is None:
        timestamp = crawler_config.timestamp
    replaced_name = str(docker_name).replace("/", "#")
    fname = "%s_dockerfile_%s.json" % (replaced_name, timestamp)
    return fname


def generate_docker_versions_fname(docker_name):
    """
    generate the name of file for docker
    :param docker_name: the docker name
    :return: a string of docker_name replaced "/" by some string(such as "#")
    """
    replaced_name = str(docker_name).replace("/", "#")
    fname = "%s_versions.json" % replaced_name
    return fname


def generate_docker_tags_fname(docker_name):
    """
    generate the name of file for docker
    :param docker_name: the docker name
    :return: a string of docker_name replaced "/" by some string(such as "#")
    """
    replaced_name = str(docker_name).replace("/", "#")
    fname = "%s_tags.json" % replaced_name
    return fname


def get_docker_json_from_file(docker_name):
    fname = generate_docker_fname(docker_name)
    path = os.path.join(crawler_config.dockers_json_dir, fname)
    if os.path.exists(path) is False:
        return None
    with open(path, 'r') as f:
        docker = json.load(f)
    return docker


def get_official_docker_json_from_file(docker_name):
    fname = generate_docker_fname(docker_name)
    path = os.path.join("E:\docker_project\dockerdocker\data\dockerhub\official\dockers\json", fname)
    if os.path.exists(path) is False:
        return None
    with open(path, 'r') as f:
        docker = json.load(f)
    return docker


def get_docker_versions_json_file(docker_name):
    fname = generate_docker_versions_fname(docker_name)
    path = os.path.join(crawler_config.versions_json_dir, fname)
    if os.path.exists(path) is False:
        return None
    with open(path, 'r') as f:
        docker_versions = json.load(f)
    return docker_versions


def get_dockerfile_json_from_file(docker_name):
    # timestamp = "2018-05-11-13-02-54"
    # timestamp = "2018-05-11-11-48-37"
    timestamp = crawler_config.timestamp
    fname = generate_dockerfile_fname(docker_name, timestamp)
    path = os.path.join(crawler_config.dockerfiles_json_dir, fname)
    if os.path.exists(path) is False:
        print "open dockerfile error: [%s]" % path
        return None
    with open(path, 'r') as f:
        dockerfile = json.load(f)
    return dockerfile


def generate_official_dockerfile_fname(docker_name, version):
    """
    generate json file name fo official dockerfile from docker name and version
    :param docker_name: the name of docker, just like: library/nginx
    :param version: the version of docker file
    :return: the json file name for docker name and version
    """
    docker_name = str(docker_name).replace("/", "#")
    fname = "%s_%s.json" % (docker_name, version)
    return fname


def get_official_dockerfile_json_from_file(docker_name):
    fname = generate_official_dockerfile_fname(docker_name, "latest")
    path = os.path.join("E:\docker_project\dockerdocker\data\dockerhub\official\dockerfiles\json", fname)
    if os.path.exists(path) is False:
        print "open dockerfile error: [%s]" % path
        return None
    with open(path, 'r') as f:
        dockerfile = json.load(f)
    return dockerfile


def get_dockerinfo_from_file(docker_name):
    dockerinfo = dict()
    names = str(docker_name).split("/")
    docker = get_official_docker_json_from_file(docker_name)
    if docker is None:
        return None
    dockerfile = get_official_dockerfile_json_from_file(docker_name)
    if dockerfile is None:
        print "dockerfile [%s:latest] is none" % docker_name
        dockerfile = {"contents": ""}
        # return None
    dockerinfo["username"] = names[0]
    dockerinfo["repname"] = names[1]
    dockerinfo["short_desc"] = docker["short_description"]
    if dockerinfo["short_desc"] is None:
        dockerinfo["short_desc"] = ""
    dockerinfo["full_desc"] = docker["full_description"]
    if dockerinfo["full_desc"] is None:
        dockerinfo["full_desc"] = ""
    if "contents" not in dockerfile:
        logging.warning("dockerfile [%s] has no attribute ['contents'], it's not a dockerfile", docker_name)
        return None
    dockerinfo["dockerfile"] = dockerfile["contents"]
    if dockerinfo["dockerfile"] is None:
        dockerinfo["dockerfile"] = ""
    return dockerinfo


def get_dockerinfo_from_database(docker_name):
    return None


def get_docker_tags_from_api(docker_info):
    docker_tags_url = crawler_config.auto_tags_url
    json_docker_tags = get_json_data(docker_tags_url, post_data=docker_info)
    if check_json_format(json_docker_tags) is False:
        # logging.error("docker_tags_info [%s] can not be got by url: [%s], json String: [%s]", docker_info, docker_tags_url, json_docker_tags)
        logging.error("docker_tags_info [%s/%s] can not be got by url: [%s], json String: [%s]", docker_info["username"], docker_info["repname"], docker_tags_url, json_docker_tags[0:20])
        return None
    raw_docker_tags = json.loads(json_docker_tags)
    docker_tags = format_docker_tags(raw_docker_tags)
    return docker_tags


def generate_tags(docker_name, path_type="file"):
    if path_type is "file":
        docker_info = get_dockerinfo_from_file(docker_name)
    else:
        docker_info = get_dockerinfo_from_database(docker_name)

    if docker_info is None:
        logging.error("Generate tags Error: dockerinfo of [%s] is None" % docker_name)
        return None
    docker_tags = get_docker_tags_from_api(docker_info)
    return docker_tags


def get_docker_tags_from_file(docker_name):
    fname = generate_docker_tags_fname(docker_name)
    # path = os.path.join(crawler_config.tags_json_dir, fname)
    path = os.path.join(crawler_config.TAGS_JSON_DIR, fname)
    if os.path.exists(path) is False:
        # logging.error("Error read path: [%s]" % path)
        return None
    with open(path, 'r') as f:
        docker_tags = json.load(f)
    return docker_tags


def read_object_from_file(file_name):
    """
    read an object from json file
    :param file_name: json file name
    :return: None if file doesn't exist or can not convert to an object by json, else return the object
    """
    if os.path.exists(file_name) is False:
        logging.error("Error read path: [%s]" % file_name)
        return None
    with open(file_name, 'r') as f:
        try:
            obj = json.load(f)
        except Exception:
            logging.error("Error json: [%s]" % f.read()[0:10])
            return None
    return obj


def read_text_from_file(file_name):
    if os.path.exists(file_name) is False:
        logging.error("Error read path: [%s]" % file_name)
        return None
    with open(file_name, 'r') as f:
        text = f.read()
    return text

def delete_files_in_dir(dir_name):
    base_path = dir_name
    filenames = os.listdir(base_path)
    for filename in filenames:
        raw_json_path = os.path.join(base_path, filename)
        os.remove(raw_json_path)

def get_official_docker_names():
    docker_names = read_object_from_file("E:\docker_project\dockerdocker\data\dockerhub\official\dockernames\json\official_docker_names.json")
    official_docker_names = list()
    for docker_name in docker_names:
        official_docker_names.append("library/%s" % docker_name)
    docker_names = official_docker_names
    return docker_names

