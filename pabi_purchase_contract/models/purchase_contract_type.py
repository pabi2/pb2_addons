# -*- coding: utf-8 -*-
from openerp import models, fields


class PurchaseContractType(models.Model):
    _name = 'purchase.contract.type'
    name = fields.Char(string="Name")
