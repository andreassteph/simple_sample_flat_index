"""
This module is based on flask_flatpages and creates a website structure based on a file structure. 
By default the .md extension creates a html website 
"""
import logging
import sys
from flask import Flask, Blueprint,render_template, send_from_directory,jsonify, url_for
#from flask_flatpages import FlatPages, pygments_style_defs
from flatpages_index import FlatPagesIndex
from flask_frozen import Freezer
from config import Config
import os
import re
from flatpages_index.utils import  path_depth, page_to_link, page_to_link, file_to_link
from functools import partial
#from .flatpages import FileLists

# This is the directory, required for absolute file paths
package_directory = os.path.dirname(os.path.abspath(__file__))
# Loading the config file 
cfg = Config((os.path.join(package_directory, '../config.cfg')))

# Loading constants from config file 
FLATPAGES_AUTO_RELOAD = cfg.get("FLATPAGES_AUTO_RELOAD",True) # Default can be overwritten by config cfg
FLATPAGES_EXTENSION = cfg.get("FLATPAGES_EXTENSION",".md") # Default can be overwritten by config cfg
FLATPAGES_ROOT = os.path.abspath(cfg.pages_root)


# Initialize application
app = Flask(__name__)
app.config.from_object(__name__)

app.logger.setLevel(logging.DEBUG)
# Initialize FlatPages Index
#FlatPagesIndex.FLATPAGES_ROOT=FLATPAGES_ROOT
flatpages = FlatPagesIndex(app)
flatpages.get('index')

app.logger.info('Initialize SimpleSample App')
app.logger.info('flatpages loaded %d pages' % len(flatpages._pages))
app.logger.info("Data directory is: %s" % flatpages.root)
app.logger.info("Url prefix;: %s" % cfg.url_prefix)
app.logger.info("Extensions: %s" % FLATPAGES_EXTENSION)






freezer = Freezer(app)


page_blueprint  = Blueprint('intern', __name__)

@page_blueprint.route('/<path:name>/')
@page_blueprint.route('/')
def post(name='index'):
    page = flatpages.get(name)
    
    if not page is None:
        page.meta["has_img"]=page.meta.get('has_img',True)
        page=page.load_linklists(partial(url_for,'intern.post'))
        return render_template(page.meta["template"], post=page,
                               pth=page.meta["dirpath"])

    if os.path.exists(os.path.join(FLATPAGES_ROOT,name)):
        return send_from_directory(FLATPAGES_ROOT,name)
    else:
        return send_from_directory('static',name)




@page_blueprint.route('/<path:name>.json',strict_slashes=False)
def postjson(name='index'):
    page = flatpages.get(name)
    if not page is None:
        page.meta["has_img"]=page.meta.get('has_img',True)

        page=page.load_linklists(partial(url_for,'intern.post'))
        p=page.meta

        p["html"]=page.html
        return jsonify(page=p)
    
    if os.path.exists(u'{}/{}'.format(FLATPAGES_ROOT,path)):
        return send_from_directory(FLATPAGES_ROOT,path)
    else:
        return send_from_directory('static',path)


    
app.register_blueprint(page_blueprint, url_prefix=cfg.url_prefix,static_folder='static')
app.add_url_rule('%s/<path:name>' % cfg.url_prefix,'page', post)
