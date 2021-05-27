#!/usr/bin/env python
# -*-coding:utf-8-*-


import os
import json
import logging
import tempfile
import shutil

logger = logging.getLogger(__name__)


def write_json(file, data):
    """
    采用更稳妥的写文件方式，先在另外一个临时文件里面写，确保写操作无误之后再更改文件名
    """
    fp = tempfile.NamedTemporaryFile(mode='wt', encoding='utf8', delete=False)
    try:
        json.dump(data, fp, indent=4, ensure_ascii=False)
        fp.close()
    except Exception as e:
        logger.error(f"write data to tempfile {fp.name} failed!!! \n"
                     f"{e}")
    finally:
        shutil.move(fp.name, file)


def get_json_file(json_filename):
    """
    :return:
    """
    if not os.path.exists(json_filename):
        data = {}
        write_json(json_filename, data)

    return json_filename


def get_json_data(json_filename):
    """
    获取json文件存储的值
    :return:
    """
    with open(get_json_file(json_filename), encoding='utf8') as f:
        res = json.load(f)
        return res


def get_json_value(json_filename, k):
    res = get_json_data(json_filename)
    return res.get(k)


def set_json_value(json_filename, k, v):
    """
    对json文件的某个k设置某个值v
    """
    res = get_json_data(json_filename)
    res[k] = v
    write_json(get_json_file(json_filename), res)
