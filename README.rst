.. contents::

.. image:: https://secure.travis-ci.org/collective/collective.multimail.png
    :target: http://travis-ci.org/collective/collective.multimail

Introduction
============

Allows you to use more than one mailhost. Email is filtered by rules which
determine which mailhost to send a particular email to. Each rule can apply
regular expressions to email headers such as "to", "from" and "subject".
Scripts or views can be configured in place of a mailhost to allow custom
behaviour.

Potential uses include:

- using different SMTP servers depending on the sender;
- expanding special email addresses into multiple send calls;
- sending via an external API such as twitter;
- adding additional headers or altering the text of standard Plone emails.

For example, if you have a rule chain::

    - header-match: {to: 'allsubscribers@notarealdomain'}
      action: 'send and stop'
      mailhost: '/sendtoall'

    # Catch-all rule, uses the patched MailHost object.
    - action: 'send and stop'
      mailhost: 'default'

and you have a Python Script ``sendtoall``::

    def sendtoall(messageText, mto=None, mfrom=None, subject=None, encode=None, immediate=False, charset='utf8', msg_type=None):
        for email in context.getSubscribers():
            context.MailHost.send(messageText, email, mfrom, subject, encode, immediate, charset, msg_type)

You can use the email address ``allsubscribers@notarealdomain`` in contentrules or
other places in Plone to deliver an email to a database of subscribers.

Details
=======

Either install via Generic Setup or by adding in the ZMI. Once a MultiMailHost
object is placed in the same folder as a normal MailHost object, a monkeypatch
to MailHost will allow MultiMail to handle all email sending.

Rule definition
---------------

A Rule Chain is a YAML list of rule definitions.
A Rule definition can contain:

header-match
  A dictionary of regular expressions for headers such as 'to', 'from'.

action
  Either 'send and continue', 'send and stop' or 'stop'

mailhost
  A traversable path to a IMailHost object or callable. Callables need to support
  the arguments (messageText, email, mfrom, subject, encode, immediate, charset, msg_type).
  The path is relative to the MultiMailHost and paths starting with / start from the Zope root.

Rules are evaluated top to bottom.

Rules are set via the ZMI.

``default`` is a special mailhost which uses the orginal mailhost object unfiltered. If
you want to resend an email and have it also filtered then use ``/MailHost``.

TODO
====

- [ ] Test with PloneFormGen
- [ ] Handle matching when email is sent as text including headers (like PFG)
- [ ] Ability to disable monkeypatch so can be used standalone
- [ ] Security around traverse to script


