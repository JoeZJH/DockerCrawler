#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import re
import MySQLdb
from datetime import *
# from crawler_helper import *
import crawler_helper as ch
import crawler_config as cc
import logging


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'docker_manager',
        'USER': 'docker',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


def get_database_connection(database=None):
    if database is None:
        database = DATABASES['default']
    db = MySQLdb.connect(database["HOST"],
                         database['USER'],
                         database['PASSWORD'],
                         database['NAME'],
                         charset='utf8')
    return db


def execute(sql, db=None):
    if db is None:
        db = get_database_connection()
        cursor = db.cursor()
        cursor.execute(sql)
        db.close()
    else:
        cursor = db.cursor()
    return cursor

def get_all_docker_names_database():
    sql = """select user_name, docker_name 
              from docker_manager.DockerManager_docker;"""
    cursor = execute(sql)
    docker_names = list()
    for row in cursor.fetchall():
        docker_name = "%s/%s" % (row[0], row[1])
        docker_names.append(docker_name)
    return docker_names


def get_all_docker_names_and_ids_database():
    sql = """select user_name, docker_name, id
              from docker_manager.DockerManager_docker;"""
    cursor = execute(sql)
    dockers = list()
    for row in cursor.fetchall():
        docker = dict()
        docker_name = "%s/%s" % (row[0], row[1])
        docker_id = row[2]
        docker["docker_name"] = docker_name
        docker["id"] = docker_id
        dockers.append(docker)
    return dockers


def get_docker_database(docker_name):
    names = str(docker_name).split("/")
    sql = """select user_name, docker_name, updated_time 
              from docker_manager.DockerManager_docker 
              where User_name = "%s"
              and docker_name = "%s";""" % (names[0], names[1])
    cursor = execute(sql)
    row = cursor.fetchone()
    if row is None:
        return None
    docker = dict()
    # docker_name = "%s/%s" % (row[0], row[1])
    # docker["name"] = docker_name
    docker["last_updated"] = row[2]
    return docker


def get_docker_id_database(docker_name):
    names = str(docker_name).split("/")
    sql = """select id
              from docker_manager.DockerManager_docker 
              where User_name = "%s"
              and docker_name = "%s";""" % (names[0], names[1])
    cursor = execute(sql)
    row = cursor.fetchone()
    if row is None:
        return None
    docker_id = row[0]
    return docker_id


def generate_sql_string(string):
    return str(string).encode("unicode_escape").replace("\"", "\\\"").replace("\'", "\\\'").replace("\\", "\\\\").replace("\\\\\"", "\\\"")


def insert_docker_sql(docker_name, docker=None):
    line_head = """insert into docker_manager.DockerManager_docker """ \
                + """(created_time,updated_time,user_name,docker_name,short_desc,full_desc,pulls,stars) """
    if docker is None:
        docker = ch.get_docker_json_from_file(docker_name)
    names = str(docker_name).split('/')

    updated_time = ch.convert_ints2datetime(docker["last_updated"]).__str__()
    u_name = names[0]
    d_name = names[1]
    short_desc = generate_sql_string(docker["short_description"])
    full_desc = generate_sql_string(docker["full_description"])
    pulls = docker["pull_count"]
    stars = docker["star_count"]

    line_sql = """%s values (NOW(), "%s", "%s", "%s", "%s", "%s", "%s", "%s");\n""" \
               % (line_head, updated_time, u_name, d_name, short_desc, full_desc, pulls, stars)
    return line_sql


def update_docker_sql(docker_name, docker=None):
    line_head = """update docker_manager.DockerManager_docker"""
    if docker is None:
        docker = ch.get_docker_json_from_file(docker_name)
    names = str(docker_name).split("/")
    u_name = names[0]
    d_name = names[1]
    updated_time = ch.convert_ints2datetime(docker["last_updated"])
    short_desc = generate_sql_string(docker["short_description"])
    full_desc = generate_sql_string(docker["full_description"])
    pulls = docker["pull_count"]
    stars = docker["star_count"]

    line_sql = """%s set updated_time="%s", short_desc="%s", full_desc="%s", pulls=%d, stars=%d """ \
               % (line_head, updated_time, short_desc, full_desc, pulls, stars) \
               + """where user_name="%s" """ % u_name \
               + """ and docker_name="%s";\n""" % d_name
    return line_sql


def delete_docker_versions_sql(docker_id):
    sql = """delete from docker_manager.DockerManager_dockerversion where docker_id="%s";\n""" % docker_id
    return sql


def update_docker_versions_sql(docker_name, docker_versions=None):
    docker_id = get_docker_id_database(docker_name)
    # docker_versions = get_docker_versions_json_file(docker_name)
    sql = delete_docker_versions_sql(docker_id)
    sql += insert_docker_versions_sql(docker_name, docker_id, docker_versions)
    return sql


def insert_docker_versions_sql(docker_name, docker_id=None, docker_versions=None):
    # return None
    # docker_id = get_docker_id_database(docker_name)
    # if docker_id is None:
    #     docker_id =
    if docker_versions is None:
        docker_versions = ch.get_docker_versions_json_file(docker_name)
    sql = ""
    if docker_versions is None:
        logging.warn("docker version is None: [%s]", docker_name)
        return sql
    # print docker_name
    for docker_version in docker_versions:
        line_sql = insert_docker_version_sql(docker_name, docker_version, docker_id)
        sql += line_sql
    return sql


def insert_docker_version_sql(docker_name, docker_version, docker_id=None):
    # dockerfile = ch.get_dockerfile_json_from_file(docker_name)
    # if dockerfile is None:
    #     line_head = """insert into docker_manager.DockerManager_dockerversion """ \
    #                 + """(created_time,updated_time,name,is_lasted,docker_id) """
    # else:
    #     line_head = """insert into docker_manager.DockerManager_dockerversion """ \
    #                 + """(created_time,updated_time,name,is_lasted,dockerfile_path,docker_id) """
    line_head = """insert into docker_manager.DockerManager_dockerversion """ \
                + """(created_time,updated_time,name,is_lasted,dockerfile_path,docker_id) """
    updated_time = ch.convert_ints2datetime(docker_version["last_updated"]).__str__()
    name = docker_version["name"]
    # we can ignore 'is_lasted' now
    is_lasted = "false"
    dockerfile_path = ch.generate_dockerfile_fname(docker_name)

    if docker_id is None:
        names = str(docker_name).split("/")
        u_name = names[0]
        d_name = names[1]
        docker_id = """(select id from docker_manager.DockerManager_docker where user_name="%s" and docker_name="%s")""" \
                    % (u_name, d_name)
    # if dockerfile is None:
    #     line_sql = """%s values (NOW(), "%s", "%s", %s, %s);\n""" \
    #                % (line_head, updated_time, name, is_lasted, docker_id)
    # else:
    #     line_sql = """%s values (NOW(), "%s", "%s", %s, "%s", %s);\n""" \
    #                % (line_head, updated_time, name, is_lasted, dockerfile_path, docker_id)
    line_sql = """%s values (NOW(), "%s", "%s", %s, "%s", %s);\n""" \
               % (line_head, updated_time, name, is_lasted, dockerfile_path, docker_id)
    return line_sql


def insert_docker_tags_sql(docker_name, docker_id=None, docker_tags=None):
    """
    TODO: generate insert sql with the structure of tags
    :param docker_name:
    :return:
    """
    if docker_tags is None:
        docker_tags = ch.get_docker_tags_from_file(docker_name)
    sql = ""
    for docker_tag in docker_tags:
        line_sql = insert_docker_tag_sql(docker_name, docker_tag, docker_id)
        sql += line_sql
    return sql


def insert_docker_tag_sql(docker_name, docker_tag, docker_id=None):
    line_head = """insert into docker_manager.DockerManager_dockertag """ \
                + """(created_time,updated_time,name,tag_from,docker_id) """
    name = docker_tag
    if docker_id is None:
        names = str(docker_name).split("/")
        u_name = names[0]
        d_name = names[1]
        docker_id = """(select id from docker_manager.DockerManager_docker where user_name="%s" and docker_name="%s")""" \
                    % (u_name, d_name)
    line_sql = """%s values (NOW(), NOW() , "%s", "%s", %s);\n""" \
               % (line_head, name, "desc", docker_id)
    return line_sql


def generate_insert_sql_fname(docker_name):
    replaced_name = str(docker_name).replace("/", "#")
    fname = "insert_%s.sql" % replaced_name
    return fname


def generate_update_sql_fname(docker_name):
    replaced_name = str(docker_name).replace("/", "#")
    fname = "update_%s.sql" % replaced_name
    return fname


def generate_insert_sql():
    print "%s: start generate insert sql" % ch.get_time()

    sql_dir = ch.find_and_create_dirs(cc.incremental_insert_sql_dir)

    # docker_names = ch.get_new_docker_names()
    docker_names = ch.read_object_from_file(cc.available_new_docker_names_for_db_path)

    for docker_name in docker_names:
        sql_name = generate_insert_sql_fname(docker_name)
        insert_sql_path = os.path.join(sql_dir, sql_name)
        if os.path.exists(insert_sql_path):
            logging.warn("insert sql file exists: [%s]" % insert_sql_path)
            continue
        sql_file = open(insert_sql_path, 'w')
        sql_file.write("\nbegin;\n")
        sql_insert_docker = insert_docker_sql(docker_name)
        sql_insert_docker_versions = insert_docker_versions_sql(docker_name)
        sql_insert_tags = insert_docker_tags_sql(docker_name)
        sql = "%s\n%s\n%s" % (sql_insert_docker, sql_insert_docker_versions, sql_insert_tags)
        sql_file.write(sql)
        sql_file.write("commit;\n")
        sql_file.close()
    print "%s: done generate insert sql" % ch.get_time()
    return None


# def generate_insert_docker_versions_sql():
#     sql_name = "incremental_insert_docker_versions.sql"
#     sql_dir = find_and_created_dirs(crawler_config.incremental_insert_sql_dir)
#     insert_sql_path = os.path.join(sql_dir, sql_name)
#     docker_names = get_new_docker_names()
#     sql_file = open(insert_sql_path, 'w')
#     sql_file.write("begin;\n")
#     line_head = """insert into docker_manager.DockerManager_dockerversion """ \
#                 + """(created_time,updated_time,name,is_lasted,dockerfile_path,docker_id) """
#     for docker_name in docker_names:
#         docker_id = get_docker_id_database(docker_name)
#         docker_versions = get_docker_versions_json_file(docker_name)
#         for docker_version in docker_versions:
#
#             updated_time = convert_ints2datetime(docker_version["last_updated"]).__str__()
#             name = docker_version["name"]
#             # we can ignore 'is_lasted' now
#             is_lasted = "false"
#             # TODO: dockerfile_path is "" now
#             dockerfile_path = ""
#             line_sql = """%s values (NOW(), "%s", "%s", "%s", "%s", "%s");\n""" \
#                        % (line_head, updated_time, name, is_lasted, dockerfile_path, docker_id)
#
#             sql_file.write(line_sql)
#     sql_file.write("commit;\n")
#     return None


def generate_update_sql():
    print "%s: start generate update sql" % ch.get_time()
    sql_dir = ch.find_and_create_dirs(cc.incremental_update_sql_dir)
    # docker_names = ch.get_updated_docker_names()
    docker_names = ch.read_object_from_file(cc.available_updated_docker_names_for_db_path)

    for docker_name in docker_names:
        sql_name = generate_update_sql_fname(docker_name)
        update_sql_path = os.path.join(sql_dir, sql_name)
        if os.path.exists(update_sql_path):
            logging.warn("update sql file exists: [%s]" % update_sql_path)
            continue
        sql_file = open(update_sql_path, "w")
        sql_file.write("\nbegin;\n")
        sql_update_docker = update_docker_sql(docker_name)
        sql_update_docker_versions = update_docker_versions_sql(docker_name)
        # we never change the tags of dockers in the database
        # sql_update_tags = update_docker_tags_sql(docker_name)
        sql = "%s\n%s" % (sql_update_docker, sql_update_docker_versions)
        sql_file.write(sql)
        sql_file.write("commit;\n")
    print "%s: done generate update sql" % ch.get_time()
    return None


# def get_new_available_docker_names_for_db_and_write_to_file():
#     docker_names = ch.get_new_docker_names()
#     available_docker_names = list()
#     for docker_name in docker_names:
#         docker_tags = ch.get_docker_tags_from_file(docker_name)
#         docker_versions = ch.get_docker_versions_json_file(docker_name)
#         docker = ch.get_docker_json_from_file(docker_name)
#         if docker is None or docker_tags is None or docker_versions is None:
#             continue
#         available_docker_names.append(docker_name)
#     ch.write_object_to_file(cc.available_new_docker_names_for_db_path, available_docker_names)
#     return available_docker_names
#
#
# def get_updated_available_docker_names_for_db_and_write_to_file():
#     docker_names = ch.get_updated_docker_names()
#     available_docker_names = list()
#     for docker_name in docker_names:
#         docker_versions = ch.get_docker_versions_json_file(docker_name)
#         docker = ch.get_docker_json_from_file(docker_name)
#         if docker is None or docker_versions is None:
#             continue
#         available_docker_names.append(docker_name)
#     ch.write_object_to_file(cc.available_updated_docker_names_for_db_path, available_docker_names)
#     return available_docker_names


def get_all_available_docker_names_and_write_to_file():
    """
    check if docker is available
    :return: return a list of docker names have docker json file in docker path
    """
    all_docker_names = ch.get_all_docker_names()
    available_docker_names = list()
    unavailable_docker_names = list()
    for docker_name in all_docker_names:
        docker = ch.get_docker_json_from_file(docker_name)
        dockerfile = ch.get_dockerfile_json_from_file(docker_name)
        docker_versions = ch.get_docker_versions_json_file(docker_name)
        docker_tags = ch.get_docker_tags_from_file(docker_name)
        if docker is None or docker_versions is None or docker_tags is None or dockerfile is None:
            unavailable_docker_names.append(docker_name)
            continue
        else:
            available_docker_names.append(docker_name)
    ch.write_object_to_file(cc.unavailable_docker_names_for_db_path, unavailable_docker_names)
    ch.write_object_to_file(cc.available_docker_names_for_db_path, available_docker_names)
    return available_docker_names


def classify_available_docker_names_and_write_to_file():
    """
    generate available_new_docker_names and available_updated_docker_names for generate sql
    :return: available_updated_docker_names, available_new_docker_names
    """
    available_all_docker_names_set = set(ch.read_object_from_file(cc.available_docker_names_for_db_path))
    all_docker_names_db_set = set(get_all_docker_names_database())
    available_updated_docker_names = list(available_all_docker_names_set & all_docker_names_db_set)
    available_new_docker_names = list(available_all_docker_names_set - all_docker_names_db_set)
    # for docker_name in available_all_docker_names:
    #     docker = get_docker_database(docker_name)
    #     if docker is None:
    #         available_new_docker_names.append(docker_name)
    #     else:
    #         available_updated_docker_names.append(docker_name)
    ch.write_object_to_file(cc.available_new_docker_names_for_db_path, available_new_docker_names)
    ch.write_object_to_file(cc.available_updated_docker_names_for_db_path, available_updated_docker_names)
    return available_updated_docker_names, available_new_docker_names


def execute_sql_with_path(sql_path, cur):
    try:
        with open(sql_path, 'r') as fp:
            for sql_line in fp.readlines():
                # print("execute sql_line: [%s]" % sql_line)
                print("execute %s" % sql_path)
                if sql_line is None:
                    continue
                if sql_line == "\n" or sql_line == "\r\n":
                    continue
                if sql_line == "begin;\n":
                    continue
                if sql_line == "commit;\n":
                    continue
                # print "one Line: [%s]" % sql_line
                cur.execute(sql_line)
                # print("execute sql_line success: [%s]" % sql_line)
    except Exception as e:
        raise e
    return


def execute_insert_sqls():
    conn = get_database_connection()
    cur = conn.cursor()
    sql_dir = ch.find_and_create_dirs(cc.semi_tag_rec_sql_dir)
    docker_names = get_all_docker_names_database()
    try:
        for docker_name in docker_names:
            # print docker_name
            sql_name = generate_insert_sql_fname(docker_name)
            insert_sql_path = os.path.join(sql_dir, sql_name)
            if os.path.exists(insert_sql_path) is False:
                logging.error("execute insert sql file error, insert sql file does not exist: [%s]" % insert_sql_path)
                continue
            docker_id = get_docker_id_database(docker_name)
            if docker_id is None:
                logging.error("execute insert sql file error, docker exists in database: [%s]" % docker_name)
                continue
            try:
                execute_sql_with_path(insert_sql_path, cur)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(e.message)
    finally:
        conn.close()
    return


def execute_sqls(sqls):
    conn = get_database_connection()
    cur = conn.cursor()
    temp_dir = "./.temp/"
    ch.find_and_create_dirs(temp_dir)
    for sql in sqls:
        # print("execute %s" % sql)
        try:
            temp_sql_path = os.path.join(temp_dir, "%s.sql" % id(sql))
            with open(temp_sql_path, "w") as sql_file:
                sql_file.write(sql)
            print("Write sql success")
            execute_sql_with_path(temp_sql_path, cur)
            conn.commit()
        except Exception as e:
            print("execute sql exception: %s" % sql)
            print("ExceptionMessage: %s" % e.message)
            conn.rollback()

    conn.close()
    import shutil
    shutil.rmtree(path=temp_dir)


def execute_update_sqls():
    conn = get_database_connection()
    cur = conn.cursor()
    sql_dir = ch.find_and_create_dirs(cc.incremental_update_sql_dir)
    docker_names = ch.read_object_from_file(cc.available_updated_docker_names_for_db_path)
    try:
        for docker_name in docker_names:
            print docker_name
            sql_name = generate_update_sql_fname(docker_name)
            update_sql_path = os.path.join(sql_dir, sql_name)
            if os.path.exists(update_sql_path) is False:
                logging.error("execute update sql file error, update sql file does not exist: [%s]" % update_sql_path)
                continue
            docker_id = get_docker_id_database(docker_name)
            if docker_id is None:
                logging.error("execute udpate sql file error, docker does not exist in database: [%s]" % docker_name)
                continue
            try:
                execute_sql_with_path(update_sql_path, cur)
                conn.commit()
            except Exception as e:
                conn.rollback()
                logging.exception(e.message, e.args)
                print(e.message)
    finally:
        conn.close()
    return


# def generate_available_docker_names_for_stars_and_pulls():
#     all_docker_names = get_all_docker_names_database()
#     available_docker_names = list()
#     unavailable_docker_names = list()
#     for docker_name in all_docker_names:
#         docker = ch.get_docker_json_from_file(docker_name)
#         if docker is None:
#             unavailable_docker_names.append(docker_name)
#             continue
#         else:
#             available_docker_names.append(docker_name)
#     ch.write_object_to_file(cc.unavailable_docker_names_for_db_path_for_stars_and_pulls, unavailable_docker_names)
#     ch.write_object_to_file(cc.available_docker_names_for_db_path_for_stars_and_pulls, available_docker_names)
#     return available_docker_names
#     pass



def generate_update_sql_fname_for_stars_and_pulls(docker_name):
    replaced_name = str(docker_name).replace("/", "#")
    fname = "update_for_stars_and_pull%s.sql" % replaced_name
    return fname


# def generate_update_sql_for_stars_and_pulls():
#     print "%s: start generate update sql for stars and pull" % ch.get_time()
#     sql_dir = ch.find_and_create_dirs(cc.incremental_update_sql_dir_for_stars_and_pulls)
#     # docker_names = ch.get_updated_docker_names()
#     docker_names = ch.read_object_from_file(cc.available_docker_names_for_db_path_for_stars_and_pulls)
#
#     for docker_name in docker_names:
#         sql_name = generate_update_sql_fname_for_stars_and_pulls(docker_name)
#         update_sql_path = os.path.join(sql_dir, sql_name)
#         if os.path.exists(update_sql_path):
#             logging.warn("update sql file exists: [%s]" % update_sql_path)
#             continue
#         sql_file = open(update_sql_path, "w")
#         sql_file.write("\nbegin;\n")
#         sql_update_docker = update_docker_sql_for_stars_and_pulls(docker_name)
#         # we never change the tags of dockers in the database
#         # sql_update_tags = update_docker_tags_sql(docker_name)
#         sql = "%s" % sql_update_docker
#         sql_file.write(sql)
#         sql_file.write("commit;\n")
#     print "%s: done generate update sql for stars and pull" % ch.get_time()
#     return None


def update_docker_sql_for_stars_and_pulls(docker_name):
    line_head = """update docker_manager.DockerManager_docker"""
    docker = ch.get_docker_json_from_file(docker_name)
    names = str(docker_name).split("/")
    u_name = names[0]
    d_name = names[1]
    # updated_time = ch.convert_ints2datetime(docker["last_updated"])
    # short_desc = generate_sql_string(docker["short_description"])
    # full_desc = generate_sql_string(docker["full_description"])
    stars = docker["star_count"]
    pulls = docker["pull_count"]

    line_sql = """%s set pulls=%d, stars=%d """ \
               % (line_head, pulls, stars) \
               + """where user_name="%s" """ % u_name \
               + """ and docker_name="%s";\n""" % d_name
    return line_sql


def generate_available_docker_names_and_write_to_file_for_stars_and_pulls():
    all_docker_names = get_all_docker_names_database()
    available_docker_names = list()
    unavailable_docker_names = list()
    for docker_name in all_docker_names:
        docker = ch.get_docker_json_from_file(docker_name)
        if docker is None:
            unavailable_docker_names.append(docker_name)
            continue
        else:
            available_docker_names.append(docker_name)
    ch.write_object_to_file(cc.unavailable_docker_names_for_db_path_for_stars_and_pulls, unavailable_docker_names)
    ch.write_object_to_file(cc.available_docker_names_for_db_path_for_stars_and_pulls, available_docker_names)
    return available_docker_names
    pass


def generate_update_sqls_and_write_to_file_for_stars_and_pulls():
    print "%s: start generate update sql for stars and pull" % ch.get_time()
    sql_dir = ch.find_and_create_dirs(cc.incremental_update_sql_dir_for_stars_and_pulls)
    # docker_names = ch.get_updated_docker_names()
    docker_names = ch.read_object_from_file(cc.available_docker_names_for_db_path_for_stars_and_pulls)

    for docker_name in docker_names:
        sql_name = generate_update_sql_fname_for_stars_and_pulls(docker_name)
        update_sql_path = os.path.join(sql_dir, sql_name)
        if os.path.exists(update_sql_path):
            logging.warn("update sql file exists: [%s]" % update_sql_path)
            continue
        sql_file = open(update_sql_path, "w")
        sql_file.write("\nbegin;\n")
        sql_update_docker = update_docker_sql_for_stars_and_pulls(docker_name)
        # we never change the tags of dockers in the database
        # sql_update_tags = update_docker_tags_sql(docker_name)
        sql = "%s" % sql_update_docker
        sql_file.write(sql)
        sql_file.write("commit;\n")
    print "%s: done generate update sql for stars and pull" % ch.get_time()
    return None


def execute_update_sqls_pulls_and_stars():
    conn = get_database_connection()
    cur = conn.cursor()
    sql_dir = ch.find_and_create_dirs(cc.incremental_update_sql_dir_for_stars_and_pulls)
    docker_names = ch.read_object_from_file(cc.available_docker_names_for_db_path_for_stars_and_pulls)
    try:
        for docker_name in docker_names:
            print docker_name
            sql_name = generate_update_sql_fname_for_stars_and_pulls(docker_name)
            update_sql_path = os.path.join(sql_dir, sql_name)
            if os.path.exists(update_sql_path) is False:
                logging.error("execute update sql pulls and stars file error, update sql file does not exist: [%s]" % update_sql_path)
                continue
            docker_id = get_docker_id_database(docker_name)
            if docker_id is None:
                logging.error("execute update sql pulls and stars file error, docker does not exist in database: [%s]" % docker_name)
                continue
            try:
                execute_sql_with_path(update_sql_path, cur)
                conn.commit()
            except Exception as e:
                conn.rollback()
                logging.exception(e.message, e.args)
                print(e.message)
    finally:
        conn.close()
    return
    pass


def update_new_col_pulls_and_stars():
    generate_available_docker_names_and_write_to_file_for_stars_and_pulls()
    generate_update_sqls_and_write_to_file_for_stars_and_pulls()
    execute_update_sqls_pulls_and_stars()
    pass


def generate_update_db_semi_tag_rec_sql():
    sql_dir = ch.find_and_create_dirs(cc.semi_tag_rec_sql_dir)
    # docker_names = ch.get_updated_docker_names()
    docker_names = get_all_docker_names_database()

    for docker_name in docker_names:
        sql_name = generate_insert_sql_fname(docker_name)
        semi_tag_sql_path = os.path.join(sql_dir, sql_name)
        if os.path.exists(semi_tag_sql_path):
            logging.warn("semi_tag_sql_path sql file exists: [%s]" % semi_tag_sql_path)
            continue
        with open(semi_tag_sql_path, "w") as sql_file:
            sql_file.write("\nbegin;\n")
            # we never change the tags of dockers in the database
            # sql_update_tags = update_docker_tags_sql(docker_name)
            sql = insert_docker_tags_sql(docker_name)
            sql_file.write(sql)
            sql_file.write("commit;\n")
    print "%s: done generate update sql" % ch.get_time()
    return None


if __name__ == "__main__":
    # get_all_available_docker_names_and_write_to_file()
    # classify_available_docker_names_and_write_to_file()
    # generate_insert_sql()
    # generate_update_sql()
    # execute("\n")
    # insert_sql_dir = cc.incremental_insert_sql_dir
    # sql_path = os.path.join(insert_sql_dir, "insert_00dingens#docker-whale.sql")
    # execute_sql_with_path(sql_path)
    # execute_insert_sqls()
    # execute_update_sqls()
    # print get_docker_id_database("insert_00dingens/docker-whale")
    # update_new_col_pulls_and_stars()
    # generate_update_db_semi_tag_rec_sql()
    execute_insert_sqls()
