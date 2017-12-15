# -*- coding: utf-8 -*-

"""
Endpoint example for the RAPyDo framework
"""

#################
# IMPORTS
from restapi.rest.definition import EndpointResource
from restapi.services.detect import detector
from utilities.logs import get_logger
import dateutil.parser

from b2stage.apis.commons.endpoint import EudatEndpoint

#################
# INIT VARIABLES
log = get_logger(__name__)
service_name = "sqlalchemy"
# NOTE: if you need to operate based on service availability
# SERVICE_AVAILABLE = detector.check_availability(service_name)


#################
# REST CLASS
class Airods(EndpointResource):

    def get(self):
        # # --> important into mongo collections we must have:
        # #     "_cls" : "b2stage.models.mongo.wf_do"
        
        service = 'mongo'
        mongohd = self.get_service_instance(service_name=service)
        
        variables = detector.output_service_variables(service)
        db = variables.get('database')
        # test if it works
        # BAD: using private internal meta
        # (src: http://bit.ly/2njr3LN)
        mongohd.wf_do._mongometa.connection_alias = db
        
        # just a test:
        # mongohd.Testing(onefield='justatest1').save()
        # for element in mongohd.Testing.objects.all():
        #    log.pp(element)
        # return "Completed"
        
        
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
        #myfirstvalue = mycollection.objects.raw({"dc_coverage_x": { "$gte" : myLat }, "dc_coverage_y": { "$gte" : myLon }, "dc_coverage_x": { "$lte" : myLatX }, "dc_coverage_y": { "$lte" : myLonX }})
            #,"dc_coverage_t_min": { "$gte" : myStartDate },"dc_coverage_t_max": { "$lte" : myEndDate }})

        #myfirstvalue = mongohd.wf_do.objects.all()
        for document in myfirstvalue:
                myLine = [document.fileId,document.dc_identifier,document.irods_path, document.dc_coverage_x, document.dc_coverage_y ]
                documentResult1.append(myLine)

        
        # Download :: to check w/ irods
        if myargs.get('download') == 'true':
            
            icom = self.get_service_instance(service_name='irods') #, user='rods', password='sdor' 
            
            myobj = myfirstvalue[0].irods_path
            #myobj = icom.list() #myfirstvalue[0].irods_path
            #myresp = icom.get_permissions(myfirstvalue[0].irods_path)
            print (myobj)
            
            #for meta in my-meta:
             #   print(meta)
            
            print ("eccolo")
            print (myfirstvalue[0].irods_path) 
                
            try:
                # for time being ... @TODO: allow multi files download
                return icom.read_in_streaming(myfirstvalue[0].irods_path)
                #for document in myfirstvalue:
                #    print(document.irods_path)
                #    icom.read_in_streaming(document.irods_path)
                    
                # test only
                #return("download ok")
            
            except BaseException as e:
                print(e, type(e))
                return self.force_response(e)
                
            
        # Pid list :: OK
        else:
            
            return  ["total files to download: "+str(len(documentResult1)) +" format:< fileId - PID - Lat - Lon >",documentResult1]   # ,documentResult1


#################
# REST CLASS
class AirodsMeta(EndpointResource):

    def get(self):

       # # --> important into mongo collections we must have:
        # #     "_cls" : "b2stage.models.mongo.wf_do"
        
        service = 'mongo'
        mongohd = self.get_service_instance(service_name=service)
        
        variables = detector.output_service_variables(service)
        db = variables.get('database')
        # test if it works
        # BAD: using private internal meta
        # (src: http://bit.ly/2njr3LN)
        mongohd.wf_do._mongometa.connection_alias = db
        
        # just a test:
        # mongohd.Testing(onefield='justatest1').save()
        # for element in mongohd.Testing.objects.all():
        #    log.pp(element)
        # return "Completed"
        
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

        #myfirstvalue = mycollection.objects.raw({"dc_coverage_x": { "$gte" : myLat }, "dc_coverage_y": { "$gte" : myLon }, "dc_coverage_x": { "$lte" : myLatX }, "dc_coverage_y": { "$lte" : myLonX },"dc_coverage_t_min": { "$gte" : myStartDate },"dc_coverage_t_max": { "$lte" : myEndDate }})
        myfirstvalue = mongohd.wf_do.objects.all()
        

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

        """
        # Write server logs, on different levels:
        # very_verbose, verbose, debug, info, warning, error, critical, exit
        log.info("Received a test HTTP request")

        # Parse input parameters:
        # NOTE: they can be caught only if indicated in swagger files
        self.get_input()
        # pretty print arguments obtained from the _args private attribute
        log.pp(self._args, prefix_line='Parsed args')

        # Activate a service handle
        service_handle = self.get_service_instance(service_name)
        log.debug("Connected to %s:\n%s", service_name, service_handle)

        # Handle errors
        if service_handle is None:
            log.error('Service %s unavailable', service_name)
            return self.send_errors(
                message='Server internal error. Please contact adminers.',
                # code=hcodes.HTTP_BAD_NOTFOUND
            )

        # Output any python structure (int, string, list, dictionary, etc.)
        response = 'Hello world!'
        return self.force_response(response)
        """