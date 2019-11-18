# -*- coding: utf-8 -*-
"""
   Shape Files Write API   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 18 sept. 2017
"""
__docformat__ = "restructuredtext"  



import sys
import os
import copy
import externModules.shapefile as shp


class Shape_Writer():
    """ API for write output SHAPE format files (shp, dbf,shx, prj)
     
        Write GIS output files   
    """  

    def __init__(self,log, filename,outputFieldsShape,boolAddShapeFields,userFieldShapeMap,spatialReferenceWKT=None):
        """
        Constructor
        
        :param log: logger object
        :param filename: Work files without extension name
        :param outputFieldsShape: output fields for shape files
        :param spatialReferenceWKT: Spatial Reference, Well Known Text format
        
        """        
        self.filename = filename

        self.__spatialReferenceWKT = spatialReferenceWKT
        
        self.__log=log
        
        self.__outputFieldsShape = copy.deepcopy(outputFieldsShape)
        
        self.__boolAddShapeFields =  boolAddShapeFields
        self.__userFieldShapeMap  =  userFieldShapeMap
        
        #Set up shapefile writer and create empty fields
        self.__w = shp.Writer(shapeType=shp.POLYGON)
        #self.__w = shp.Writer(shapeType=shp.POINT)
        self.__w.autoBalance = 1 #ensures gemoetry and attributes match
        

        

    def populateAll(self,dataList=[]):
        """
        Populate data in shape records 
        
        :param dataList: building list for populate records
        
        """   
        
        try:
            #Assign the output record for shp file 
            self.assignOutputRecord()
            
            #loop through the data and write the shapefile
            for building in dataList:
                try:
                    if building.Regstatus and building.Regprocess:
                        #BUGFIX 0.25
                        pointList       = []
                        dataRecord      = []
                        
                        
                        end = len(building.shpGeometryData.points) 
                        for part in building.shpGeometryData.parts[::-1]:
                            subset = building.shpGeometryData.points[part:end]
                            end = part
                            pointList.append(subset)
                        pointList.reverse()
                        
                        
                        #pointList  = [[point for point in points] for points in building.shpGeometryData.points]
                        #print ("writer", building.reference, pointList, len(building.shpGeometryData.points))
                        #self.__w.poly(parts=[pointList])
                         
                        self.__w.poly(parts=pointList)

                        dataRecord = [self.formatValue(outputField.headerName,getattr(building,outputField.attributeName),outputField.format,outputField.length,outputField.precision) for outputField in self.__outputFieldsShape ]
                        
                        if self.__boolAddShapeFields and self.__userFieldShapeMap:
                            userFieldslist  = []
                            for userFieldMap in self.__userFieldShapeMap:
                                userFieldslist.append(building.shpRecordData[userFieldMap.position])
                            else:
                                dataRecord.extend(userFieldslist)
                            
                        self.__w.record(*dataRecord)
                        
                        
                        
                        """ 
                        print(building.projectID,building.areaID,building.countryID,building.reference, building.centroid,\
                                        building.annualEnergyDemand,building.annualEnergyDemandSquareMeter, building.hourlyMaximumEnergyDemand,\
                                        building.totalHeight, building.footPrintArea, building.grossFloorArea,building.numberOfFloors,building.roofArea,building.exteriorEnvelopeArea,\
                                        building.volume,building.protectionLevel) #write the attributes
                        
                        
                        self.__w.record(building.projectID,building.areaID,building.countryID,building.reference, building.centroid,\
                                        building.annualEnergyDemand,building.annualEnergyDemandSquareMeter, building.hourlyMaximumEnergyDemand,\
                                        building.totalHeight, building.footPrintArea, building.grossFloorArea,building.numberOfFloors,building.roofArea,building.exteriorEnvelopeArea,\
                                        building.volume,building.protectionLevel) #write the attributes
                        """
                except:
                    building.Regstatus = False 
                    self.__log.write_log("ERROR", "populateAll shp write record - reference " +  str(building.reference) +  " unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                                   
        except:
            self.__log.write_log("ERROR", "populateAll shp write  unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    

  
    def saveShapeFile(self):    
        """
        Create and write shp file  
        
        """   
        try:
            self.__w.saveShp(self.filename)
            self.__log.write_log("INFO", "saveShapeFile  - " +  self.filename + " Created")
        except :
            self.__log.write_log("ERROR", "saveShapeFile  unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    


    def saveQgisFiles(self):    
        """
        Create and write shape files 
        """   
        try:
            self.__w.save(self.filename)
            try:
                if self.__spatialReferenceWKT is not None:
                    file_name_no_extension = os.path.splitext(self.filename)[0]
                    prjOut = open(file_name_no_extension +".prj", "w")
                    prjOut.writelines(self.__spatialReferenceWKT)
                    prjOut.close()
                
                #prjOut = open( self.filename +".prj", "w")
                #epsg = self.getInternetWKT_PRJ()
                #prjOut.write(epsg)
                #prjOut.close()
                
                
            except:
                self.__log.write_log("ERROR", "saveQgisFiles saving projection file .prj  unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                raise
            self.__log.write_log("INFO", "saveQgisFiles  - " + self.filename + " Saved")
        except :
            self.__log.write_log("ERROR", "saveQgisFiles  unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))   
            raise 



    def assignOutputRecord(self):
        """
        Assign to shape files the format of records 
        
        """   
        
        try:
            for outputFields in self.__outputFieldsShape:
                self.writeRecordFormat(outputFields.headerName,outputFields.format,outputFields.length,outputFields.precision)
            
           
            if self.__boolAddShapeFields and self.__userFieldShapeMap:
                for userFieldShape in self.__userFieldShapeMap:  
                    self.__w.field(userFieldShape.key,userFieldShape.dataFormat,userFieldShape.length,userFieldShape.precision)  

        except:
            raise
                                  
    def writeRecordFormat(self,key,dataFormat,length,precision):
        """
        Populate data in shape records 
        
        :param key: Name of data header 
        :param dataFormat: type of data
        :param length: length of data
        :param precision: decimals of data if is a number 
        
        """   
        
        try:
            if dataFormat in ('str'):
                if length is not None:
                    self.__w.field(key,'C',size=str(length))
                else:
                    self.__w.field(key,'C')    
            elif dataFormat in ('float'):
                if length is not None and precision is not None:
                    self.__w.field(key,'N',size=str(length),decimal=precision)
                elif length is not None:
                    self.__w.field(key,'N',str(length))
                elif precision is not None:
                    self.__w.field(key,'N',decimal=precision)    
                else:
                    self.__w.field(key,'N')    
            elif dataFormat in ('int'):
                if length is not None:
                    self.__w.field(key,'N',str(length),decimal=0)
                else:
                    self.__w.field(key,'N',decimal=0)    
            elif dataFormat in ('date'):
                self.__w.field(key,'D')
            elif dataFormat in ('boolean'):
                self.__w.field(key,'L')
                
        except: 
            self.__log.write_log("ERROR", "writeRecordFormat  unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise       
        
    def formatValue(self,key, value, dataFormat, length, precision):
        
        """
        Data formatting

        :param key: dict key to transform
        :param value: dict value to transform
        :param dataFormat: type of format
        :param length: max length of data
        :param precision: precision if is a number
        :returns: value transformed into the corresponding format and styling
        """  
        
        try:
            
            result = str(value)
            if dataFormat in 'float':
                result = result.replace(",",".")
                result = "{:{}.{}f}".format(float(result),length,precision)
                result = result.strip()
                result = float(result)
            elif dataFormat in 'int':   
                result = result.replace(",",".")
                result = "{:{}.0f}".format(float(result),length)
                result = result.strip()
                result = int(result)
            elif dataFormat in 'str' and length is not None and length > 0:
                result = "{:.{}}".format(result,length)
                result = result.strip()
            elif dataFormat in 'boolean':
                if result is None or result.lower() == "false" or result == "0":  
                    result = False
                else:
                    result = True
            elif dataFormat in 'date':
                pass               
            
            return result
        
        except:
            self.__log.write_log("ERROR", "SHP formatValue - key " + key + " value " + value + " Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            return str(value)
        
        
    #def getInternetWKT_PRJ (self):
    #    #Create a projection file (.prj)
    #    try:
            
    #        import urllib
    #        epsg="3057"
    #        wkt = urllib.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg))
    #        remove_spaces = wkt.read().replace(" ","")
    #        output = remove_spaces.replace("\n", "")
    #        return output
    #    except:
    #        raise


if __name__ == '__main__':     
    points = [(306071.40986368, 252439.71721231248), (306069.50166681403, 252440.5027735775), (306068.698077736, 252440.8962055875), (306067.99461009854, 252441.29094035248), (306067.2878705185, 252441.98530876747), (306066.482318275, 252442.57936504748), (306065.975821576, 252443.37599973), (306065.2697363845, 252444.07101952247), (306064.35621003853, 252445.56462812997), (306063.646198516, 252446.75990584248), (306062.8314848335, 252448.45413871997), (306062.21963158605, 252449.85069207998), (306039.27873394155, 252440.45522302), (306038.0576450005, 252442.84773257747), (306035.7659764735, 252441.62770251997), (306035.3576380495, 252442.6249614725), (306032.0451234625, 252443.799395105), (306032.5332972835, 252445.30407713), (306030.92546473903, 252446.0915925275), (306026.30613631755, 252448.05549568997), (306025.40177141054, 252448.44827632248), (306024.416916718, 252446.53908887), (306020.8014202555, 252448.11086277748), (306020.20330916654, 252447.80536672997), (306018.9796026715, 252450.59782207248), (306016.285485217, 252449.57515939747), (306007.81573486154, 252469.52164120247), (306005.36766748305, 252475.206212645), (305999.1293819125, 252491.46850330997), (305996.98887712904, 252496.25482518), (305995.250821273, 252500.74411891), (305997.44629469054, 252501.4625882925), (305997.2421254785, 252501.9615434575), (305996.423485465, 252504.15668563248), (305997.021596554, 252504.46153030248), (305995.4909818525, 252508.05192308247), (305992.9401754795, 252514.03612817498), (305992.24128856155, 252513.830292885), (305991.41872221703, 252516.52569297998), (305988.5269794355, 252515.20079114498), (305978.8197804265, 252539.64112632247), (305981.2122247825, 252540.7614956225), (305979.990481453, 252543.35397807247), (305981.2881338485, 252543.76434589748), (305981.77761644655, 252545.0697064075), (305986.58606314455, 252556.71829023998), (305987.17370401754, 252558.324587155), (305986.865487034, 252559.32249748497), (305989.659725929, 252560.24615077997), (305988.7363837555, 252563.0412116325), (306010.0786102945, 252572.12271673747), (306011.508449167, 252568.6313333375), (306013.605109921, 252569.2488392075), (306014.903416705, 252569.5601976525), (306016.27632377803, 252573.07372788747), (306043.3032232165, 252584.60441239248), (306052.1767312765, 252588.68008140998), (306052.575253873, 252588.88331118997), (306054.27208325354, 252589.4975601725), (306055.576279534, 252589.10803642747), (306056.5572078955, 252591.51813317748), (306066.830452957, 252595.8054998825), (306078.6820830805, 252590.59773676997), (306086.6171980315, 252587.06010556748), (306090.10770629055, 252588.58953993747), (306083.47286128905, 252604.44797655247), (306094.744048813, 252609.0440961925), (306099.1317237055, 252598.77187301748), (306103.8498647905, 252597.00859412499), (306118.9112705065, 252603.13675364497), (306124.412714626, 252615.791715715), (306122.67923948955, 252619.6810907675), (306134.34960399853, 252624.47978881), (306140.5741474105, 252609.81923541747), (306139.39363055653, 252607.30752377748), (306144.31463207654, 252605.24591399), (306155.70491830754, 252631.96020801997), (306172.561311679, 252638.90389216997), (306174.87261186104, 252637.82195414248), (306175.460252734, 252639.32793892248), (306177.6544173745, 252640.24638119747), (306180.204569359, 252634.36248823997), (306182.1435224845, 252629.77483650748), (306164.98676479154, 252622.829198225), (306152.120832493, 252593.00001698997), (306161.10493220954, 252571.35604542), (306165.12156882253, 252569.68721626498), (306177.99011867505, 252574.796621375), (306179.72621136555, 252570.5073005375), (306178.647124729, 252567.8965795175), (306180.5873866315, 252563.10830351498), (306165.726878185, 252556.88243737), (306163.919457148, 252557.56768649997), (306162.84102490003, 252554.856653345), (306174.2895517075, 252550.04688188498), (306177.8598953635, 252541.769176615), (306177.86251291755, 252541.4688915875), (306169.7284638625, 252544.80524714247), (306167.1711136045, 252539.37992394497), (306168.6984563635, 252536.1901283275), (306171.912158287, 252534.815070425), (306172.72752635804, 252533.01987403497), (306167.84120742854, 252530.87879619247), (306163.45680447854, 252540.750422205), (306149.59881921404, 252546.5418195575), (306142.6171483075, 252543.582611575), (306147.62322033255, 252531.1132920925), (306121.691767243, 252520.192948305), (306119.64942073455, 252525.17989444497), (306106.49293994205, 252530.7771813025), (306101.8055551165, 252528.83737910748), (306090.88642860553, 252554.56874448998), (306095.174636446, 252556.40562903997), (306098.96550902654, 252557.93766891997), (306093.252043033, 252571.20166895248), (306073.76958861103, 252579.44875947997), (306066.4371654685, 252582.691316675), (306059.35602751, 252579.73145731498), (306057.315644167, 252584.418769805), (306055.02201247454, 252583.39871264), (306054.623489878, 252583.19548285997), (306056.561788615, 252578.70749188497), (306047.286486016, 252574.82853887248), (306082.8583904875, 252483.84673518248), (306076.07630807353, 252480.98849071248), (306087.9141960385, 252453.06328590997), (306095.8139740105, 252453.82800309497), (306103.2124903915, 252454.68912414997), (306110.8099408765, 252455.75217223), (306115.80750585103, 252444.28401996498), (306115.307553037, 252444.28011169998), (306107.907727879, 252443.51865140247), (306100.507902721, 252442.75784248248), (306071.40986368, 252439.71721231248), (306006.93492794054, 252503.8420703), (306007.44535097055, 252502.5451776975), (306025.89714350505, 252510.302432345), (306032.77803858253, 252513.26098894997), (306031.854696409, 252516.05539842497), (306032.54180433403, 252517.6623467175), (306033.81720752054, 252520.77527979), (306033.41933931253, 252520.471737875), (306033.02212549304, 252520.16819596), (306032.72306994855, 252519.9656175575), (306032.32454735204, 252519.76238777747), (306031.8252489265, 252519.6581673775), (306031.42541755305, 252519.55459835497), (306031.026240568, 252519.45168071), (306030.5256333655, 252519.44712106747), (306030.1251476035, 252519.44386417998), (306029.62454040104, 252519.54026804998), (306029.22340025054, 252519.63667192), (306028.820951323, 252519.83403930248), (306028.419156784, 252520.03075530747), (306028.017362245, 252520.22747131248), (306027.7143803695, 252520.52515082998), (306027.311931442, 252520.82217896997), (306027.0089495665, 252521.11985848748), (306026.8060891315, 252521.51850151748), (306026.60257430805, 252521.91714454748), (306026.39905948454, 252522.31578757748), (306026.195544661, 252522.71443060748), (306026.09215127805, 252523.11437639248), (306025.988757895, 252523.5136708), (306025.984831564, 252524.01392871997), (306025.9815596215, 252524.4145258825), (306026.077754731, 252524.91543517998), (306026.17460422905, 252525.31668371998), (306026.370920779, 252525.71858363747), (306026.467770277, 252526.11983217747), (306026.764862656, 252526.52238347247), (306026.96183359454, 252526.92428339), (306027.259580362, 252527.22717392747), (306027.65744857, 252527.53071584247), (306027.95519533753, 252527.8329550025), (306028.35371793405, 252528.03683615997), (306028.7522405305, 252528.24006594), (306029.15207190404, 252528.34363496248), (306029.551248889, 252528.4465526075), (306030.051201703, 252528.55077300748), (306030.4510330765, 252528.554029895), (306025.83235904353, 252530.41762092247), (306024.60603499453, 252533.5103612925), (306014.03438877704, 252529.02041618497), (305998.77470334555, 252522.59066888248), (305999.997755452, 252519.89852567497), (305997.10208633955, 252519.07388175998), (305998.427223052, 252516.1824170375), (305997.329159149, 252515.77335196748), (305999.88061991055, 252509.78914687497), (306001.30980439455, 252506.29841485247), (306002.4065595205, 252506.8077920575), (306003.52949018654, 252504.11434609498), (306004.926609634, 252504.62632880997), (306006.422541745, 252505.2392750375), (306006.93492794054, 252503.8420703), (306150.122330014, 252568.16364429248), (306140.21946884354, 252592.00210666), (306141.69707807654, 252594.91636959498), (306135.26901984104, 252597.66583402248), (306133.25939275755, 252598.65071680248), (306131.87928741105, 252596.13705102997), (306106.94250484154, 252585.92540596248), (306105.96026770305, 252583.71528210497), (306102.917361178, 252576.38467971998), (306109.039819984, 252562.02310859997), (306110.2366965505, 252562.53313718247), (306131.183018047, 252571.11112748), (306137.7197047735, 252555.05206659497), (306151.085589886, 252560.4656649975), (306152.893010923, 252559.77976448997), (306154.0715646115, 252562.4914490225), (306152.064555082, 252563.17539539747), (306150.122330014, 252568.16364429248)]
    parts  = [0, 134, 196]
    pointList = []
    end = len(points) 
    for part in parts[::-1]:
        #print (part) 
        subset = points[part:end]
        end = part
        print ("subset",len(subset),subset)
        pointList.append(subset)
    pointList.reverse()
    
    print("PointlistFinal",pointList)
    