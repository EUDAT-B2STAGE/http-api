# -*- coding: utf-8 -*-

"""
Example for mongodb

class MongoExample(EndpointResource):

    # @decorate.catch_error()
    def get(self):

        #####################
        service = 'mongo'
        mongohd = self.get_service_instance(service_name=service)
        from restapi.services.detect import detector
        variables = detector.output_service_variables(service)
        db = variables.get('database')

        # test if it works
        # BAD: using private internal meta
        # (src: http://bit.ly/2njr3LN)
        mongohd.Testing._mongometa.connection_alias = db
        mongohd.Testing(onefield='justatest1').save()
        for element in mongohd.Testing.objects.all():
            log.pp(element)


"""

pass
