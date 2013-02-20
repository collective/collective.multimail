
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

	2.  


mailhost object should be used for email address which begin with 'sendnews:'

This is a paragraph It's quite
short

	This paragraph *will* result **in** an indentation blobk of
	text, bypikc

this is another one. ``fixed space literal``


 1. the first of many in a list
    and here is the second line

    a) And this is an a

    b) and this is a b

 2. a second line

 3. a third line

 * an important point
 * a second important point

    - a sub point of the above

Section Two
~~~~~~~~~~~

what
  this is a what! beleive it or not!

how
  no need to ask

Sub section
+++++++++++
::

  A little bit of code
      for us to know
    for a little infor

Here werw are again