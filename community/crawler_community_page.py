# -*- coding: utf-8 -*-
import proxy_config
from crawler_helper import *
import json
import threading
import copy
import sys
import crawler_config
# initialize logging
# from logging_initialize import *


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append("..")

# global variables
thread_num = crawler_config.community_page_thread_num
count = crawler_config.community_all_docker_size
page_size = crawler_config.community_page_size
community_page_url = crawler_config.community_page_url
community_page_json_path = find_and_create_dirs(crawler_config.pages_json_dir)
community_params = {
    "source": "community",
    "type": "image%2Cbundle",
    "page_size": page_size,
    "q": "%2B",
    "page": 0
}


class CommunityPageWorkerThread(threading.Thread):
    """
    subclass of threading.Thread: for community page worker
    """
    def __init__(self, thread_id, save_base_path, from_page, to_page, page_url, params):
        """
        initialize object for CommunityPageWorkerThread
        :param thread_id: id of thread
        :param save_base_path: the base path for raw json of the community page
        :param from_page: the first page of the thread
        :param to_page: the last page of the thread
        :param page_url: the url of page(no params)
        :param params: the params
        """
        super(CommunityPageWorkerThread, self).__init__()
        self.thread_id = thread_id
        self.from_page = from_page
        self.to_page = to_page
        self.save_base_path = save_base_path
        self.page_url = page_url
        self.params = params

    def get_community_page(self):
        """
        get a community page
        :return: a json object of page
        """
        json_page = get_json_data(self.page_url, self.params)
        raw_page = json.loads(json_page)
        page = format_page(raw_page)
        return page

    def get_community_pages_and_write_to_files(self):
        """
        get community pages and write to files
        :return: None
        """
        for page_id in range(self.from_page, self.to_page+1) :
            self.params["page"] = page_id
            page = self.get_community_page()

            page_fname = "page_%d.json" % page_id
            path = os.path.join(self.save_base_path, page_fname)
            write_object_to_file(path, page)

    def run(self):
        """
        :return: None
        """
        logging.info("%s: Starting %s %d" % (get_time(), self.__class__.__name__, self.thread_id))
        self.get_community_pages_and_write_to_files()
        logging.info("%s: Exiting %s %d" % (get_time(), self.__class__.__name__, self.thread_id))


def start_page_crawler():
    """
    the entry of this program
    :return: None
    """
    global thread_num
    global count
    global page_size
    # json_page = getJsonData(verified_page_url, params)
    # page = json.loads(json_page)
    # count = page["count"]
    print "%s: start page crawler" % get_time()

    # proxy_helper.get_available_proxy_and_write_to_file(proxy_config.page_target_url)

    page_num = count / page_size

    per_worker = page_num / thread_num

    thread_list = list()

    for thread_id in range(0, thread_num):
        from_page = per_worker * thread_id + 1
        to_page = per_worker*(thread_id+1)
        params = copy.deepcopy(community_params)
        # params["page_size"] = page_size
        worker = CommunityPageWorkerThread(thread_id, community_page_json_path, from_page, to_page, community_page_url, params)
        logging.info("%s: CommunityPageWorkerThread %d, page %d-%d" % (get_time(), thread_id, from_page, to_page))
        thread_list.append(worker)

    # [page_num * page_size <= count < (page_num+1) * page_size]
    # [per_worker * thread_num <= page_num < (thread_num+1) * per_worker]
    # it's ok even if [page_size * page > count]
    # the number of dockers in page_$(page_num+1).json will less than page_size

    # params = copy.deepcopy(community_params)
    # from_page = per_worker * thread_num + 1
    # to_page = page_num + 1
    # worker = CommunityPageWorkerThread(thread_num, community_page_json_path, from_page, to_page, community_page_url, params)
    # logging.info("%s: CommunityPageWorkerThread %d, page %d-%d" % (get_time(), thread_num, from_page, to_page))
    # thread_list.append(worker)

    for worker in thread_list:
        worker.start()

    for worker in thread_list:
        worker.join()

    print "%s: done page crawler" % get_time()
    pass


if __name__ == "__main__":
    logging.info("%s: start" % get_time())
    start_page_crawler()
    logging.info("%s: done" % get_time())
