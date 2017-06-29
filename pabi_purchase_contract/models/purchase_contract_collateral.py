# -*- coding: utf-8 -*-
from openerp import models, fields


class PurchaseContractCollateral(models.Model):
    _name = 'purchase.contract.collateral'
    name = fields.Char(string="Name")
