
from zope.interface import implements
from Products.MailHost.interfaces import IMailHost
from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.class_init import InitializeClass

import threading
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import yaml
from AccessControl.SecurityManagement import getSecurityManager

from interfaces import MultiMailChainStop, IMultiMailHost

from OFS.Folder import Folder
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from App.special_dtml import DTMLFile
from AccessControl.Permissions import use_mailhost_services, change_configuration
from persistent.dict import PersistentDict

manage_addMultiMailHostForm=DTMLFile('templates/addMultiMailForm', globals())

from email.message import Message

import re
_re_cache = {}

_MARKER_OBJECT = object()

def manage_addMultiMailHost(self, id, title='', REQUEST=None):
    """Add a new MultiMailHost object with id *id*. 
    """
    ob = MultiMailHost(id)
    ob.title = title
    self._setObject(id, ob)
    ob = self._getOb(id)

    checkPermission=getSecurityManager().checkPermission

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class MultiMailHost(Folder):
    """MultiMailHost"""

    implements(IMailHost)

    meta_type = "Multi Mail Host"
    security = ClassSecurityInfo()

    smtp_host = '-'

    manage_options = Folder.manage_options + ( {
            'label': 'Set Rules',
            'action': 'manage_setDefaultChainForm',
            'help': () 
        },) 


    def __init__(self, id=None):

        if id is not None:
            self.id = str(id)

        self._chains = PersistentDict()
        self._chainDefaultConfig  = ''




    security.declareProtected(use_mailhost_services, 'send')
    def send(self, messageText, mto=None, mfrom=None, subject=None,
            encode=None, immediate=False, charset='utf8', msg_type=None):
        """Send mail.
        """

        sendargs = dict(
                messageText=messageText,
                mto=mto,
                mfrom=mfrom,
                subject=subject,
                encode=encode,
                immediate=immediate,
                charset=charset,
                msg_type=msg_type  )


        #detect mail loops
        thread_data = threading.local()
        depth = getattr(thread_data, "collective_multimailhost_send_depth", 0)
        if depth > 32:
            raise Exception("multimail send recursion depth exceeded")
        thread_data.collective_multimailhost_send_depth = depth + 1

        try:
            self._sendToChain ("default", 0, sendargs)
        except MultiMailChainStop:
            pass


    def secureSend(self, message, email_recipient, source,
                                subject, subtype,
                                charset=None, debug=False):
        self.send(message, email_recipient, source, subject=subject, charset=charset, immediate=True)



    def _matchRuleForSend (self, rule, sendargs):


        header_match = rule.get('header-match', {})


        if len(header_match) > 0:

            ### Normalise headers ###

            headers = {}
            if isinstance(type(sendargs["messageText"]), Message):
                for key, value in sendargs["messageText"].items():

                    # not suer if theis is the correct way to decode a MIME header value
                    headers[key.lower()] = str(value)

            # all sorts of email assumptions made here (sorry), eg that the To
            # and from  is the same as the mail envelope as the MIME header
            headers['to'] = sendargs['mto'] or headers.get('to', None)
            if headers['to'] is None:
                del headers['to']

            headers['from'] = sendargs['mfrom'] or headers.get('from', None)
            if headers['from'] is None:
                del headers['from']

            headers['subject'] = sendargs['subject'] or headers.get('subject', None)
            if headers['subject'] is None:
                del headers['subject']


            ### search for matches ###

            for header, expression in header_match.items():

                header = header.lower()

                # get compiled regular expression
                compiled = _re_cache.get(expression, None)
                if compiled is None:
                    try:
                        compiled = _re_cache[expression] = re.compile(expression)
                    except:
                        return False

                value = headers.get(header, None)
                if value is not None:
                    if compiled.search(value) is None:
                        return False
                else:
                    return False

        return True




    def _sendToChain(self, chain, currentDepth, sendargs):
        """Send mail.
        """

        currentDepth = currentDepth + 1

        chain = self._getChain(chain)

        for rule in chain:

            if self._matchRuleForSend (rule, sendargs):

                action = rule['action']

                if action == 'send and continue':
                    self[rule['mailhost']].send(**sendargs)

                elif action == 'send and stop':
                    self[rule['mailhost']].send(**sendargs)
                    raise MultiMailChainStop()

                elif action == 'stop':
                    raise MultiMailChainStop()

                elif action == 'send and return':
                    raise NotImplemented()
                    self[rule['mailhost']].send(**sendargs)
                    return

                elif action == 'jump':
                    raise NotImplemented()
                    self._sendToChain(rule['chain'], currentDepth, sendargs)

                elif action == 'return':
                    raise NotImplemented()
                    return

                else:
                    raise Exception("Invalid action")

    template_manage_setDefaultChainForm = PageTemplateFile("templates/setDefaultChainForm.zpt", globals())
    def manage_setDefaultChainForm (self):
        """manage_setDefaultChainForm"""
        return self.template_manage_setDefaultChainForm.pt_render({'context':self})
        


    def manage_setDefaultChain (self, yamlstring):
        """manage_setDefaultChain"""

        self._chainDefaultConfig = yamlstring
        rules = yaml.load(yamlstring)

        self._setChain("default", rules)

        self.REQUEST.RESPONSE.redirect(self.REQUEST['URL1']+'/manage_setDefaultChainForm')

    def _setChain(self, chain, rules):

        if chain != 'default':
            raise NotImplemented("support for only a default chain")

        for r in rules:
            if r['action'] not in ('send and continue', 'send and stop', 'stop'):
                raise Exception ("invalid action")

        self._chains[chain] = rules

    def _getChain (self, chain):
        return self._chains[chain]

InitializeClass(MultiMailHost)
