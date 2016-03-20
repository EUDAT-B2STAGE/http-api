# -*- coding: utf-8 -*-

""" Main routes """

from __future__ import absolute_import
import os
from pathlib import Path
from flask import Blueprint, render_template, request, jsonify, g
from flask.ext.login import logout_user, current_user
from .basemodel import user_config
from .security import login_point, register_api
from . import htmlcodes as hcodes
from config import get_logger, FRAMEWORKS

logger = get_logger(__name__)
CURRENT_FRAMEWORK = None
BLUEPRINT_KEY = 'blueprint'
CURRENT_BLUEPRINT = BLUEPRINT_KEY + '_example'

#######################################
# Blueprint for base pages, if any
cms = Blueprint('pages', __name__)

#######################################
# Framework user configuration
fconfig = user_config['frameworks']
# Static directories
staticdir = fconfig['staticdir'] + '/'
bowerdir = staticdir + fconfig['bowerdir'] + '/'
# CSS files
css = []
for scss in fconfig['css']:
    css.append(bowerdir + scss)
for scss in fconfig['customcss']:
    css.append(staticdir + scss)
# JS: Angular framework and app files
js = []
for sjs in fconfig['js']:
    js.append(bowerdir + sjs)
    if CURRENT_FRAMEWORK is None:
        for frame in FRAMEWORKS:
            if frame in sjs:
                CURRENT_FRAMEWORK = frame
                logger.info("Found framework '%s'" % CURRENT_FRAMEWORK)
for sjs in fconfig['customjs']:
    js.append(staticdir + sjs)
# Fonts
fonts = []
for sfont in fconfig['fonts']:
    # This should be an external url
    if 'http' not in sfont:
        sfont = staticdir + sfont
    fonts.append(sfont)
# Images
imgs = []
for simg in fconfig['imgs']:
    js.append(staticdir + simg)
#logger.debug("JSON img load: %s" % imgs)
# TO FIX!
if 'logos' not in user_config['content']:
    user_config['content']['logos'] = [{
        "src": "static/img/default.png", "width": '90'
    }]

#######################################
# ## JS BLUEPRINTS

# Load only a specified angular blueprint
if 'blueprints' not in user_config or \
  BLUEPRINT_KEY not in user_config['blueprints']:
    logger.critical("No blueprint file/key found!")
else:
    CURRENT_BLUEPRINT = user_config['blueprints'][BLUEPRINT_KEY]

logger.info("Adding JS blueprint '%s'" % CURRENT_BLUEPRINT)
prefix = __package__
# JS BLUEPRINT config
jfiles = [Path(prefix + '/js/blueprint.js')]
# JS files in the root directory
app_path = os.path.join(prefix, staticdir, 'app')
jfiles.extend(Path(app_path).glob('*.js'))
# JS common files
common_path = os.path.join(app_path, 'commons')
jfiles.extend(Path(common_path).glob('*.js'))
# JS files only inside the blueprint subpath
blueprint_path = os.path.join(app_path, CURRENT_BLUEPRINT)
jfiles.extend(Path(blueprint_path).glob('**/*.js'))

# Use all files found
for pathfile in jfiles:
    strfile = str(pathfile)
    jfile = strfile[len(prefix)+1:]
    if jfile not in js:
        js.append(jfile)

#######################################
user_config['content']['stylesheets'] = css
user_config['content']['jsfiles'] = js
user_config['content']['images'] = imgs
user_config['content']['htmlfonts'] = fonts


#######################################
def templating(page, framework=CURRENT_FRAMEWORK, **whatever):
    template_path = 'frameworks' + '/' + framework
    tmp = whatever.copy()
    tmp.update(user_config['content'])
    templ = template_path + '/' + page
    return render_template(templ, **tmp)


def jstemplate(title='App', mydomain='/'):
    """ If you decide a different domain, use slash as end path,
        e.g. /app/ """
    return templating('main.html', mydomain=mydomain, jstitle=title)


# #################################
# # BASIC INTERFACE ROUTES
@cms.before_request
def before_request():
    """ Save the current user as the global user for each request """
    g.user = current_user


@cms.route('/auth', methods=['POST'])
def auth():
    """
    IMPORTANT: This route is a proxy for JS code to APIs login.
    With this we can 'intercept' the request and save extra info on server
    side, such as: ip, user, token
    """
    # Verify POST data
    if not ('username' in request.json and 'password' in request.json):
        return "No valid (json) data credentials", hcodes.HTTP_BAD_UNAUTHORIZED
    # Request login (with or without API)
    resp, code = login_point(
            request.json['username'], request.json['password'])
    if resp is None:
        resp = {}
    # Forward response
    return jsonify(**resp), code


@cms.route('/doregistration', methods=['POST'])
def register():

    response, code = register_api(request.json)
    # # Forward response
    # return jsonify(**resp)
    print("RESP is", response, code)
    return "OK"


################################################
# Create a configuration file for angular from python variables
@cms.route('/js/blueprint.js')
def jsblueprint():
    variables = {
        'name': CURRENT_BLUEPRINT,
        'time': user_config['options']['load_timeout'],
        'api_url': request.url_root
    }
    return render_template("blueprint.js", **variables)


######################################################
# MAIN ROUTE: give angular the power

@cms.route('/', methods=["GET"])
@cms.route('/<path:mypath>', methods=["GET"])
def home(mypath=None):
    """
    The main and only real HTML route in this server.
    The only real purpose is to serve angular pages and routes.
    """
    logger.debug("Using angular route. PATH is '%s'" % mypath)
    if mypath is None:
        # return templating('welcome.html')
        pass
    elif mypath == 'loggedout':
        logout_user()
    return jstemplate()
