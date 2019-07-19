# -*- coding: utf-8 -*-


from crawler_community_page import *
from crawler_community_dockers import *
from parse_docker_names import *
from crawler_threads import *
from logging_initialize import *
from mysql_helper import *
from crawler_helper import *


def start_incremental_crawler():
    print "%s: start incremental crawler" % get_time()
    start_page_crawler()
    # parse_pages()
    # start_dockers_crawler(DockerIncrementWorkerThread)
    # parse_modified_docker_names()
    # start_dockers_crawler(DockerWorkerThread)
    # start_dockers_crawler(DockerfileWorkerThread)
    # start_dockers_crawler(DockerVersionsWorkerThread)
    # start_dockers_crawler(DockerTagsWorkerThread)
    # get_all_available_docker_names_and_write_to_file()
    # classify_available_docker_names_and_write_to_file()
    # generate_insert_sql()
    # generate_update_sql()
    # execute_insert_sqls()
    # execute_update_sqls()
    # update_new_col_pulls_and_stars()
    start_official_docker_tags_crawler()
    print "%s: done incremental crawler" % get_time()


def delete_pages_json():
    base_path = crawler_config.pages_json_dir
    filenames = os.listdir(base_path)
    for filename in filenames:
        raw_json_path = os.path.join(base_path, filename)
        os.remove(raw_json_path)


def repeat_crawler_and_parse():
    for i in range(30, 100):
        start_page_crawler()
        parse_pages(i)
        delete_pages_json()
    return None


if __name__ == "__main__":
    logging.info("%s start: incremental crawler" % get_time())
    start_incremental_crawler()
    # repeat_crawler_and_parse()
    logging.info("%s done: incremental crawler" % get_time())

