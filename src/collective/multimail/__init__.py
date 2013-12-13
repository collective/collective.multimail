# -*- extra stuff goes here -*-

from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory("collective.multimail")
from Products.CMFCore import utils as CMFCoreUtils


from ScriptableMailHost import ScriptableMailHost, manage_addScriptableMailHostForm, manage_addScriptableMailHost
from MultiMailHost import manage_addMultiMailHostForm, manage_addMultiMailHost
import MultiMailHost

def initialize(context):
    """Initializer called when used as a Zope 2 product."""


    #context.registerClass (
    #        ScriptableMailHost,
    #        constructors=(manage_addScriptableMailHostForm, manage_addScriptableMailHost)
    #    )

    context.registerClass (
            MultiMailHost.MultiMailHost,
            constructors=(manage_addMultiMailHostForm, manage_addMultiMailHost)
        )

    tools = (MultiMailHost, )
    CMFCoreUtils.ToolInit(MultiMailHost.MultiMailHost.meta_type,
                          tools=tools).initialize(context)