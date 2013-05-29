from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost
from MultiMailHost import MultiMailHost
from interfaces import IMultiMailHost

_STASH_NAME = "collective.multimail-MailHost_stashed"



def setupVerious(context):
    if not context.readDataFile('multimailhost_various.txt'):
        return
    stash_MailHost(context)
    createtool_MultiMailHost(context)
    save_stashed_MailHost(context)



def stash_MailHost(context):
    portal = getToolByName(context._site, 'portal_url').getPortalObject()
    # let's not atempt recousion
    if type(portal["MailHost"]) != MultiMailHost:
        portal._setObject(_STASH_NAME, portal["MailHost"])


def createtool_MultiMailHost(context):
    portal = getToolByName(context._site, 'portal_url').getPortalObject()
    if type(portal["MailHost"]) != MultiMailHost:
        portal._delObject("MailHost")
        portal._setObject("MailHost", MultiMailHost())


def save_stashed_MailHost(context):
    portal = getToolByName(context._site, 'portal_url').getPortalObject()
    if _STASH_NAME in portal:
        portal["MailHost"]._setObject('MailHost_default', portal[_STASH_NAME])
        portal._delObject(_STASH_NAME)






