# -*- coding: UTF-8 -*-
from openerp import models, fields


class purchase_contract_type(models.Model):
    _name = 'purchase.contract.type'
    name = fields.Char(string="Name")

purchase_contract_type()
