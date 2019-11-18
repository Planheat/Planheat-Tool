# -*- coding: utf-8 -*-
"""
   Process Own Exceptions 
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 12 sep. 2017
"""

__docformat__ = "restructuredtext"

class MaxRetryExceeded(Exception):
    """ Number of attempts exceeded """
    pass


class NoDataFoundException(Exception):
    """ No data found on database table """
    pass


class NumberIncorrectException(Exception):
    """ Number of columns on CSV incorrect """ 
    pass


class ShapeFileFormatException(Exception):
    """ shp file format not valid for process """
    pass


class DBNotFoundException(Exception):
    """ DB file not found on filesystem"""
    pass


class NotFoundResourceException(Exception):
    """ Java jar file not found on fileSystem """
    pass


class DataValueNoneException(Exception):
    """ The properties required by the process have None value """
    pass


class ZeroValueException(Exception):
    """ The properties required by the process have Zero value """
    pass

class WrongValueException(Exception):
    """ The properties required by the process have wrong value """
    pass

class NoProcessException(Exception):
    """ the building use not evaluate """
    pass


class JavaProcessException(Exception):
    """ Java process finish with error, non 0 value """
    pass

class NOANoDataFoundException(Exception):
    """ No data Found for given logitude and latitude """
    pass

class LoadScenarioException(Exception):
    """ Error loading saved scenario from pickle """
    pass