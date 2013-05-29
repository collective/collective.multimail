from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost
from MultiMailHost import MultiMailHost
from interfaces import IMultiMailHost

_STASH_NAME = "collective.multimail-MailHost_stashed"


### Setup of mailhost - stash current mail host...

def setupPreToolSet(context):
    if not context.readDataFile('multimailhost_various.txt'):
        return
    stash_MailHost(context)

def stash_MailHost(context):
    portal = getToolByName(context._site, 'portal_url').getPortalObject()
    # let's not atempt recousion
    if type(IMultiMailHost.implementedBy(portal["MailHost"])) != MultiMailHost:
        portal._setObject(_STASH_NAME, portal["MailHost"])


### Save the stashed mailhost into the multimailhost...

def setupPostToolSet(context):
    if not context.readDataFile('multimailhost_various.txt'):
        return
    save_stashed_MailHost(context)

def save_stashed_MailHost(context):
    portal = getToolByName(context._site, 'portal_url').getPortalObject()
    if _STASH_NAME in portal:
        portal["MailHost"]._setObject('MailHost_default', _STASH_NAME)
        portal._delObject(_STASH_NAME)






