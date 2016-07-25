# -*- coding: UTF-8 -*-
from openerp import models, fields


class purchase_contract_collateral(models.Model):
    _name = 'purchase.contract.collateral'
    name = fields.Char(string="Name")

purchase_contract_collateral()
