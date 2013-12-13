
from collective.multimail import MessageFactory as _


from Products.MailHost.interfaces import IMailHost
from zope.interface import Interface
from zope.schema import TextLine, Text

class IScriptableMailHost(Interface):

	id = TextLine (
		title=_(u'ID'),
		readonly=True,
		required=True
		)

	script = Text (
		title=_(u"Script"),
		readonly=False,
		required=False,
		default=_(u'') )


class IMultiMailHost(IMailHost): pass

class MultiMailChainStop(Exception): pass



