import os 
import time
import datetime

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
# from django.core.servers.basehttp import FileWrapper
from wsgiref.util import FileWrapper

from .model.urlmanager import UrlFile, User, CheckPoint


def make_response(res_code, res_desc, res_data):
    res = {
        'status': res_code,     # 1(success), 0(fail) 
        'desc': res_desc, 
        'result': res_data
    }
    
    return JsonResponse(res)


def res_error(err_no, res_data=''):
    errors = {
        0: 'Authentication error',
        1: 'Invalid key Error',
        2: 'Service expiration exceeded',
	3: 'Invalid url file version',
        4: 'There is no verion information',
    }
    
    return make_response(0, errors.get(err_no, 'Undefined Error'), res_data)


def is_valid_file_key(file_key):
    qs = User.objects.filter(file_key__exact=file_key)\
                    .order_by('-reg_date')[:1]
    if len(qs) == 0:
        return False
    info = qs[0]
   
    current = datetime.datetime.now()
    now = time.time()
    start_ts, end_ts = info.valid_start.timestamp(), info.valid_end.timestamp() 
    if (start_ts > now) or (end_ts < now):
        return False
    return True


def get_last_ver():
    def lookup_ver(t):
        qs = CheckPoint.objects.filter(file_type__exact=t).order_by('-id')[:1]
        if len(qs) == 0:
            return None
        return '{type}.{ver}'.format(type=qs[0].file_type, ver=qs[0].file_ver) 

    part_ver = lookup_ver('part')
    full_ver = lookup_ver('full')    
    if not (part_ver and full_ver):
        return []
    return part_ver, full_ver
   
 
def urldb_info(request, file_key):
    # lookup url file info
    if not is_valid_file_key(file_key):
        return res_error(1)

    vers = get_last_ver()
    if not vers:
        return res_error(4)
    
    # make response with urlfile verison
    res_data = { 
        'last_url_ver': vers
    }
    
    return make_response(1, 'Succes', res_data)


def get_file_path(file_ver):
    tkns = file_ver.split('.', 1)
    if len(tkns) != 2:
        return None
    qs = CheckPoint.objects.filter(file_ver__exact=tkns[1]).filter(file_type__exact=tkns[0])[:1]
    if len(qs) != 1:
        return None
    return qs[0].file_path


def make_full_path(fname):
    # ver format : full.0001.0.0.10
    home_dir = '/var/www/html/data/url_files'
    tkns = fname.split('.')
    file_path = os.path.join(home_dir,tkns[-4], tkns[-3], fname)
    return file_path


def urldb_download(request, file_key, file_ver):
    if not is_valid_file_key(file_key):
        return res_error(1)
    file_name = get_file_path(file_ver)
    if not file_name:
        return res_error(3, file_ver)
    file_path = make_full_path(file_name)
    response = HttpResponse(FileWrapper(open(file_path,'rb')), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename='+file_name
    return response
