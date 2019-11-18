# -*- coding: utf-8 -*-
"""
   loadData
   Load the csv with the hourly demand generated to the sqlite3 database and extract the aggregate consumption by day and time for the district 
   :author: Sergio Aparicio Vegas
   :version: 1.0
   :date: 22 Jan. 2018
   :copyright: (C) 2018 by Tecnalia

 ***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License or      * 
 *   any later version.                                                    *
 *                                                                         *
 ***************************************************************************
"""

__docformat__ = "restructuredtext"

import sys
import argparse
from src.main import loadData 

if __name__ == '__main__':
    
    try:
        parser = argparse.ArgumentParser()
        command_line = ""
        for command in sys.argv[:]:
            command_line +=  command + " "
             
        parser.add_argument("-d", "--db", type=str, help="sqlite3 database", required=True)
        parser.add_argument("-i", "--inputfile", type=str, help="Input csv file")
        parser.add_argument("-o", "--outputfile", type=str, help="Output csv file")
        parser.add_argument("-m", "--mantain",help="No Empty Table before load data",action="store_true")
        parser.add_argument("-t", "--total",help="Show fields totalized",action="store_false")
        parser.add_argument("-v", "--version",help="loadData Version",action="store_false")
        args = parser.parse_args()
            
      
                
        #print (args)
        if args.db is None:
            parser.print_help()
            sys.exit(1)
        
        if args.version is not None:
            print(__doc__)    
        
        print("LAUNCH", command_line)    
        loadData(args)
        
       
            
            

    except SystemExit as e:
        pass        
    