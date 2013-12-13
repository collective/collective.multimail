from Products.PythonScripts.PythonScript import manage_addPythonScript
from collective.multimail.testing import COLLECTIVE_MULTIMAIL_INTEGRATION, COLLECTIVE_MULTIMAIL_FUNCTIONAL
from Products.MailHost.interfaces import IMailHost
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests.utils import MockMailHost
import unittest2 as unittest
import doctest
from zope.component import getSiteManager
from Acquisition import aq_base
import transaction

from collective.multimail.ScriptableMailHost import manage_addScriptableMailHost


from StringIO import StringIO

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

class TestMultiMail (unittest.TestCase):

    layer = COLLECTIVE_MULTIMAIL_INTEGRATION


    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

        mm = self.portal['MultiMailHost']

        mm._setObject('one', MockMailHost('one') )
        mm._setObject('two', MockMailHost('two') )
        mm._setObject('catch_all', MockMailHost('catch_all') )

        mm._setChain("default",
            [
                {
                    'header-match': {'to': 'one'},
                    'action': 'send and stop',
                    'mailhost': 'one'
                },
                {
                    'header-match': {'to': 'two'},
                    'action': 'send and stop',
                    'mailhost': 'two'
                },
                {
                    'action': 'send and stop',
                    'mailhost': 'default'
                }
            ]
            )

    def tearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)
    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product 
            installed
        """
        pid = 'collective.multimail'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')



    def test_multi_mail_host(self):

#        setRoles(self.portal, TEST_USER_ID, ['Manager',])

        mm = self.portal['MultiMailHost']

        mm.send("hello", mto="one", mfrom='test', subject="s")
        mm.send("hello", mto="two", mfrom='test', subject="s")
        mm.send("hello", mto="other", mfrom='test', subject="s")


        self.assertTrue('To: one' in mm['one'].messages[-1])
        self.assertTrue('To: two' in mm['two'].messages[-1])
        self.assertTrue('To: other' in self.portal['MailHost'].messages[-1])


    def test_monkeypatch(self):

        mm = self.portal['MultiMailHost']
        self.assertTrue(len(mm['one'].messages) == 0)

        #we have to send via a real MailHost object
        mailhost = self.portal._original_MailHost
        mailhost.send("hello", mto="one", mfrom='test', subject="s")
        self.assertTrue('To: one' in mm['one'].messages[-1])

    def test_scriptable_mail_host(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager',])
        self.portal.sc_executed = False

        manage_addPythonScript(self.portal, 'scriptablemailhost')
        sc = self.portal['scriptablemailhost']

        message = "hello, world!"
        mto = "a@b.com"
        mfrom = "b@b.com"
        subject = "test 7f14cb3d-d0b7-4950-b863-329da017a9e8"

        script = "context.MailHost.send(messageText, mto=mto, mfrom=mfrom, subject=subject)\n"
        sc.ZPythonScript_edit("messageText, mto, mfrom, subject, encode, immediate, charset, msg_type",
                              StringIO(script))

        mm = self.portal['MultiMailHost']
        mm._setChain("default",
            [
                {
                    'action': 'send and stop',
                    'mailhost': 'scriptablemailhost'
                },
            ]
            )

        mm.send(message, mto, mfrom, subject)

        lastMessage = self.portal.MailHost.messages[-1]
        self.assertTrue(('Subject: %s'%subject) in lastMessage)


def _test_suite():

    layer = COLLECTIVE_MULTIMAIL_FUNCTIONAL
    options = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF
    main_use_case = doctest.DocFileSuite('main_use_case.rst', optionflags=options, globs=dict(layer=layer))

    suite = unittest.TestSuite()
    #suite.addTests([main_use_case])
    #suite.addTests([TestMultiMail()])
    suite.layer = layer

    return suite
