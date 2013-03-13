
from urllib import quote

from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import Item
from Products.MailHost.interfaces import IMailHost
from AccessControl.SecurityInfo import ClassSecurityInfo

from zope.schema.fieldproperty import FieldProperty
from zope.interface import implements
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from AccessControl.class_init import InitializeClass
from AccessControl.Permissions import use_mailhost_services, change_configuration

from interfaces import IScriptableMailHost
from Acquisition import Implicit
from Globals import Persistent
from AccessControl.Role import RoleManager
from OFS.SimpleItem import Item
from collective.multimail import MessageFactory as _

from App.special_dtml import DTMLFile
import os

from Products.PythonScripts.PythonScript import PythonScript

from App.Common import package_home
from OFS.History import Historical
from OFS.SimpleItem import SimpleItem
from OFS.Cache import Cacheable
from OFS.History import Historical
from Shared.DC.Scripts.Script import BindingsUI


class ScriptableMailHost (PythonScript):
    """Scriptable MailHost"""


    implements(IMailHost,IScriptableMailHost)

    meta_type = "Scriptable Mail Host"
    security = ClassSecurityInfo()

    manage_options = (
        {'label':'Edit',
         'action':'ZPythonScriptHTML_editForm',
         'help': ('PythonScripts', 'PythonScript_edit.stx')},
        ) + BindingsUI.manage_options + (
        {'label':'Proxy',
         'action':'manage_proxyForm',
         'help': ('OFSP','DTML-DocumentOrMethod_Proxy.stx')},
        ) + Historical.manage_options + SimpleItem.manage_options + \
        Cacheable.manage_options


    def __init__ (self, *args, **kwargs):
        super(ScriptableMailHost, self).__init__ (*args, **kwargs)

        
    security.declareProtected(use_mailhost_services, 'send')
    def send(self, messageText, mto=None, mfrom=None,
              subject=None, encode=None,
              immediate=False, charset=None, msg_type=None):
        """Send mail.
        """

        bound_names = dict( 
                    messageText=messageText,
                    mto=mto,
                    mfrom=mfrom,
                    subject=subject,
                    encode=encode,
                    immediate=immediate,
                    charset=charset,
                    msg_type=msg_type )

        self._exec (bound_names, args=(), kw={})


    def _exec(self, bound_names, args, kw):
        bound_names = dict(bound_names)
        bound_names["mailhost"] = getToolByName(self, 'MailHost')
        bound_names["portal"] = getToolByName(self, 'portal_url').getPortalObject()
        super(ScriptableMailHost, self)._exec(bound_names, args=args, kw=kw)



InitializeClass (ScriptableMailHost)



manage_addScriptableMailHostForm = DTMLFile('templates/addScriptableMailHostForm', globals())


_default_file = os.path.join(package_home(globals()), 'default_py')

def manage_addScriptableMailHost(self, id, REQUEST=None,  submit=None):
    """Add a Python script to a folder.
    """
    id = str(id)
    id = self._setObject(id, ScriptableMailHost(id))
    if REQUEST is not None:
        file = REQUEST.form.get('file', '')
        if type(file) is not type(''): file = file.read()
        if not file:
            file = open(_default_file).read()
        self._getOb(id).write(file)
        try: u = self.DestinationURL()
        except: u = REQUEST['URL1']
        if submit==" Add and Edit ": u="%s/%s" % (u,quote(id))
        REQUEST.RESPONSE.redirect(u+'/manage_main')
    return ''

