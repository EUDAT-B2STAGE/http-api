# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from ... import get_logger, htmlcodes as hcodes
from ..base import ExtendedApiResource
from .. import decorators as decorate
from ..services.neo4j.graph import GraphFarm

# Security
# from confs import config
# from flask.ext.security import roles_required, auth_token_required

logger = get_logger(__name__)


#####################################
class JustATest(ExtendedApiResource):

    @decorate.apimethod
    def get(self):
        logger.warning("a call")
        return self.response('Hello world!')


#####################################
class GraphEndPoint(ExtendedApiResource, GraphFarm):

    @decorate.apimethod
    def get(self):
        graph = self.get_graph_instance()
        print(graph)
        logger.warning("a call")
        return self.response('Hello world!')


class MyGraphLogin(ExtendedApiResource, GraphFarm):

    def get(self):
        return "Hello World! I need user and pwd via POST :-)"

    # @decorate.apimethod
    def post(self):

        from flask.ext.restful import request
        from flask.ext.login import login_user
        from ..services.accounting.graphbased import UserModel

        j = request.get_json(force=True)
        if 'username' not in j or 'password' not in j:
            return self.response(
                errors={'Missing credentials':
                        'you need to specify username and password'})

        user, token = \
            UserModel.emit_token_from_credentials(j['username'], j['password'])

        # In case something is wrong
        if user is None or token is None:
            return self.response(errors={
                'Invalid credentials': 'wrong username or password'},
                code=hcodes.HTTP_BAD_UNAUTHORIZED)

        # Save the user for flask login sessions
        login_user(user)

        return self.response({'Authentication-token': token})
