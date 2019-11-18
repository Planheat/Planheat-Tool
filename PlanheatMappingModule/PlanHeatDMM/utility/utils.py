# -*- coding: utf-8 -*-
"""
   Miscelaneous utilities
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 29 Sep. 2017
"""

__docformat__ = "restructuredtext"

import os
import glob
import time
import sys
from config import config as Config
from functools import wraps



def load_dynamic_module(name, path, alias=None):
    import importlib
    spec = importlib.util.spec_from_file_location(name,path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if alias is None:
        alias = name
    sys.modules[alias]=mod


def install_and_import(name, package,version=None):
    import importlib
    try:
        importlib.import_module(name)
    except ImportError:
        import pip
        if version is not None:
            package += "==" + version
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(name)


def check_work_folders():
    try:
        base_path = Config.PLUGIN_DIR
        log_path= base_path + os.path.sep + Config.LOG_DIR_PATH
        temp_path= base_path + os.path.sep + Config.TEMP_DIR_PATH
        
        if not os.path.exists(log_path):
            os.makedirs(log_path)
            
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)     
               
    except Exception:
        raise   

def check_LIDAR_files(path):
    fileSearch = path + os.path.sep + "*." + Config.LIDAR_FILE_EXT
    dataList = glob.glob(fileSearch,recursive=False)
    
    if dataList:
        return True
    else:
        return False  
    
       
def check_no_other_files(path):
    fileLidarSearch = path + os.path.sep + "*." + Config.LIDAR_FILE_EXT
    fileAllSearch = path + os.path.sep + "*"
    dataLIDARList = glob.glob(fileLidarSearch,recursive=False)
    dataALLList   = glob.glob(fileAllSearch,recursive=False)
    
    if len(dataALLList) == len(dataLIDARList):
        return True
    else:
        return False


def clean_temp_files(log):
    
    log.write_log("INFO", "clean temporary files")
    path=Config.PLUGIN_DIR + os.path.sep + "temp"
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            try:
                os.remove(filename)  
            except:
                log.write_log("ERROR", "clean_temp_files unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
              
    

def clean_old_log_files(log):
    log.write_log("INFO", "clean old log files")
    now = time.time()
    path=Config.PLUGIN_DIR + Config.LOG_PARAMS['path'] 
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if name.rfind("." + Config.LOG_PARAMS["logExt"]) != -1:
                filename = os.path.join(root, name)
                timestamp = os.path.getmtime(filename)
                if now - Config.RAW_FILES_TTL * Config.DAYS_REMOVE_OLD_LOGS > timestamp:
                    try:
                        os.remove(filename)  
                    except:
                        log.write_log("ERROR", "clean_old_log_files unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                        pass
        

def showResults(dataList):
    total = 0
    ok = 0
    error = 0
    skip=0
    for data in dataList:
        total += 1
        if data.Regstatus and data.Regprocess:
            ok += 1 
        elif data.Regstatus and not data.Regprocess:
            skip += 1    
        else:   
            error += 1 
    
    return total, ok, error, skip      

def fix_encode_error_char_map(original_value):
    
    """ charmap unicode encode errors"""
    new_value = original_value
    new_value = new_value.replace("ā",'a')
    new_value = new_value.replace("Ā",'A')
    new_value = new_value.replace(u"\u0305",'') # corresponding with ̅
    new_value = new_value.replace(u"\u0304",'') # corresponding with ̄
    new_value = new_value.replace(u"\u0148",'n') # corresponding with ň

    return new_value
                
def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print ("{}  {:.2f} ms".format(method.__name__, (te - ts) * 1000))
        return result
    return timed
                
    #Decorator for control time process of a function
def time_control(self,function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" % (function.func_name, str(t1-t0)))
        return result
    return function_timer