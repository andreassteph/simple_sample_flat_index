"""
This module is based on flask_flatpages and creates a website structure based on a file structure. 
By default the .md extension creates a html website 
"""
import logging
import sys
from flask import Flask, Blueprint,render_template, send_from_directory,jsonify, url_for

from flatpages_index import FlatPagesIndex
import flatpages_index
from flask_frozen import Freezer
from config import Config
import os

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

flatpages = FlatPagesIndex(app)
flatpages_index.Links.endpoint="stuff.post"
flatpages_index.Links.url=(lambda s,x: url_for(s.endpoint, name=x))
#flatpages_index.Links.image_url=(lambda s,x: url_for('stuff.page', name=x))
flatpages_index.Links.file_url=(lambda s,x: url_for('stuff.page', name=x))
flatpages_index.Links.thumb_url=(lambda s,x: url_for('stuff.thumb', size=128,name=x))

flatpages.get('index')

app.logger.info('Initialize SimpleSample App')
app.logger.info('flatpages loaded %d pages' % len(flatpages._pages))
app.logger.info("Data directory is: %s" % flatpages.root)
app.logger.info("Url prefix;: %s" % cfg.url_prefix)
app.logger.info("Extensions: %s" % FLATPAGES_EXTENSION)

freezer = Freezer(app)

page_blueprint  = Blueprint('stuff', __name__)

@page_blueprint.route('/thumb<int:size>/<path:name>/')
def thumb(size=64,name=''):
    pass

@page_blueprint.route('/<path:name>/')
@page_blueprint.route('/')
def page(name='index'):
    page = flatpages.get(name)
    
    if not page is None:
        page["has_img"]=True
        page.links.endpoint='stuff.page'
        return render_template(page["template"], post=page,
                               pth=page["dirpath"])

    if os.path.exists(os.path.join(FLATPAGES_ROOT,name)):
        return send_from_directory(FLATPAGES_ROOT,name)
    else:
        return send_from_directory('static',name)




@page_blueprint.route('/<path:name>.json',strict_slashes=False)
def pagejson(name='index'):
    page = flatpages.get(name)
    if not page is None:
        page["has_img"]=False
        page.links.endpoint='stuff.pagejson'
#        page.links.file_url=lambda n: url_for('intern.post', name=n)
        return jsonify(page=dict(page))
    
    if os.path.exists(u'{}/{}'.format(FLATPAGES_ROOT,path)):
        return send_from_directory(FLATPAGES_ROOT,path)
    else:
        return send_from_directory('static',path)


    
app.register_blueprint(page_blueprint, url_prefix=cfg.url_prefix,static_folder='static')
