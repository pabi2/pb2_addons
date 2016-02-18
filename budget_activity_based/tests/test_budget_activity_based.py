# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# © 2016 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


class TestBudgteActivityBased(common.TransactionCase):

    def setUp(self):
        super(TestBudgteActivityBased, self).setUp()
        # Prepare Test Data
        self.product1 = self.env.ref('product.product_product_7')
        self.product2 = self.env.ref('product.product_product_9')
