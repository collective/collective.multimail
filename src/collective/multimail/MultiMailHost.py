from Products.Five import BrowserView
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
from email import message_from_string
from yaml.parser import ParserError
import logging
log = logging.getLogger("collective.multimail")


import re
_re_cache = {}

_MARKER_OBJECT = object()

DEFAULT_RULES = """
-
 action: 'send and stop'
 mailhost: 'default'
"""

class InvalidRulesException(Exception):
    pass


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

    implements(IMultiMailHost)

    meta_type = "Multi Mail Host"
    security = ClassSecurityInfo()

    manage_options =  ( ( {
            'label': 'Set Rules',
            'action': 'manage_setDefaultChainForm',
        },) + Folder.manage_options )



    def __init__(self, id=None):

        if id is not None:
            self.id = str(id)

        self._chains = PersistentDict()
        self._chainDefaultConfig  = DEFAULT_RULES


    def getChainConfig(self):
        """
        :return: current YAML config
        """
        return self._chainDefaultConfig


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
            matchargs = self._matchHeaders(sendargs)
            self._sendToChain ("default", 0, sendargs, matchargs)
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
            if isinstance(sendargs["messageText"], Message):
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

    def _matchHeaders(self, sendargs):
        """Sets missing message headers.
        returns fixed sendargs"""
        matchargs = sendargs
        messageText = sendargs['messageText'] if 'messageText' in sendargs else ''
        charset = sendargs['charset'] if 'charset' in sendargs else None

        # If we have been given unicode fields, attempt to encode them
        if isinstance(messageText, unicode):
            messageText = self._try_encode(messageText, charset)

        mo = messageText
        if not isinstance(messageText, Message):
            # Otherwise parse the input message
            mo = message_from_string(messageText)

        if 'messageText' in matchargs:
            matchargs['messageText'] = mo

        return matchargs

    def _try_encode(self, text, charset):
        """Attempt to encode using the default charset if none is
        provided.  Should we permit encoding errors?"""
        if charset:
            return text.encode(charset)
        else:
            return text.encode()


    def _sendToChain(self, chain, currentDepth, sendargs, matchargs):
        """Send mail. matchargs is just for _matchRuleForSend function
        """

        currentDepth = currentDepth + 1

        chain = self._getChain(chain)

        posargs = [sendargs[x] for x in ('messageText','mto','mfrom','subject',
                   'encode', 'immediate', 'charset', 'msg_type')]

        for rule in chain:

            if not self._matchRuleForSend(rule, matchargs):
                continue

            log.info("rule %s matched. send and continue" % rule)

            action = rule['action']
            if rule['mailhost'] == 'default':
                send = self.aq_parent.MailHost._old_send
            #elif rule['mailhost'] in self.objectIds():
            #    send = self.get(rule['mailhost']).send
            else:
                view = self.unrestrictedTraverse(rule['mailhost'])
                if IMailHost.providedBy(view):
                    send = view.send
                elif view is not None:
                    #assume its a callable
                    send = view
                else:
                    send = None

            if action == 'send and continue':
                send(*posargs)

            elif action == 'send and stop':
                send(*posargs)
                raise MultiMailChainStop()

            elif action == 'stop':
                raise MultiMailChainStop()

            elif action == 'send and return':
                raise NotImplemented()
                send(*posargs)
                return

            elif action == 'jump':
                raise NotImplemented()
                self._sendToChain(rule['chain'], currentDepth, sendargs, matchargs)

            elif action == 'return':
                raise NotImplemented()
                return

            else:
                raise Exception("Invalid action")
        log.info("end of chain reached" % rule)


    def _setChain(self, chain, rules):

        if not rules:
            raise InvalidRulesException("Empty rules")

        if chain != 'default':
            raise NotImplemented("support for only a default chain")

        for r in rules:
            if r['action'] not in ('send and continue', 'send and stop', 'stop'):
                raise InvalidRulesException ("invalid action")

        self._chains[chain] = rules

    def _getChain (self, chain):
        return self._chains[chain]

class ChainSetView(BrowserView):

    last_error = ""
    last_rules = None

    title = "blah"


    def __call__(self, yamlstring=None):
        """manage_setDefaultChain"""
        if yamlstring is None:
            self.last_rules = self.context.getChainConfig()
            return self.index()

        try:
            rules = yaml.load(yamlstring)
            self.context._setChain("default", rules)
            self.context._chainDefaultConfig = yamlstring
            self.last_error = ""
            self.last_rules = yamlstring
            self.request['manage_tabs_message'] = "Saved"
        except ParserError, e:
            self.last_error = str(e)
            self.last_rules = yamlstring
        except InvalidRulesException, e:
            self.last_error = str(e)
            self.last_rules = yamlstring

        return self.index()

#        self.request.RESPONSE.redirect(self.request['URL1']+'/manage_setDefaultChainForm')


InitializeClass(MultiMailHost)
