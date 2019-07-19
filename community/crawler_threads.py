# -*- coding: utf-8 -*-
import threading
from crawler_helper import *


class WorkerThread(threading.Thread):
    """
    subclass of threading.Thread
    """
    def __init__(self, thread_id, save_path, docker_names):
        """
        initialize object for WorkerThread
        :param thread_id: id of thread
        :param save_path: the path for saving files
        :param docker_names: docker names processed by this thread
        """
        super(WorkerThread, self).__init__()
        self.thread_id = thread_id
        self.save_path = save_path
        self.docker_names = docker_names
        return


    def process(self):
        """
        get docker and write to file
        :return: None
        """
        pass

    def run(self):
        """
        :return: None
        """
        # we don't need continue if docker_names is empty
        if self.docker_names.__len__() is 0:
            return
        logging.info("%s: Starting %s %d" % (get_time(), self.__class__.__name__, self.thread_id))
        self.process()
        logging.info("%s: Exiting %s %d" % (get_time(), self.__class__.__name__, self.thread_id))
        return


class DockerWorkerThread(WorkerThread):
    """
    subclass of WorkerThread
    """
    def __init__(self, thread_id, docker_save_path, docker_names):
        """
        initialize object for WorkerThread
        :param thread_id: id of thread
        :param docker_save_path: the path for saving dockers
        :param docker_names: docker names processed by this thread
        """
        super(DockerWorkerThread, self).__init__(thread_id, docker_save_path, docker_names)
        return

    def process(self):
        """
        :return:
        """
        for docker_name in self.docker_names:
            json_docker = get_docker_json_from_file(docker_name)
            if json_docker is not None:
                logging.warn("docker %s exits in json file", docker_name)
                continue
            docker = get_community_docker(docker_name)
            if docker is None:
                logging.error("docker [%s] can not be got by url", docker_name)
                continue
            docker_fname = generate_docker_fname(docker_name)
            path = os.path.join(self.save_path, docker_fname)
            write_object_to_file(path, docker)
        return


class DockerfileWorkerThread(WorkerThread):
    """
    subclass of WorkerThread
    """
    def __init__(self, thread_id, dockerfile_save_path, docker_names):
        """
        initialize object for WorkerThread
        :param thread_id: id of thread
        :param dockerfile_save_path: the path for saving dockerfiles
        :param docker_names: docker names processed by this thread
        """
        super(DockerfileWorkerThread, self).__init__(thread_id, dockerfile_save_path, docker_names)
        return

    def process(self):
        """
        :return:
        """
        for docker_name in self.docker_names:
            dockerfile = get_community_dockerfile(docker_name)
            if dockerfile is None:
                logging.error("%s: dockerfile [%s] can not be got by url", get_time(), docker_name)
                dockerfile = {"contents": "None"}
            dockerfile_fname = generate_dockerfile_fname(docker_name)
            path = os.path.join(self.save_path, dockerfile_fname)
            write_object_to_file(path, dockerfile)
        return


class DockerVersionsWorkerThread(WorkerThread):
    """
    subclass of WorkerThread
    """
    def __init__(self, thread_id, versions_save_path, docker_names):
        """
        initialize object for WorkerThread
        :param thread_id: id of thread
        :param versions_save_path: the path for saving versions
        :param docker_names: docker names processed by this thread
        """
        super(DockerVersionsWorkerThread, self).__init__(thread_id, versions_save_path, docker_names)
        return

    def process(self):
        """
        :return:
        """
        for docker_name in self.docker_names:
            # docker_github_url = get_link_url(docker_name)
            # # print docker_name
            # # tags = get_tags_github(github_url)
            # versions_urls = get_versions2dockerfiles_urls_github(docker_github_url)
            # print versions_urls
            docker_versions = get_community_docker_versions(docker_name)
            versions_fname = generate_docker_versions_fname(docker_name)
            path = os.path.join(self.save_path, versions_fname)
            write_object_to_file(path, docker_versions)
        return


class DockerIncrementWorkerThread(WorkerThread):
    """
    subclass of WorkerThread
    """
    def __init__(self, thread_id, docker_names_save_path, docker_names):
        """
        initialize object for WorkerThread
        :param thread_id: id of thread
        :param docker_names_save_path: the path for saving new docker names
        :param docker_names: docker names processed by this thread
        """
        super(DockerIncrementWorkerThread, self).__init__(thread_id, docker_names_save_path, docker_names)
        return

    def process(self):
        """
        :return:
        """
        new_docker_names = list()
        updated_docker_names = list()
        error_docker_names = list()
        for docker_name in self.docker_names:
            docker = get_community_docker(docker_name)
            if docker is None:
                logging.error("docker [%s] can not be got by url", docker_name)
                error_docker_names.append(docker_name)
                continue
            docker["last_updated"] = convert_ints2datetime(docker["last_updated"])
            # determine if save the docker and get dockerfile by last_updated time of docker
            old_docker = get_old_community_docker_updated_time(docker_name)
            if old_docker is None:
                new_docker_names.append(docker_name)
            elif docker["last_updated"] != old_docker["last_updated"]:
                updated_docker_names.append(docker_name)
            else:
                # print docker_name + " is updated at last time"
                logging.info(get_time() + ": Exists " + docker_name + " is updated at last time")

        new_file_name = "%s_thread_%s.json" % (crawler_config.new_docker_names_json_prefix, self.thread_id)
        updated_file_name = "%s_thread_%s.json" % (crawler_config.updated_docker_names_json_prefix, self.thread_id)
        error_file_name = "%s_thread_%s.json" % (crawler_config.error_docker_names_json_prefix, self.thread_id)
        new_docker_names_fname = os.path.join(self.save_path, new_file_name)
        updated_docker_names_fname = os.path.join(self.save_path, updated_file_name)
        error_docker_names_fname = os.path.join(self.save_path, error_file_name)
        write_object_to_file(new_docker_names_fname, new_docker_names)
        write_object_to_file(updated_docker_names_fname, updated_docker_names)
        write_object_to_file(error_docker_names_fname, error_docker_names)

        return


class DockerTagsWorkerThread(WorkerThread):
    """
    subclass of WorkerThread
    """
    def __init__(self, thread_id, tags_save_path, docker_names):
        """
        initialize object for WorkerThread
        :param thread_id: id of thread
        :param tags_save_path: the path for saving tags
        :param docker_names: docker names processed by this thread
        """
        super(DockerTagsWorkerThread, self).__init__(thread_id, tags_save_path, docker_names)
        return

    def process(self):
        """
        :return:
        """
        error_docker_names = list()
        for docker_name in self.docker_names:
            if get_docker_tags_from_file(docker_name) is not None:
                # if the tags is not None means the tags of docker_name is ok
                continue
            docker_tags = generate_tags(docker_name, path_type="file")
            if docker_tags is None:
                error_docker_names.append(docker_name)
                continue
            fname = generate_docker_tags_fname(docker_name)
            path = os.path.join(self.save_path, fname)
            # write_tags_string_to_file(path, docker_tags)
            write_object_to_file(path, docker_tags)
        error_dir = crawler_config.error_tags_docker_names_json_dir
        path = os.path.join(error_dir, "error_tags_docker_names_thread_%s.json" % self.thread_id)
        write_object_to_file(path, error_docker_names)

        return
