import crawler_helper as ch
import mysql_helper as mh
import os


class DockerFullInfo:
    """
    docker full info, including dockerfile, docker_name, docker_tags, docker_versions, docker
    """
    def __init__(self, docker_full_info_dict=None):
        self.docker_name = ""
        self.dockerfile = dict()
        self.docker_versions = list()
        self.docker_tags = list()
        self.docker = dict()
        if docker_full_info_dict:
            self.__dict__ = docker_full_info_dict

    def __repr__(self):
        return self.__dict__


def _crawler_docker_full_info_with_name(docker_name):
    """
    crawler for one docker with docker name
    :param docker_name:
    :return: return a json
    """
    docker = ch.get_community_docker(docker_name)
    if docker is None:
        print("docker [%s] can not be got by url", docker_name)
    dockerfile = ch.get_community_dockerfile(docker_name)
    if dockerfile is None:
        print("dockerfile [%s] can not be got by url", docker_name)
        dockerfile = {"contents": "None"}
    docker_versions = ch.get_community_docker_versions(docker_name)
    docker_info = _get_docker_info(dockerfile, docker_name, docker)
    docker_tags = ch.get_docker_tags_from_api(docker_info)
    if docker_tags is None:
        print("docker_tags [%s] can not be generated", docker_name)
        docker_tags = []
    docker_full_info = DockerFullInfo()
    docker_full_info.docker_name = docker_name
    print "docker_name:\n", docker_name
    docker_full_info.docker = docker
    print "docker:\n", docker
    docker_full_info.docker_tags = docker_tags
    print "docker_tags:\n", docker_tags
    docker_full_info.docker_versions = docker_versions
    print "docker_versions:\n", docker_versions
    docker_full_info.dockerfile = dockerfile
    print "dockerfile:\n", dockerfile
    return docker_full_info


def _write_docker_full_info(docker_full_info, insert=False):
    """
    write dockerfile to disk and the other info to datebase
    :param docker_full_info: a list of DockerFullInfo
    :param insert: True means insert a docker, and False means update a docker
    :return: True if success, else False
    """
    docker_full_info = DockerFullInfo(docker_full_info.__dict__)
    if insert:
        sql = _generate_insert_sql(docker_full_info)
    else:
        sql = _generate_update_sql(docker_full_info)

    mh.execute_sqls([sql])
    print("Write done: docker full info to database")
    dockerfile_fname = ch.generate_dockerfile_fname(docker_full_info.docker_name)
    dockerfile_path = os.path.join("./", dockerfile_fname)
    ch.write_object_to_file(dockerfile_path, docker_full_info.dockerfile)
    pass


def _generate_insert_sql(docker_full_info):
    """
    genetate insert sql for docker full info
    :param docker_full_info: a object of DockerFullInfo
    :return: a string of sql
    """
    docker_full_info = DockerFullInfo(docker_full_info.__dict__)
    docker_name = docker_full_info.docker_name
    docker = docker_full_info.docker
    docker_versions = docker_full_info.docker_versions
    docker_tags = docker_full_info.docker_tags
    docker_sql = mh.insert_docker_sql(docker_name, docker=docker)
    docker_versions_sql = mh.insert_docker_versions_sql(docker_name, docker_versions=docker_versions)
    docker_tags_sql = mh.insert_docker_tags_sql(docker_name, docker_tags=docker_tags)
    return "%s\n%s\n%s\n" % (docker_sql, docker_versions_sql, docker_tags_sql)


def _generate_update_sql(docker_full_info):
    """
    genetate update sql for docker full info
    :param docker_full_info: a object of DockerFullInfo
    :return: a string of sql
    """
    docker_full_info = DockerFullInfo(docker_full_info.__dict__)
    docker_name = docker_full_info.docker_name
    docker = docker_full_info.docker
    docker_versions = docker_full_info.docker_versions


    docker_sql = mh.update_docker_sql(docker_name, docker=docker)
    docker_versions_sql = mh.update_docker_versions_sql(docker_name, docker_versions=docker_versions)

    return "%s\n%s\n" % (docker_sql, docker_versions_sql)


def _get_docker_info(dockerfile, docker_name, docker):
    """
    generate docker info for docker tags generation
    :param dockerfile: json object
    :param docker_name: string
    :param docker: json object
    :return: a dict
    """
    dockerinfo = dict()
    names = str(docker_name).split("/")
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
        print("dockerfile [%s] has no attribute ['contents'], it's not a dockerfile", docker_name)
        return None
    dockerinfo["dockerfile"] = dockerfile["contents"]
    if dockerinfo["dockerfile"] is None:
        dockerinfo["dockerfile"] = ""
    return dockerinfo


def _get_increment_data_database(docker_names=None):
    """
    read all docker in database and generate a update
    :param docker_names: None mean have no any new docker
    :return: a dict(str:docker_name, bool:insert)
    """
    increment_data = dict()
    if docker_names is None:
        docker_names = list()
    print("read all docker names in database...")
    db_docker_names = mh.get_all_docker_names_database()
    print("read all docker names in database done")
    print(db_docker_names)
    new_docker_names = set(docker_names) - set(db_docker_names)
    for docker_name in new_docker_names:
        increment_data[docker_name] = True
    for docker_name in db_docker_names:
        docker = ch.get_community_docker(docker_name)
        if docker is None:
            print("can not get docker %s by url" % docker_name)
            continue
        db_docker = mh.get_docker_database(docker_name)
        docker["last_updated"] = ch.convert_ints2datetime(docker["last_updated"])
        if docker["last_updated"] != db_docker["last_updated"]:
            print("updated on docker store : %s" % docker_name)
            increment_data[docker_name] = False
        else:
            print("hit docker: %s" % docker_name)
    return increment_data


def incremental_crawler(increment_data=None):
    """
    crawler all docker and write to database(write dockerfile into file)
    increment_data will be a dict, which contains dockers waiting to modified
    :param increment_data: a dict(str:docker_name, bool:insert)
    :return: None
    """
    if increment_data is None:
        increment_data = _get_increment_data_database()
    for docker_name in increment_data:
        print("Crawler: %s" % docker_name)
        insert = increment_data[docker_name]
        docker_full_info = _crawler_docker_full_info_with_name(docker_name)
        ch.write_object_to_file("./%s_full_info.json" % docker_name.replace("/", "#"), docker_full_info.__dict__)
        _write_docker_full_info(docker_full_info=docker_full_info, insert=insert)
        # print docker_full_info.__dict__


if __name__ == "__main__":
    increment_data = {"asssaf/base-xpra": True,
                      "centerforopenscience/mfr": True,
                      "openmicroscopy/omero-base": True,
                      "upfluence/sensu-client": True,
                      }

    incremental_crawler(increment_data=increment_data)
    # print(_get_increment_data_database(["001/123"]))
