# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResBank(models.Model):
    _inherit = 'res.bank'

    name = fields.Char(
        translate=True,
    )
    abbrev = fields.Char(
        string='Abbreviation',
        size=100,
        required=False,
    )
    code = fields.Char(
        string='Code',
        size=100,
        required=False,
    )


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    bank_branch = fields.Many2one(
        'res.bank.branch',
        domain="[('bank_id', '=', bank)]",
        required=True,  # for PABI2, this is required
    )

    @api.onchange('bank')
    def _onchange_bank(self):
        self.bank_branch = False

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s %s' % (rec.bank.abbrev, rec.acc_number)))
        return res


class ResBankBranch(models.Model):
    _name = 'res.bank.branch'
    _description = 'Bank Branch'

    name = fields.Char(
        string='Name',
        size=500,
        translate=True,
        required=True,
    )
    code = fields.Char(
        string='Code',
        size=100,
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
