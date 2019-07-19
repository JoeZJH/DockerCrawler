import crawler_helper as ch
import mysql_helper as mh
import crawler_config as cc
import os
import re
import shutil

old_dockerfiles_dir = "D:\\IdeaProjects\\DockerManagerSystem\\docker-manager-system\\data\\dockerfile"
new_dockerfiles_dir = "D:\\IdeaProjects\\DockerManagerSystem\\docker-manager-system\\data\\new_dockerfiles"


def refactor_dockerfiles_database():
    sql = """select id, dockerfile_path from docker_manager.DockerManager_dockerversion where dockerfile_path like "%.txt" """

    conn = mh.get_database_connection()
    cur = conn.cursor()
    cur.execute(sql)
    sqls = list()
    refactor_paths = list()
    # print cur.fetchall().__len__()
    for row in cur.fetchall():
        docker_version_id = row[0]
        dockerfile_path = row[1]
        dockerfile_path_strip = str(dockerfile_path)[0: -4]
        names = re.split("/|_", dockerfile_path_strip, 3)
        print names
        docker_name = "%s/%s" % (names[2], names[3])
        timestamp = "1970-01-01-00-00-00"
        new_dockerfile_path = ch.generate_dockerfile_fname(docker_name, timestamp=timestamp)
        refactor_path = dict()
        refactor_path["src"] = dockerfile_path
        refactor_path["dst"] = new_dockerfile_path
        refactor_paths.append(refactor_path)
        sql = """update docker_manager.DockerManager_dockerversion set dockerfile_path = "%s" where id = %s; """ \
              % (new_dockerfile_path, docker_version_id)

        sqls.append(sql)
    cur.close()
    conn.close()
    ch.write_object_to_file("D:\\IdeaProjects\\DockerManagerSystem\\docker-manager-system\\data\\refactor_dockerfiles.json", refactor_paths)
    # refactor dockerfiles
    print refactor_paths.__len__()
    # for refactor_path in refactor_paths:
    #     refactor_dockerfile(refactor_path["src"], refactor_path["dst"])


    # rename dockerfile names
    conn = mh.get_database_connection()
    update_cur = conn.cursor()
    update_cur.execute("begin;")
    for sql in sqls:
        print sql
        update_cur.execute(sql)
    update_cur.execute("commit;")
    update_cur.close()
    pass


def refactor_dockerfile(src, dst):
    raw_text_path = os.path.join(old_dockerfiles_dir, src)
    # names = filename.split("_")
    dockerfile_json = dict()
    dockerfile_content = ch.read_text_from_file(raw_text_path)
    dockerfile_json["contents"] = dockerfile_content
    dockerfile_path = os.path.join(new_dockerfiles_dir, dst)
    ch.write_object_to_file(dockerfile_path, dockerfile_json)


def copyfile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        print "%s doesn't not exist!" % srcfile
    else:
        fpath, fname = os.path.split(dstfile)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        shutil.copyfile(srcfile, dstfile)
        # print "copy %s -> %s" % (srcfile, dstfile)


if __name__ == "__main__":
    refactor_dockerfiles_database()
