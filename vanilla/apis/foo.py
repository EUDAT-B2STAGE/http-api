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
        from ..services.accounting.graphbased import GraphUser

        j = request.get_json(force=True)

        # user = self.graph.User()
        if 'user' not in j or 'pwd' not in j:
            return self.response(errors={
                'Missing credentials': 'you need to specify user and pwd'})

        auth_user = j['user']
        auth_pwd = j['pwd']


        self.graph = GraphFarm().get_graph_instance()

###################################
# Should go in a function
        user = GraphUser.get_graph_user(email=auth_user)
        token = None

        # Check password and create token if fine
        if user is not None:
            # Validate password
            if GraphUser.validate_login(
               user.hashed_password, auth_pwd):

                logger.info("Validated credentials")

                # Create a new token and save it
                token = user.get_auth_token()
# USE JWT and DO NOT SAVE INSIDE THE DATABASE
                GraphUser.set_graph_user_token(auth_user, token)
###################################

        # In case something is wrong
        if user is None or token is None:
            return self.response(errors={
                'Invalid credentials': 'wrong username or password'},
                code=hcodes.HTTP_BAD_UNAUTHORIZED)

        # Save the user for flask login sessions
        login_user(user)

        return self.response({'Authentication-token': token})
