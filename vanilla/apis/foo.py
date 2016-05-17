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

        self.graph = GraphFarm().get_graph_instance()
        # print(self.graph.User)
        # user = self.graph.User()
        # user.name = 'Paolo2'
        # print(user)
        # user.email = 'paulie@nomail.org'
        # user.surname = 'PIIPPPOOO'
        # user.save()

        from flask.ext.restful import request
        from flask.ext.login import login_user

        j = request.get_json(force=True)

        # user = self.graph.User()
        if 'user' not in j or 'pwd' not in j:
            return self.response(errors={
                'Missing credentials': 'you need to specify user and pwd'})

        auth_user = j['user']
        auth_pwd = j['pwd']

        from ..services.accounting.graphbased import GraphUser
        user = GraphUser.get_graph_user(email=auth_user)
        if user is None:
            return self.response(errors={
                'Invalid credentials': 'wrong username or password'},
                code=hcodes.HTTP_BAD_UNAUTHORIZED)
#     #validate user and password, es using:
        GraphUser.validate_login('PASSWORD_HASH_TO_FIX', auth_pwd)
        token = user.get_auth_token()
        GraphUser.set_graph_user_token(auth_user, token)

        login_user(user)

        return self.response({'Authentication-token': token})
