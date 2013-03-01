# -*- extra stuff goes here -*-

from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory("collective.multimail")


from ScriptableMailHost import ScriptableMailHost, manage_addScriptableMailHostForm, manage_addScriptableMailHost
from MultiMailHost import MultiMailHost, manage_addMultiMailHostForm, manage_addMultiMailHost

def initialize(context):
    """Initializer called when used as a Zope 2 product."""


    context.registerClass (
            ScriptableMailHost,
            constructors=(manage_addScriptableMailHostForm, manage_addScriptableMailHost)
        )

    context.registerClass (
            MultiMailHost,
            constructors=(manage_addMultiMailHostForm, manage_addMultiMailHost)
        )
