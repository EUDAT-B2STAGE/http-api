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
import uuid
import subprocess

#from b2stage.apis.commons.endpoint import EudatEndpoint

from irods.query import SpecificQuery
from irods.models import Collection, DataObject, User, UserGroup, UserAuth

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
                #return icom.read_in_streaming(myfirstvalue[0].irods_path)
                
                for document in myfirstvalue:
                    pass
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



        
#################
# REST CLASS AirodsList
#
class AirodsList(EndpointResource):
    
    def get(self):
        
        icom = self.get_service_instance(service_name='irods') #, user='rods', password='sdor' 
            
        ####################################################

        #print ('start - QUERY!')
        session = icom.prc
        sql = "select zone_name, zone_conn_string, r_comment   from r_zone_main where r_comment LIKE 'stag%'" #where zone_type_name = 'remote'"
        #alias = 'list_zone_max'
        queryResponse = {}
        #columns = [DataObject.zone_id, DataObject.zone_name] # optional, if we want to get results by key 
        query = SpecificQuery(session, sql)
        # register specific query in iCAT
        _ = query.register()

        for result in query:
            
            #print('Endpoint: '+result[0])
            queryResponse['Endpoint']=result[0]
            if result[1]:
                #print('URL: '+result[1])
                queryResponse['URL'] =result[1]
            #else:
                #print('URL: ')
            if result[2]:
                #print('description: '+result[2])
                queryResponse['description'] =result[2]
            #else:
                #print('description: ')
            

            #print('{} {}'.format(result[zone_id], result[zone_name]))


        _ = query.remove()
            
            
           ####################################################
        return [queryResponse]
    

    
    
    

        
#################
# REST CLASS AirodsStage
# 
class AirodsStage( EndpointResource):
    
    def get(self):
        service = 'mongo'
        mongohd = self.get_service_instance(service_name=service)
        
        variables = detector.output_service_variables(service)
        db = variables.get('database')
        
        mongohd.wf_do._mongometa.connection_alias = db
        
        # MONGO
        myargs = self.get_input()
        print(myargs)
        documentResult1 = {}
        
        mycollection = mongohd.wf_do
        
        myStartDate = dateutil.parser.parse(myargs.get("start"))
        myEndDate = dateutil.parser.parse(myargs.get("end"))
        myLat = float(myargs.get("minlat"))
        myLon = float(myargs.get("minlon"))
        myLatX = float(myargs.get("maxlat"))
        myLonX = float(myargs.get("maxlon"))

        myfirstvalue = mycollection.objects.raw({"dc_coverage_x": { "$gte" : myLat }, "dc_coverage_y": { "$gte" : myLon }, "dc_coverage_x": { "$lte" : myLatX }, "dc_coverage_y": { "$lte" : myLonX },"dc_coverage_t_min": { "$gte" : myStartDate },"dc_coverage_t_max": { "$lte" : myEndDate }})

        # IRODS 
        icom = self.get_service_instance(service_name='irods')
        
        ephemeralDir=str(uuid.uuid4())
        stagePath='/'+myargs.get("endpoint")+'/home/rods#INGV/areastage/'
        dest_path=stagePath+ephemeralDir
        
        ipath = icom.create_directory(dest_path)
        
        
        if ipath is None:
            raise IrodsException("Failed to create %s" % dest_path)
        else:
            log.info("Created irods collection: %s", dest_path)
        
        # STAGE
        if ipath:
            #myLine = ['remote_collection_ID: '+ dest_path ]
            #documentResult1.append(myLine)
            myLine = self.queryIcat(icom, myargs.get("endpoint"), dest_path)
            
            documentResult1['remote_info']=myLine 
            
            i = 0
            for document in myfirstvalue:
                
                stageOk=self.icopy(icom, document.irods_path, dest_path+'/'+document.fileId)
                                
                if stageOk :
                    
                    documentResult1['file_ID_'+str(i)]=str(document.fileId)
                    i = i+1
                else:
                    
                    documentResult1['DO-NOT-OK']='stage DO '+document.fileId+': NOT OK'
                
            documentResult1['total DO staged']= str(i)   
        
        else:
            
            documentResult1['DIR-NOT-OK']='stage dir:'+dest_path+' NOT OK'
        
        
        return [documentResult1]
    
    # COPY on Remote endpoint via irule
    def icopy(self, icom, irods_path, dest_path):
        
        """ EUDAT RULE for Replica (exploited for copy) """
        
        outvar = 'response'
        inputs = {
            '*irods_path': '"%s"' % irods_path,
            '*stage_path': '"%s"' % dest_path
            }
        body = """
            *res = EUDATReplication(*irods_path, *stage_path, "false", "false", *%s);
            if (*res) {
                writeLine("stdout", "Object  replicated to stage area !");

            }
            else {
                writeLine("stdout", "Replication failed: *%s");
            }
        """ % (outvar, outvar)
        

        rule_output = self.rule(icom, 'do_stage', body, inputs, output=True)
        
        return [rule_output]
    
    
    # Rule
    def rule(self, icom, name, body, inputs, output=False):
        
        import textwrap
        from irods.rule import Rule

        user_current = icom.prc.username
        zone_current = icom.prc.zone
        
        rule_body = textwrap.dedent('''\
            %s {{
                %s
        }}''' % (name, body))

        outname = None
        if output:
            outname = 'ruleExecOut'
            
        myrule = Rule(icom.prc, body=rule_body, params=inputs, output=outname)
        try:
            raw_out = myrule.execute()
        except BaseException as e:
            msg = 'Irule failed: %s' % e.__class__.__name__
            log.error(msg)
            log.warning(e)
            # raise IrodsException(msg)
            raise e
        else:
            log.debug("Rule %s executed: %s", name, raw_out)

            # retrieve out buffer
            if output and len(raw_out.MsParam_PI) > 0:
                out_array = raw_out.MsParam_PI[0].inOutStruct
                # print("out array", out_array)

                import re
                file_coding = 'utf-8'

                buf = out_array.stdoutBuf.buf
                if buf is not None:
                    # it's binary data (BinBytesBuf) so must be decoded
                    buf = buf.decode(file_coding)
                    buf = re.sub(r'\s+', '', buf)
                    buf = re.sub(r'\\x00', '', buf)
                    buf = buf.rstrip('\x00')
                    log.debug("Out buff: %s", buf)

                err_buf = out_array.stderrBuf.buf
                if err_buf is not None:
                    err_buf = err_buf.decode(file_coding)
                    err_buf = re.sub(r'\s+', '', err_buf)
                    log.debug("Err buff: %s", err_buf)

                return buf

            return raw_out
        
        
    # Query
    def queryIcat(self, icom, zone_name, dest_path):
        
        session = icom.prc
        sql = "select zone_name, zone_conn_string, r_comment   from r_zone_main where zone_name = '"+zone_name+"'" 
        print (sql)
        
        #alias = 'list_zone_max'
        queryResponse = {}
        #columns = [DataObject.zone_id, DataObject.zone_name] # optional, if we want to get results by key 
        query = SpecificQuery(session, sql)
        # register specific query in iCAT
        _ = query.register()
        
        queryResponse['remote_collection_ID']=dest_path
        for result in query:
            
            #print('Endpoint: '+result[0])
            queryResponse['Endpoint']=result[0]
            if result[1]:
                #print('URL: '+result[1])
                queryResponse['URL'] =result[1]
            #else:
                #print('URL: ')
            if result[2]:
                #print('description: '+result[2])
                queryResponse['description'] =result[2]
            #else:
                #print('description: ')
            

            #print('{} {}'.format(result[zone_id], result[zone_name]))


        _ = query.remove()
        
        return queryResponse
        

#################
# REST CLASS AirodsFree
#        
class AirodsFree( EndpointResource):
    
    def get(self):
        myargs = self.get_input()
        print(myargs)
        documentResult = []
        
        collection_to_del = myargs.get("remote_coll_id")
        print ('@todo: delete remote collection!')
        print ('@todo: empty trash remote !')
        """
        we need two rules:
        1)
        irm -r collection_to_del
        
        2)
        irmtrash -rV --orphan /BINGV/trash/home/rods#INGV/trash
        
        """
        
        
        return ['ciao']    