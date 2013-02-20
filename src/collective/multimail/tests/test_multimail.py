
from collective.multimail.testing import COLLECTIVE_MULTIMAIL_INTEGRATION

from Products.CMFCore.utils import getToolByName

import unittest2 as unittest
import doctest

class TestMultiMail (unittest.TestCase):

    layer = COLLECTIVE_MULTIMAIL_INTEGRATION


    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
    
    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product 
            installed
        """
        pid = 'collective.multimail'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')


class test_main_use_case():

	layer = COLLECTIVE_MULTIMAIL_FUNCTIONAL 
	options = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF
	main_use_case = doctest.DocfileSuite('tests/main_use_case.rst', optionflags=options, globs=dict(layer=layer))

	suite = unittest.TestSuite()
	suite.add_Tests([main_use_case])
	suite.layer = layer

	return suite
