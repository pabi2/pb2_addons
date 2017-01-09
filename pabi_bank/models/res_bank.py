# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResBank(models.Model):
    _inherit = 'res.bank'

    abbrev = fields.Char(
        string='Abbreviation',
        required=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
    )


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    bank_branch = fields.Many2one(
        'res.bank.branch',
        domain="[('bank_id', '=', bank)]",
    )

    @api.onchange('bank')
    def _onchange_bank(self):
        self.bank_branch = False


class ResBankBranch(models.Model):
    _name = 'res.bank.branch'
    _description = 'Bank Branch'

    name = fields.Char(
        string='Name',
        translate=True,
        required=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
    )
    bank_id = fields.Many2one(
        'res.bank',
        sring='Bank',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
