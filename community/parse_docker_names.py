# -*- coding: utf-8 -*-
from crawler_helper import *
import logging_initialize


def parse_raw_json_page(raw_json_path):
    """
    read json file and parse it
    :param raw_json_path: the file path of one page
    :return: a set of docker names
    """
    with open(raw_json_path, "r") as fp:
        page = json.load(fp)
        docker_names = page['docker_names']
        docker_names_set = set(docker_names)
        return docker_names_set


def parse_modified_docker_names_json(json_path):
    """
    read json file and parse it
    :param json_path: the path of json file generated by thread
    :return: a set of docker names
    """
    with open(json_path, "r") as fp:
        docker_names = json.load(fp)
        docker_names_set = set(docker_names)
        return docker_names_set


def parse_pages(i=None):
    """
    parse the raw page json and write list of docker names to file
    :return: None
    """
    # TODO: has to visit database for getting old docker names
    print "%s: start parse pages" % get_time()
    base_path = crawler_config.pages_json_dir
    filenames = os.listdir(base_path)
    all_docker_names_set = set()
    for filename in filenames:
        raw_json_path = os.path.join(base_path, filename)
        docker_names_set = parse_raw_json_page(raw_json_path)
        all_docker_names_set |= docker_names_set
    old_docker_names = get_all_old_docker_names(i-1)
    all_docker_names_set |= set(old_docker_names)
    docker_names = list(all_docker_names_set)
    # write_object_to_file(crawler_config.all_docker_names_json_path, docker_names)
    write_object_to_file(crawler_config.all_docker_names_json_path + str(i), docker_names)
    print "%s: done parse pages" % get_time()


def parse_modified_docker_names():
    """
    parse the modified json and write list of new and updated docker names respectively
    :return:
    """
    print "%s: start parse modified docker names" % get_time()

    base_path = crawler_config.modified_docker_names_json_dir
    filenames = os.listdir(base_path)
    new_docker_names_set = set()
    updated_docker_names_set = set()
    error_docker_names_set = set()
    new_prefix = crawler_config.new_docker_names_json_prefix
    updated_prefix = crawler_config.updated_docker_names_json_prefix
    error_prefix = crawler_config.error_docker_names_json_prefix
    for filename in filenames:
        raw_json_path = os.path.join(base_path, filename)
        docker_names_set = parse_modified_docker_names_json(raw_json_path)
        if filename[0:new_prefix.__len__()] == new_prefix:
            new_docker_names_set |= docker_names_set
        elif filename[0:updated_prefix.__len__()] == updated_prefix:
            updated_docker_names_set |= docker_names_set
        elif filename[0:error_prefix.__len__()] == error_prefix:
            error_docker_names_set |= docker_names_set
        else:
            raise Exception("Error read dir[%s]" % base_path)

    new_docker_names = list(new_docker_names_set)
    updated_docker_names = list(updated_docker_names_set)
    error_docker_names = list(error_docker_names_set)
    write_object_to_file(crawler_config.new_docker_names_json_path, new_docker_names)
    write_object_to_file(crawler_config.updated_docker_names_json_path, updated_docker_names)
    write_object_to_file(crawler_config.error_docker_names_json_path, error_docker_names)
    print "%s: start delete json files in %s" % (get_time(), base_path)
    delete_files_in_dir(base_path)
    print "%s: done delete json files in %s" % (get_time(), base_path)
    print "%s: done parse modified docker names" % get_time()


if __name__ == "__main__":
    logging.info("%s: start" % get_time())
    parse_modified_docker_names()
    # parse_pages()
    logging.info("%s: done" % get_time())
