from Products.PythonScripts.PythonScript import manage_addPythonScript
from collective.multimail.testing import COLLECTIVE_MULTIMAIL_INTEGRATION, COLLECTIVE_MULTIMAIL_FUNCTIONAL
from Products.MailHost.interfaces import IMailHost
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests.utils import MockMailHost
import unittest2 as unittest
from zope.component import getSiteManager, getMultiAdapter
from Acquisition import aq_base

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login
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

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        #self.folder.invokeFactory("EasyNewsletter", "newsletter")
        #self.newsletter = self.folder.newsletter
        #self.newsletter.senderEmail = "newsletter@acme.com"
        #self.newsletter.senderName = "ACME newsletter"
        #self.newsletter.testEmail = "test@acme.com"

    def tearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)


    def _test_send_easynewsletter(self):

        mm = self.portal['MultiMailHost']
        self.assertTrue(len(mm['one'].messages) == 0)


        self.newsletter.invokeFactory("ENLIssue", id="issue")
        self.newsletter.issue.title="Title"
        self.portal.REQUEST.form.update({
            'sender_name': self.newsletter.senderName,
            'sender_email': self.newsletter.senderEmail,
            'test_receiver': self.newsletter.testEmail,
            'subject': self.newsletter.issue.title,
            'test': 'submit',
        })
        view = getMultiAdapter(
            (self.newsletter.issue, self.portal.REQUEST),
            name="send-issue")
        view = view.__of__(self.portal)

        view.send_issue()

        self.assertEqual(len(self.mailhost.messages), 1)
        self.assertTrue(self.mailhost.messages[0])
        msg = str(self.mailhost.messages[0])
        self.assertIn('To: <test@acme.com>', msg)
        self.assertIn('From: ACME newsletter <newsletter@acme.com>', msg)


        #we have to send via a real MailHost object
        mailhost = self.portal._original_MailHost
        mailhost.send("hello", mto="one", mfrom='test', subject="s")
        self.assertTrue('To: one' in mm['one'].messages[-1])

