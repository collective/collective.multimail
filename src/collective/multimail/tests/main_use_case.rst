
======================
 collective.multimail 
======================

-----------------------------------------------------------------------------------------
 Zope MailHost for routing messages to other Zope MailHosts and Zope Scriptable MailHost
-----------------------------------------------------------------------------------------


Main Scenario
=============

    1.  An integrator creates a scriptable mailhost object and registers it with
        the multimail mailhost object by specifying that the postman user has 
        the privilege to use it and that the scriptable

>>> MailHost.manage_addScriptableMailHost(id='sendnewsletter')
>>> browser.navigate('/portal/MailHost/manage_rules')
>>> browser.getControl('addline').click()
>>> browser.getControl('expression').value = 'python: permission = zope.manager'
>>> browser.getControl('mto').value = r'^sendnewsletter:.+'
>>> browser.getControl('action') = 'MailHost Send and Stop'
>>> browser.getControl('').value = 'sendnewsletter'
>>> browser.getControl("save").click()

	2.  The integrator writes a script which receives the mail and resends it multiple
        times based on results of a catalogQuery returning subscriptions objects.

>>> browser.navigate('/portal/MailHost/sendnewsletter/manage_properties')
>>> browser.getControl('script').value = """
... 
... subscriptions = [
...    ('adam@example.com',   'blue' ),
...    ('bel@example.com',    'green'),
...    ('charls@example.com', 'red'  ),
...    ('dave@example.com',   'blue' ),
...    ('eve@example.com',    'green'),
...    ('fred@example.com',   'green ),
...    ('gav@example.com',    'blue' ),
...    ('harry@example.com',  'orange'),
...    ('izy@example.com',    'green' )   ]
... 
... path = mto.split(":")[1]
... context = portal.restrictedTreverse(path)
... 
... subjects = context.Subject.split(" ")
... results = filter(lambda s: s[1] in category)
... 
... for s in kkk:
... 
...     mailhost.send(
...       personalMessageText,
...       mto=s.Email, mfrom=mfrom,
...       subject=subject )
... 
... """

	3. Content editor creates a pages for which they would like to send as a
       newsletter. And send the newsletter. We will replace the default mailhost
       with a dummy one fist,

>>> Mailhost.default = MockMailHost('default')

>>> portal.manage_addPage(id='newsletter', subject=['blue'], body='some reallly'\
...   'interesting text' )
>>> message = portal['newsletter'].renderBoddy()
>>> mfrom = 'newsletter@plonesite.com'
>>> mto = 'sendnewsletter:/newsletter'
>>> MailHost.send(message, mto, mfrom, subject="Newsletter")

>>> print MailHost.default.messages
one
two
three



