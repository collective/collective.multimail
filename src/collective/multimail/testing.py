from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import collective.multimail


COLLECTIVE_MULTIMAIL = PloneWithPackageLayer(
    zcml_package=collective.multimail,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.multimail:testing',
    name="COLLECTIVE_MULTIMAIL",
    additional_z2_products=['Products.EasyNewsletter',
                            'Products.PloneFormGen'])

COLLECTIVE_MULTIMAIL_INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_MULTIMAIL, ),
    name="COLLECTIVE_MULTIMAIL_INTEGRATION")

COLLECTIVE_MULTIMAIL_FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_MULTIMAIL, ),
    name="COLLECTIVE_MULTIMAIL_FUNCTIONAL")
