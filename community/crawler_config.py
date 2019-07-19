# -*- coding: utf-8 -*-
import os
import time

thisFilePath = os.path.split(os.path.realpath(__file__))[0]
# we have to modify the tail if we change the path of this python file
tail = 29
rootPath = thisFilePath[0:-tail]
if rootPath[-1] != "/" and rootPath[-1] != "\\":
    message = "Error root path [%s]\n\tPlease check whether you changed the path of current file" % rootPath
    raise Exception(message)
# print rootPath

data_root_path = rootPath

pages_json_dir = data_root_path + "data/dockerstore/community/pages/json/"
all_docker_names_json_path = data_root_path + "data/dockerstore/community/docker_names/json/all_docker_names.json"
# modified names including new and updated
modified_docker_names_json_dir = data_root_path + "data/dockerstore/community/modified_docker_names/json/"
new_docker_names_json_prefix = "new_docker_names"
updated_docker_names_json_prefix = "updated_docker_names"
error_docker_names_json_prefix = "error_docker_names"
new_docker_names_json_path = data_root_path + "data/dockerstore/community/docker_names/json/new_docker_names.json"
updated_docker_names_json_path = data_root_path + "data/dockerstore/community/docker_names/json/updated_docker_names.json"
error_docker_names_json_path = data_root_path + "data/dockerstore/community/docker_names/json/error_docker_names.json"

error_tags_docker_names_json_dir = data_root_path + "data/dockerstore/community/docker_tags/error_names/"
available_new_docker_names_for_db_path = data_root_path + "data/dockerstore/community/docker_names/json/available_new_docker_names_for_db.json"
available_updated_docker_names_for_db_path = data_root_path + "data/dockerstore/community/docker_names/json/available_updated_docker_names_for_db.json"
available_docker_names_for_db_path = data_root_path + "data/dockerstore/community/docker_names/json/available_docker_names_for_db.json"
unavailable_docker_names_for_db_path = data_root_path + "data/dockerstore/community/docker_names/json/unavailable_docker_names_for_db.json"
available_docker_names_for_db_path_for_stars_and_pulls = data_root_path + "data/dockerstore/community/docker_names/json/available_docker_names_for_db_for_stars_and_pull.json"
unavailable_docker_names_for_db_path_for_stars_and_pulls = data_root_path + "data/dockerstore/community/docker_names/json/unavailable_docker_names_for_db_for_stars_and_pull.json"


dockers_json_dir = data_root_path + "data/dockerstore/community/dockers/json/"
dockerfiles_json_dir = data_root_path + "data/dockerstore/community/dockerfiles/json/"
versions_json_dir = data_root_path + "data/dockerstore/community/docker_versions/json/"
tags_json_dir = data_root_path + "data/dockerstore/community/docker_tags/json/"
TAGS_JSON_DIR = "/home/jiahong/Workspace/IdeaProjects/DockerProcess/docker-process-master/data/crawler_tags/json"
images_size_count_path = data_root_path + "data/dockerstore/community/docker_versions/count/count_and_size.json"
incremental_insert_sql_dir = data_root_path + "data/dockerstore/community/incremental/insert/sql/"
incremental_update_sql_dir = data_root_path + "data/dockerstore/community/incremental/update/sql/"
incremental_update_sql_dir_for_stars_and_pulls = data_root_path + "data/dockerstore/community/incremental/update_for_stars_and_pull/sql/"
semi_tag_rec_sql_dir = data_root_path + "data/dockerstore/community/semi_tag_rec/tags/sql"

# TODO: timestamp for dockerfile name
# timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
timestamp = "2018-05-11-13-02-54"

# more than 30 will occur some problem in server
community_page_thread_num = 25

community_docker_thread_num = 100

community_tags_thread_num = 10

# if the size exceed 1000,000 the exception will be return
community_all_docker_size = 999999

community_page_size = 100

community_page_num = community_all_docker_size / community_page_size

community_docker_base_url = "https://store.docker.com/v2/repositories/"

auto_build_suffix = "autobuild/"

community_page_url = "https://store.docker.com/api/content/v1/products/search"

# auto_tags_url = "http://39.104.62.233:8000/autotags"
auto_tags_url = "http://39.104.105.27:8000/autotags"

default_time_of_docker_or_version = "1970-01-01T00:00:00.000000Z"

retry_times = 100

