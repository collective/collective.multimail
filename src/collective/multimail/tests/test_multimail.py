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

TESTMSG = '''X-SMTPAPI: {"to": ["<kiki@mail.com>", "<glebe5@mail.com>"]}
Content-Type: multipart/alternative;
 boundary="===============9046951120719983934=="
MIME-Version: 1.0
To: <abcd@mail.com>
From: <abc@mail.com>Subject: Is1

--===============9046951120719983934==
Content-Type: multipart/related;
 boundary="===============1341506654315137165=="
MIME-Version: 1.0

--===============1341506654315137165==
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: quoted-printable


Dear Test Member
=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=
=3D=3D=3D=3D=3D=3D=3D=3D=3D

Be safe 1

=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=
=3D=3D=3D=3D=3D=3D=3D=3D=3D


------------------------------------------------------------------------


--===============1341506654315137165==--
--===============9046951120719983934==
Content-Type: multipart/related;
 boundary="===============2152036350975026834=="
MIME-Version: 1.0

--===============2152036350975026834==
Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: quoted-printable
<html xmlns=3D"http://www.w3.org/1999/xhtml">
<head>
<title>Is1</title>

</head>
<body>
<!-- this is the header of the newsletter -->
<div class=3D"header">
<p>Dear Test Member<br />=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=
=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D</p>
</div>
<!-- this is the main text of the newsletter -->
<div class=3D"body-text">
<p>Be safe 1</p>
</div>
<!-- this is the footer of the newsletter -->
<div class=3D"footer">
<p>=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=
=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D<br /></p>
</div>
</body>
</html>
--===============2152036350975026834==--
--===============9046951120719983934==--
'''




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

    def test_RFC2822(self):

        mm = self.portal['MultiMailHost']

        mm._setChain("default",
            [
                {
                    'header-match': {'to':'abcd@mail\.com'},
                    'action': 'send and stop',
                    'mailhost': 'two'
                },
            ]
            )

        mm.send(TESTMSG)

        self.assertTrue('X-SMTPAPI:' in mm['two'].messages[-1])

