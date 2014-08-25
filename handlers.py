import os 
import webapp2
import re
import cgi
from security import *
import jinja2
import logging
import urllib
from subprocess import call



jinja_env = jinja2.Environment(
        autoescape=True, loader = jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), 'templates')))

def is_video(path):
    res = re.search("mp4$",path)
    return res > 0 



#General 
def render_str(template, **params):
    """Function that render a jinja template with string substitution"""
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    """General class to render http response"""

    def write(self, *a, **kw):
        """Write generic http response with the passed parameters"""
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """Utility function that can add new stuff to parameters passed"""
        params['style']='cerulean'
        if self.user : 
          params['welcome']='%s' % self.user.username
          params['logout']='Logout'
        else :
          params['welcome']='Login'
          params['login']='Login'
          params['signup']='Signup'

        return render_str(template, **params)

    def render(self, template, **kw):         
        """Render jinja template with named parameters"""
        self.write(self.render_str(template, **kw))
    
    def set_secure_cookie(self, name, val):
        """Send a http header with a hashed cookie"""
        hashed_cookie = make_cookie_hash(val)
        self.response.headers.add_header('Set-Cookie',
              "%s=%s; Path='/'" % (name,hashed_cookie))

    def read_secure_cookie(self, name):
        """Check if requesting browser sent us a cookie"""
        hashed_cookie = self.request.cookies.get(name)
        logging.error("Cookie name %s hash %s" % (name,hashed_cookie)) 
        if hashed_cookie :
            return verify_cookie_hash(hashed_cookie)
        else:
            return None

    def initialize(self, *a, **kw):
        """Function called before requests are processed.
           Used to check for sent cookies"""
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.get_by_id(int(uid))





class FrontPageHandler(Handler):
    """Class used to render the main page of the site"""

    def render_front(self, entries={}):
        """utility function used to render the front page"""
        self.render('index.html')

    def get(self):
        """function called when the front page is requested"""
        self.render_front()


class ExplorerHandler(Handler):
    def get(self):
        local_path = urllib.url2pathname(self.request.get("path"))

        if local_path == '' :
            local_path = "videos/"

        call(["ls","-l"])
        try:
            logging.error("try!")
            os_path=os.path.join(os.path.dirname(__file__),local_path)
            logging.error("ospath!")
            if os.path.isfile(os_path[:-1]) is True:
                logging.error("isfile!")
                if is_video(os_path[:-1]) is True:
                    self.redirect("explorer")
                    return
            file_list = os.listdir(os_path)
            logging.error("filelist")
        except:
            logging.error("except!")
            self.redirect("explorer")
            return


        full_path=[]
        for item in file_list:
            full_path.append(urllib.pathname2url(local_path+item))
        tuplist = zip(file_list,full_path)
        self.render("explorer.html",tuplist=tuplist)


class TestHandler(Handler):
    def get(self):
      self.render("test.html")


