# -*- coding: utf-8 -*-

""" Testing API code """

from rapydo.rest.definition import EndpointResource
from rapydo.utils.logs import get_logger
import dateutil.parser
# import json

log = get_logger(__name__)
# FAKE just to test
# RESPONSE1 = [
#     {
#         'pid': '11099/qwoprerc-343536ssdfjs-34500-asdpwe94383',
#         'network': {
#             'name': 'NN',
#             'links': {
#                 'self': 'webservices/networks/...'
#             }
#         },
#         'station' : {'name' : 'SSSS','links' : {'self' : 'webservices/stations/...'}},'channel' : {'name' : 'CCC','links' : {'self' : 'webservices/channel/...'}}},{"others" : "......."}]

# RESPONSE2 = [{"pid" : "11099/qwoprerc-343536ssdfjs-34500-asdpwe94383" ,"metadata": {"dc:contributor" : "network operator","dcterms:dateAccepted" : "2017-03-06T11:35:07.114Z","dc:identifier" : "test/f2c3ea40-0260-11e7-9f93-0242ac110008","dc:type" : "seismic waveform","dc:subject" : "mSEED, waveform, quality","dcterms:isPartOf" : "wfmetadata_catalog","dc:title" : "INGV_Repository","dc:rights" : "open access","dc:format" : "MSEED","dcterms:available" : "available from now","dc:date" : "2017-03-06T11:35:07.114Z","dc:coverage:x" : "LAT_val","dc:publisher" : "INGV EIDA NODE","dc:creator" : "INGV EIDA NODE","dc:coverage:t:min" : "time_start_val","dc:coverage:t:max" : "time_end_val","dc:coverage:x" : "LAT_val","dc:coverage:y" : "LON_val","dc:coverage:z" : "ELE_val","fileId" : "IV.ARCI..HHN.D.2015.011","smean" : 587.6017203352374,"stdev" : 25154.453024673716,"rms" : 25161.315203149203,"fileId" : "IV.ARCI..HHN.D.2015.011","type" : "seismic","status" : "open","glen" : 27054.59,"enc" : "STEIM2","srate" : 100,"gmax" : 27054.59,"sta" : "ARCI","net" : "IV","cha" : "HHN","loc" : ""}}]


class DataMongo(EndpointResource):

    def get(self):
        # # --> important into mongo collections we must have:
        # #     "_cls" : "eudat.models.mongo.wf_do"
        mongohd = self.get_service_instance(
            service_name='mongo', database='wfcat')
        # test:
        #mongohd.Testing(onefield='justatest1').save()
        #log.info("just a test - mongo insert")
        #return "Hello world!"
        
        # real:
        myargs = self.get_input()
        print(myargs)
        documentResult1 = []
        
        mycollection = mongohd.wf_do
        
        myStartDate = dateutil.parser.parse(myargs.get("start"))
        myEndDate = dateutil.parser.parse(myargs.get("end"))
        myLat = float(myargs.get("minlat"))
        myLon = float(myargs.get("minlon"))
        myLatX = float(myargs.get("maxlat"))
        myLonX = float(myargs.get("maxlon"))

        myfirstvalue = mycollection.objects.raw({"dc_coverage_x": { "$gte" : myLat }, "dc_coverage_y": { "$gte" : myLon }, "dc_coverage_x": { "$lte" : myLatX }, "dc_coverage_y": { "$lte" : myLonX },"dc_coverage_t_min": { "$gte" : myStartDate },"dc_coverage_t_max": { "$lte" : myEndDate }})
        # #myfirstvalue = mongohd.wf_do.objects.all()
        for document in myfirstvalue:
                myLine = [document.fileId,document.dc_identifier,document.irods_path, document.dc_coverage_x, document.dc_coverage_y ]
                documentResult1.append(myLine)

        

        if myargs.get('download') == 'true':
            
            icom = self.get_service_instance(service_name='irods') 
            
                
            try:
                for document in myfirstvalue:
                    print(document.irods_path)
                    icom.icom.read_in_streaming(document.irods_path)
            except:
                self.force_response('errore')
            
            return("download ok")

        else:
            
            return  ["total files to download: "+str(len(documentResult1)) +" format:< fileId - PID - Lat - Lon >",documentResult1]   # ,documentResult1


class MetaMongo(EndpointResource):

    def get(self):
        #return "Hello world!"
    
    
        # # --> important into mongo collections we must have:
        # #     "_cls" : "eudat.models.mongo.wf_do"
        mongohd = self.get_service_instance(
            service_name='mongo', database='wfcat')
        # test:
        #mongohd.Testing(onefield='justatest1').save()
        #log.info("just a test - mongo insert")
        #return "Hello world!"
        
        # real:
        myargs = self.get_input()
        print(myargs)
        documentResult1 = []
        
        mycollection = mongohd.wf_do
        
        myStartDate = dateutil.parser.parse(myargs.get("start"))
        myEndDate = dateutil.parser.parse(myargs.get("end"))
        myLat = float(myargs.get("minlat"))
        myLon = float(myargs.get("minlon"))
        myLatX = float(myargs.get("maxlat"))
        myLonX = float(myargs.get("maxlon"))

        myfirstvalue = mycollection.objects.raw({"dc_coverage_x": { "$gte" : myLat }, "dc_coverage_y": { "$gte" : myLon }, "dc_coverage_x": { "$lte" : myLatX }, "dc_coverage_y": { "$lte" : myLonX },"dc_coverage_t_min": { "$gte" : myStartDate },"dc_coverage_t_max": { "$lte" : myEndDate }})
        # #myfirstvalue = mongohd.wf_do.objects.all()
        

        for document in myfirstvalue:
             myLine = {
                "fileId" : document.fileId,
                "dc_identifier" : document.dc_identifier, 
                "dc_coverage_x" : document.dc_coverage_x, 
                "dc_coverage_y" : document.dc_coverage_y,
                "dc_coverage_z" : document.dc_coverage_z,
                "dc_title" : document.dc_title,
                "dc_subject" : document.dc_subject, 
                "dc_creator" : document.dc_creator, 
                "dc_contributor" : document.dc_contributor,
                "dc_publisher" : document.dc_publisher,
                "dc_type" : document.dc_type,
                "dc_format" : document.dc_format, 
                "dc_date" : document.dc_date, 
                "dc_coverage_t_min" : document.dc_coverage_t_min,
                "dc_coverage_t_max" : document.dc_coverage_t_max,
                "dcterms_available" : document.dcterms_available, 
                "dcterms_dateAccepted" : document.dcterms_dateAccepted, 
                "dc_rights" : document.dc_rights,
                "dcterms_isPartOf" : document.dcterms_isPartOf,
                "irods_path" : document.irods_path
             }
             documentResult1.append(myLine)

        print ("result")
        print (documentResult1)
    
        return [documentResult1] # ["total objects result:"] 
    
        # log.info("just a test")
        # mongohd = self.global_get_service('mongo', dbname='auth')
        # myargs = self.get_input()
        # print(myargs)

        # if myargs.get('debug', 'no') == 'yes':
        #     return {'Hello': 'debugger'}

        # documentResult1 = {}
        # # --> important into mongo collections we must have:
        # #     "_cls" : "commons.models.mongo.wf_do"

        # # mongohd.wf_do(fileId='justatest').save() # write-test

        # mycollection = mongohd.daily_streams
        # myreference = mongohd.wf_do
        # # log.pp(mongohd)
        # myStartDate = dateutil.parser.parse(myargs.get("start"))
        # myEndDate = dateutil.parser.parse(myargs.get("end"))
        # myLat = float(myargs.get("minlat"))
        # myLon = float(myargs.get("minlon"))
        # myLatX = float(myargs.get("maxlat"))
        # myLonX = float(myargs.get("maxlon"))

        # #myfirstvalue = mycollection.objects.raw({"dc_coverage_x": { "$gte" : myLat }, "dc_coverage_y": { "$gte" : myLon }, "dc_coverage_x": { "$lte" : myLatX }, "dc_coverage_y": { "$lte" : myLonX },"dc_coverage_t_min": { "$gte" : myStartDate },"dc_coverage_t_max": { "$lte" : myEndDate }})
        # #myfirstvalue = mongohd.wf_do.objects.all()
        # #myfirstvalue = mycollection.objects.raw({"ts": { "$gte" : myStartDate },"te": { "$lte" : myEndDate }})
        # myfirstvalue = myreference.objects.raw({"dc_coverage_x": { "$gte" : myLat }, "dc_coverage_y": { "$gte" : myLon }, "dc_coverage_x": { "$lte" : myLatX }, "dc_coverage_y": { "$lte" : myLonX },"dc_coverage_t_min": { "$gte" : myStartDate },"dc_coverage_t_max": { "$lte" : myEndDate }})

        # for document in myfirstvalue:
        #     myLine = mycollection.objects.raw({"fileId": document.fileId})

        #     #[document.fileId]
        #     print (list(myLine.values()))
        #     print (type (myLine))
        #     #documentResult1.append(list(myLine.values()))
        #     documentResult1[document.fileId] = list(myLine.values())

        # print (type (documentResult1) )
        # #print (documentResult1)
        # return  ["total objects result:"+str(len(documentResult1))]  # , json.dumps(documentResult1)  , json.loads(documentResult1) RESPONSE2




