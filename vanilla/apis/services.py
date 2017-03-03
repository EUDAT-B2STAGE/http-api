# -*- coding: utf-8 -*-

"""
Custom method to initialize mixed services which rely on each other
"""

from rapydo.services import get_instance_from_services
from rapydo.utils.logs import get_logger

log = get_logger(__name__)


def init(internal_services, enable_security):

    if enable_security:
        icom = get_instance_from_services(internal_services, 'irods')
        graph = get_instance_from_services(internal_services, 'neo4j')

        users = graph.User.nodes.all()

        # Only available one user, the default one?
        if len(users) == 1:
            userobj = users.pop()
            associated = userobj.associated.all()

            # Link default user to default irods users
            if len(associated) < 2:
                irodsusers = graph.IrodsUser.get_or_create(
                    {'username': icom.get_current_user(),
                        'default_user': False},
                    {'username': icom.get_default_user(),
                        'default_user': True},
                )
                for irodsuser in irodsusers:
                    if irodsuser not in associated:
                        userobj.associated.connect(irodsuser)

            log.info("Mixed irods and graph users")
    else:
        pass
