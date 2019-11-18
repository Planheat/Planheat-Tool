# -*- coding: utf-8 -*-
"""
   Model Map refurbishment tab values
   :author: Sergio Aparicio Vegas 
   :version: 0.2  
   :date: 30 Nov 2017
"""
__docformat__ = "restructuredtext"

class RefurbishmentTabData():
    
    """ Refurbishment tab data for each building use """

    def __init__(self,index,name,check):
        self.__tab_index   = index
        self.__tab_name    = name
        self.__tab_check   = check
        
        self.__rows = []
        
     
    def __str__(self):
        return "index:" + str(self.__tab_index) + " name:" + str(self.__tab_name) + " checked: " + str(self.__tab_check)    
     
                 
   
    @property
    def tab_index(self):
        return self.__tab_index
    
    @tab_index.setter
    def tab_index(self, val):
        self.__tab_index = val
    
    
    @property
    def tab_name(self):
        return self.__tab_name
    
    @tab_name.setter
    def tab_name(self, val):
        self.__tab_name = val         
             
    
    @property
    def tab_check(self):
        return self.__tab_check
    
    @tab_check.setter
    def tab_check(self, val):
        self.__tab_check = val
    
        
    @property
    def rows(self):
        return self.__rows                 
        
    @rows.setter
    def rows(self, val):
        self.__rows = val
        
        
            
class RowRefurbishTableData():
    
    """ Refurbishment period data for each building use """

    def __init__(self):
        self.__row_index                = 0
        self.__row_period_id            = 0
        self.__row_period_text          = ""
        self.__row_refurbishment_level  = ""
        self.__row_roof_percentage      = 0
        self.__row_wall_percentage      = 0
        self.__row_window_percentage    = 0
     
    def __str__(self):
        return "index:" + str(self.__row_index) + " row_period_id:" + str(self.__row_period_id) + " period_text:" + self.__row_period_text + " refurbishment_level: " + str(self.row_refurbishment_level) \
            +  " roof_percentage:" + str(self.__row_roof_percentage) +  " wall_percentage:" + str(self.__row_wall_percentage) +  " window_percentage:" + str(self.__row_window_percentage)      
     
                 
   
    @property
    def row_index(self):
        return self.__row_index
    
    @row_index.setter
    def row_index(self, val):
        self.__row_index = val
    
    
    @property
    def row_period_id(self):
        return self.__row_period_id
    
    @row_period_id.setter
    def row_period_id(self, val):
        self.__row_period_id = val
        
    
    @property
    def row_period_text(self):
        return self.__row_period_text
    
    @row_period_text.setter
    def row_period_text(self, val):
        self.__row_period_text = val         
             
             
    @property
    def row_refurbishment_level(self):
        return self.__row_refurbishment_level
    
    @row_refurbishment_level.setter
    def row_refurbishment_level(self, val):
        self.__row_refurbishment_level = val
    
  
    
    @property
    def row_roof_percentage(self):
        return self.__row_roof_percentage
    
    @row_roof_percentage.setter
    def row_roof_percentage(self, val):
        self.__row_roof_percentage = int(val)              
  
    
        
    @property
    def row_wall_percentage(self):
        return self.__row_wall_percentage
    
    @row_wall_percentage.setter
    def row_wall_percentage(self, val):
        self.__row_wall_percentage = int(val)              
    
    
        
    @property
    def row_window_percentage(self):
        return self.__row_window_percentage
    
    @row_window_percentage.setter
    def row_window_percentage(self, val):
        self.__row_window_percentage = int(val)    
            
    
            