# -*- coding: utf-8 -*-

"""
Useless code which has some beauty and/or techincal difficulties.
"""

from felask import get_logger
logger = get_logger(__name__)

###############################################
import os
import csv
from sqlalchemy import inspect
from felask.basemodel import User, MyModel


def init_insert(db, userconfig):
    """
    This function has been prepared originally to load data from csv
    and inject it at server startup inside the main data model.

    I was assumning the server to work directly with a database,
    sqllite or postgres.

    Things have changed, and angular works with APIs, which are elastic
    and modular and granular. So data is no longer needed to be created here.

    This has become deprecated and WILL BE REMOVED SOME TIME SOON
    """

    # Add at least the first user
    user = User(**userconfig['BASIC_USER'])
    db.session.add(user)
    db.session.commit()

    # Try to populate with data if there is some
    modelname = 'mymodel'
    csvfile = os.path.join(userconfig['MYCONFIG_PATH'], modelname + '.csv')
    if not os.path.exists(csvfile):
        return

    data = []
    with open(csvfile, 'r') as csvfile:
        creader = csv.reader(csvfile, delimiter=';')
        for row in creader:
            data.append(row)

    mapper = inspect(MyModel)
    for pieces in data:
        i = 0
        content = {}
        for column in mapper.attrs:
            try:
                value = pieces[i]
                if not (value == '-' or value.strip() == ''):
                    content[column.key] = pieces[i]
            except:
                pass
            i += 1
        # Add one row at the time
        obj = MyModel(**content)
        db.session.add(obj)
    db.session.commit()


###############################################


from felask import m, pypages as custom_views
app = None

# Dynamically load all custom blueprints from pypages module
meta = m()
for module_name in meta.get_submodules_from_package(custom_views):
    module_path = custom_views.__name__ + '.' + module_name
    module = meta.get_module_from_string(module_path)
    try:
        app.register_blueprint(module.bp)
    except Exception:
        logger.warning(
            "OOPS: Could not find 'bp' inside module '%s'" % module_name)
