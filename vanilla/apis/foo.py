# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from restapi import get_logger
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

    @decorate.apimethod
    def post(self):
        from flask.ext.restful import request
        from flask.ext.login import login_user

        v = request.get_json(force=True)
        self.graph = GraphFarm().get_graph_instance()

        auth_user = v['user']
        auth_pwd = v['pwd']

        user = self.graph.User.nodes.filter(email=auth_user)
        user_obj = None
        for u in user.all():
            #validate user and password, es using: User.validate_login(user.password, auth_pwd):
            user_obj = User(u._id)
            login_user(user_obj)
            break
        if user_obj is None:
            return self.response("ERROR!")

        return self.response(user_obj.get_auth_token())
