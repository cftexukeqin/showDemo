from django.shortcuts import render,redirect
from django.conf import settings
import base64

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.style.use('ggplot')

from ..utils import handle_memcache

# Create your views here.
import json
from random import randrange

from django.http import HttpResponse
from rest_framework.views import APIView

from pyecharts.charts import Bar,Line
from pyecharts import options as opts


# Create your views here.
def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, msg='',code=200):
    context = {
        "code": code,
        "msg": msg,
        "data": data,
    }
    return response_as_json(context)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error

# 柱状图函数
def bar_base() -> Bar:
    name_list = handle_memcache.get_value('name_list')
    rate_list = handle_memcache.get_value('rate_list')
    if name_list and rate_list:
        c = (
            Bar()
                .add_xaxis(name_list)
                .add_yaxis("App", rate_list)
                .set_global_opts(title_opts=opts.TitleOpts(title="App好评柱状图", subtitle="热门App好评率"))
                .dump_options_with_quotes()
        )
        return c
    else:
        c = (
            Bar()
        )
        return c

# 折线图函数
def line_base() -> Line:
    name_list = handle_memcache.get_value('name_list')
    comment_list = handle_memcache.get_value('comment_list')
    if comment_list:
        c = (
            Line()
                .add_xaxis(name_list)
                .add_yaxis("评论数量",comment_list )
                .set_global_opts(title_opts=opts.TitleOpts(title="App评论数折线图"))
                .dump_options_with_quotes()
        )
        return c
    else:
        c = (
            Line()
        )
        return c

def bar_img(request):
    if request.method == 'GET':
        return render(request,'showImg.html')
    else:
        name_list = handle_memcache.get_value('name_list')
        rate_list = handle_memcache.get_value('rate_list')
        comment_list = handle_memcache.get_value('comment_list')
        file_name_str = handle_memcache.get_value('file_name')
        encodestr = base64.b64encode(file_name_str.encode('utf-8'))
        file_name = str(encodestr, 'utf-8')
        if not name_list and not rate_list:
            data = {}
            return json_response(data,code=401,msg="参数错误")

        plt.figure(figsize=(15,10))
        plt.plot(name_list, comment_list,color='red',linewidth=3.0)
        # plt.bar(name_list, rate_list)
        # plt.legend()  # 显示图例，即label
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.xticks(rotation=45)
        plt.title('Title',fontsize=30)
        plt.xlabel("X轴",fontsize=20)
        plt.ylabel("数量",fontsize=20)
        plt.savefig(settings.MEDIA_ROOT + '/' + file_name_str + '_' + file_name + '.svg')

        data = {
            'img': settings.MEDIA_URL + file_name_str + '_' + file_name + '.svg'
        }
        return json_response(data=data, msg="success")

def upload_csv(request):
    data = {}
    if "GET" == request.method:
        return render(request, "index.html", data)
    # if not GET, then proceed
    csv_file = request.FILES.get("file")
    file_name = str(csv_file).split('.')[0]
    try:
        content = csv_file.read().decode('utf8')
        content_str = content.split("\n")
        name_list = []
        rate_list = []
        comment_list = []
        for line in content_str:
            if line:
                # 姓名
                name = line.split(',')[0]
                # 好评率
                rate = line.split(',')[1]
                # 评论数
                comment_times = int(line.split(',')[1])
                name_list.append(name)
                rate_list.append(rate)
                comment_list.append(comment_times)
            else:
                pass
        handle_memcache.set_key('file_name',file_name)
        handle_memcache.set_key('name_list',name_list)
        handle_memcache.set_key('rate_list',rate_list)
        handle_memcache.set_key('comment_list',comment_list)

        data = {
            'code':200,
            'msg':'上传成功!'
        }

        return json_response(data,msg="上传成功!")
    except Exception as e:
        data = {
            'code':401,
            'msg':'文件编码错误!'
        }
        return json_response(data,msg="文件编码错误!")

    # return render(request,'index.html')


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))


class LineView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(line_base()))


class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        return render(request,'index.html')


def delete_data(request):
    if request.method == 'POST':
        handle_memcache.delete_key('name_list')
        handle_memcache.delete_key('rate_list')
        handle_memcache.delete_key('comment_list')
        data = {
            'code': 200,
            'msg': 'success'
        }
        return json_response(data)