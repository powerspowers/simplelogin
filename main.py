#!/usr/bin/env python

import webapp2
import os
import uuid

from gaesessions import *
from models import *

from google.appengine.ext.webapp import template


### LOGIN ###

class SigninPost(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        pwd = self.request.get('password')
                
        m = hashlib.sha1()
        m.update(pwd)
        hashPwd = m.hexdigest()
        
        emailLower = email.lower()

        account = SimpleAccount.all().filter('emailLower', emailLower).get()
        if account:
            if (hashPwd == account.password):
                session = get_current_session()
                if session.is_active():
                    session.terminate()
                session = get_current_session()
                session['me'] = account.simpleid
                session['firstName'] = account.firstName
                session['lastName'] = account.lastName
                self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/')

            
class SignupPost(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        pwd = self.request.get('password')
        firstname = self.request.get('firstname')
        lastname = self.request.get('lastname')
        
        session = get_current_session()
        if session.is_active():
            session.terminate()
        
        result = doSignup(email, pwd, firstname, lastname)
        if result[0]:
            # Success
            account = result[1]
            session = get_current_session()
            session['me'] = account.simpleid
            session['firstName'] = account.firstName
            session['lastName'] = account.lastName
            self.redirect('/')
        else:
            failReason = result[1]
            self.redirect('/&err=' + failReason)            

def doSignup(email, pwd, firstname, lastname):
    emailLower = email.lower()
    existingId = SimpleAccount.all().filter('emailLower', emailLower).get()
    
    failReason = None
    if (existingId == None):
        account = createAccount(emailLower, pwd, firstname, lastname)
    else:
        failReason = 'That email is already associated with another account'

    # Return list, first item indicates success, next is either account or failReason
    if failReason == None:
        return [1, account]
    else:
        return [0, failReason]

def createAccount(emailLower, pwd, firstname, lastname):   
    simpleid = str(uuid.uuid4())
    account = SimpleAccount(key_name=simpleid)
    account.simpleid = simpleid
    account.emailLower = emailLower
    account.firstName= firstname
    account.lastName= lastname

    m = hashlib.sha1()
    m.update(pwd)
    hashPwd = m.hexdigest()
    account.password = hashPwd
                    
    account.put()                   

    return account

class Signout(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.is_active():
            session.terminate()
        self.redirect('/')
        
### CRON ###

class CleanUpSessions(webapp2.RequestHandler):
    def get(self):
        while not delete_expired_sessions():
            pass

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {
        }
        sessionCheck(template_values)
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

def sessionCheck(template):
    session = get_current_session()
    if session.has_key('me'):
        template['loggedin'] = True
        template['firstname'] = session['firstName']
        template['lastname'] = session['lastName']
    else:
        template['loggedin'] = False
    return template
    

app = webapp2.WSGIApplication([

    # LOGIN
    ('/s/signin',  SigninPost),
    ('/s/signup',  SignupPost),
    ('/s/signout', Signout),

    # CRON
    ('/s/cleanupsessions', CleanUpSessions),
    
    ('/', MainHandler)
], debug=True)
