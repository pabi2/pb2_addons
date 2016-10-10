# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Bank(models.Model):
    _inherit = "res.partner.bank"

    journal_id = fields.Many2one(
        string='Default Account Journal',
    )
    journal_ids = fields.One2many(
        'account.journal',
        'bank_id',
        string='Account Journals',
    )
    branch_cheque = fields.Char(
        string='Bank Branch',
        size=64,
    )

    @api.multi
    def write(self, vals):
        res = super(Bank, self).write(vals)
        if vals.get('journal_ids', False) or vals.get('journal_id', False):
            for rec in self:
                if not rec.journal_id and not rec.journal_ids:
                    continue
                elif not rec.journal_id and rec.journal_ids:
                    rec.journal_id = rec.journal_ids[0]
                elif rec.journal_id not in rec.journal_ids:
                    rec.journal_ids += rec.journal_id
        return res

    @api.model
    def create(self, vals):
        res = super(Bank, self).create(vals)
        res.write(vals)
        return res
