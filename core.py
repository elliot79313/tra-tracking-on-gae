# -*- coding: utf-8 -*-
import sys
import simplejson as json
reload(sys)
sys.setdefaultencoding("utf-8")
import re
import urllib
import urllib2
import logging

def crawl(date, station):

    form = {
        "searchdate": str(date.year)+"/"+ str(date.month) +"/"+str(date.day),
        "fromstation":station #Taipei:1008
    }

    payload = urllib.urlencode(form)
   
    method = "http://twtraffic.tra.gov.tw/twrail/mobile/ie_stationsearchresult.aspx?"+ payload


    res = (urllib2.urlopen(method)).read()

    return res

def parser(date, data):
    regex   = ur"TRSearchResult\.push\(\'(.*?)\'*\)"
    records = re.findall(regex,data); 


    print "[INFO] Available ", len(records)
    logging.info("[INFO] Available "+ str(len(records)))

    tra_log = []
    #We group 6 cells into a record

    for idx in range(0, len(records), 6):
        
        try:
            tra = { 
                "type"  : records[idx],   #車種
                "number": records[idx+1], #車次
                "time"  : records[idx+2], #開車時間
                "to"    : records[idx+3], #開往
                "dir"   : records[idx+4], #方向: 順逆
                "delay" : int(records[idx+5]), #晚點
                "index" : str(date.month) + "_" + str(date.day) +"_"+records[idx+1]
            }
            print tra["type"]
            print str(date.month) + "_" + str(date.day) +"_"+tra["number"]
        except:
            print "[ERROR] Index", idx

        tra_log.append(tra)
    
    return tra_log
