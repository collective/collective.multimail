from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost


def setupVarious(context):
    if not context.readDataFile('multimailhost_various.txt'):
        return
    site = context.getSite()
    replace_mailhost(site)


def replace_mailhost(self):
    portal = getToolByName(self, 'portal_url').getPortalObject()
    portal.MultiMailHost._setObject('MailHost_default', portal.MailHost)
    portal._delObject('MailHost')
    portal._setObject('MailHost', portal.MultiMailHost)

    sm = self.getSiteManager()
    sm.registerUtility(portal.MailHost, provided=IMailHost)