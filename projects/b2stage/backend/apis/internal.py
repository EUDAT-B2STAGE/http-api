# # -*- coding: utf-8 -*-

# """
# Internal endpoints.
# Code to implement the /api/internal endpoint

# FIXME: TO BE DEPRECATED
# """

# from restapi import decorators
# from restapi.connectors.irods.client import IrodsException
# from restapi.utilities.htmlcodes import hcodes
# # from restapi.utilities.logs import log

# from b2stage.apis.commons.endpoint import EudatEndpoint
# from b2stage.apis.commons import CURRENT_MAIN_ENDPOINT


# ###############################
# # Classes


# class MetadataEndpoint(EudatEndpoint):

#     labels = ['helpers', 'eudat']
#     PATCH = {
#         '/metadata/<path:location>': {
#             'summary': 'Add metadata to object',
#             'custom': {},
#             'parameters': [
#                 {
#                     'name': 'metadata',
#                     'in': 'body',
#                     'required': True,
#                     'schema': {'type': 'array', 'items': {'type': 'string'}},
#                 }
#             ],
#             'responses': {'200': {'description': 'Metadata added'}},
#         }
#     }

#     @decorators.catch_errors(exception=IrodsException)
#     @decorators.auth.required(roles=['normal_user'])
#     def patch(self, location=None):
#         """
#         Add metadata to an object.
#         """

#         if location is None:
#             return self.send_errors(
#                 'Location: missing filepath inside URI', code=hcodes.HTTP_BAD_REQUEST
#             )
#         location = self.fix_location(location)

#         ###################
#         # BASIC INIT
#         r = self.init_endpoint()
#         if r.errors is not None:
#             return self.send_errors(errors=r.errors)
#         icom = r.icommands

#         path, resource, filename, force = self.get_file_parameters(icom, path=location)

#         dct = {}
#         pid = self._args.get('PID')
#         if pid:
#             dct['PID'] = pid
#         else:
#             return self.send_errors('PID: missing parameter in JSON input')

#         checksum = self._args.get('EUDAT/CHECKSUM')
#         if checksum:
#             dct['EUDAT/CHECKSUM'] = checksum

#         out = None
#         if dct:
#             icom.set_metadata(location, **dct)
#             out, _ = icom.get_metadata(location)

#         return {
#             'metadata': out,
#             'location': filename,
#             'link': self.httpapi_location(location, api_path=CURRENT_MAIN_ENDPOINT),
#         }
