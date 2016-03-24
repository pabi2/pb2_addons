# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class PurchaseType(models.Model):
    _name = 'purchase.type'
    _description = 'PABI2 Purchase Type'

    name = fields.Char(string='Purchase Type')


class PurchaseMethod(models.Model):
    _name = 'purchase.method'
    _description = 'PABI2 Purchase Method'

    name = fields.Char(string='Purchase Method')
