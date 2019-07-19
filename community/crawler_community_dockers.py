# -*- coding: utf-8 -*-

from utils import *
import sys
from crawler_threads import *
from crawler_helper import *
import crawler_config
import proxy_helper
import proxy_config
# from logging_initialize import *


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append("..")


def start_dockers_crawler(worker_thread):
    """
    the entry of this program
    :return: None
    """
    print "%s: start %s" % (get_time(), worker_thread)

    # print worker_thread is DockerVersionsWorkerThread
    # print DockerVersionsWorkerThread
    thread_list = list()
    # docker_names = list()

    if worker_thread is DockerfileWorkerThread:
        proxy_helper.get_available_proxy_and_write_to_file(get_community_dockerfile_url(proxy_config.target_docker_name))
        docker_names = get_modified_docker_names()
        thread_num = crawler_config.community_docker_thread_num
        save_path = find_and_create_dirs(crawler_config.dockerfiles_json_dir)
    elif worker_thread is DockerWorkerThread:
        proxy_helper.get_available_proxy_and_write_to_file(get_community_docker_url(proxy_config.target_docker_name))
        docker_names = get_modified_docker_names()
        thread_num = crawler_config.community_docker_thread_num
        save_path = find_and_create_dirs(crawler_config.dockers_json_dir)
    elif worker_thread is DockerVersionsWorkerThread:
        proxy_helper.get_available_proxy_and_write_to_file(get_community_docker_versions_url(proxy_config.target_docker_name))
        docker_names = get_modified_docker_names()
        thread_num = crawler_config.community_docker_thread_num
        save_path = find_and_create_dirs(crawler_config.versions_json_dir)
    elif worker_thread is DockerIncrementWorkerThread:
        proxy_helper.get_available_proxy_and_write_to_file(get_community_docker_url(proxy_config.target_docker_name))
        docker_names = get_all_docker_names()
        thread_num = crawler_config.community_docker_thread_num
        save_path = find_and_create_dirs(crawler_config.modified_docker_names_json_dir)
    elif worker_thread is DockerTagsWorkerThread:
        thread_num = crawler_config.community_tags_thread_num
        docker_names = get_new_docker_names()
        save_path = find_and_create_dirs(crawler_config.tags_json_dir)
    else:
        raise Exception("Error: Thread[%s] class type error" % str(worker_thread))
        pass

    # print docker_names
    count = docker_names.__len__()
    # print docker_names
    # consider the div of integer
    per_worker = (count + (thread_num-1)) / thread_num
    for thread_id in range(0, thread_num):
        from_docker = per_worker * thread_id
        to_docker = per_worker*(thread_id+1)-1
        # print "from [%d] to [%d]" % (from_docker, to_docker)
        worker = worker_thread(thread_id, save_path, docker_names[from_docker: to_docker + 1])
        logging.info("%s: %s %d, docker %d-%d" % (get_time(), worker_thread.__name__, thread_id, from_docker, to_docker))
        thread_list.append(worker)

    for worker in thread_list:
        worker.start()

    for worker in thread_list:
        worker.join()

    print "%s: done %s" % (get_time(), worker_thread)


def start_official_docker_tags_crawler():
    print "%s: start %s" % (get_time(), DockerTagsWorkerThread)

    # print worker_thread is DockerVersionsWorkerThread
    # print DockerVersionsWorkerThread
    thread_list = list()
    thread_num = crawler_config.community_tags_thread_num
    docker_names = get_official_docker_names()
    save_path = find_and_create_dirs("E:\docker_project\dockerdocker\data\dockerhub\official\dockertags\json\\")
    # print docker_names
    count = docker_names.__len__()
    # print docker_names
    # consider the div of integer
    per_worker = (count + (thread_num-1)) / thread_num
    for thread_id in range(0, thread_num):
        from_docker = per_worker * thread_id
        to_docker = per_worker*(thread_id+1)-1
        # print "from [%d] to [%d]" % (from_docker, to_docker)
        worker = DockerTagsWorkerThread(thread_id, save_path, docker_names[from_docker: to_docker + 1])
        logging.info("%s: %s %d, docker %d-%d" % (get_time(), DockerTagsWorkerThread.__name__, thread_id, from_docker, to_docker))
        thread_list.append(worker)

    for worker in thread_list:
        worker.start()

    for worker in thread_list:
        worker.join()

    print "%s: done %s" % (get_time(), DockerTagsWorkerThread)

if __name__ == "__main__":
    logging.info("%s: start" % get_time())
    # start_dockers_crawler(DockerWorkerThread)
    # start_dockers_crawler(DockerfileWorkerThread)
    # start_dockers_crawler(DockerVersionsWorkerThread)
    # start_dockers_crawler(DockerIncrementWorkerThread)
    logging.info("%s: done" % get_time())
