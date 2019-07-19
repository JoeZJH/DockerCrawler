# -*- coding: utf-8 -*-
import crawler_helper as ch
import crawler_config as cc


def count_all_docker_images_size():
    docker_names = ch.get_all_docker_names()
    images_size = 0
    images_count = 0
    for docker_name in docker_names:
        size, count = count_docker_image_size(docker_name)
        images_size += size
        images_count += count
    return images_size, images_count


def count_docker_image_size(docker_name):
    docker_versions = ch.get_docker_versions_json_file(docker_name)
    if docker_versions is None:
        return 0, 0
    size = 0
    count = 0
    for docker_version in docker_versions:
        # print docker_version["full_size"]
        count += 1
        size += docker_version["full_size"] if docker_version["full_size"] is not None else 0
    return size, count


def write_images_size_and_count_to_file(size, count):
    data = {"images_size": size, "images_count": count}
    ch.write_object_to_file(cc.images_size_count_path, data)


if __name__ == "__main__":
    size, count = count_all_docker_images_size()
    write_images_size_and_count_to_file(size, count)
    print size, count
