# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    is_transdebt = fields.Boolean(
        string='Transfer Debt',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    transdebt_partner_id = fields.Many2one(
        'res.partner',
        string='Trasnfer Debt To',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.multi
    def onchange_partner_id(self, partner_id, journal_id, amount,
                            currency_id, ttype, date):
        res = super(AccountVoucher, self).\
            onchange_partner_id(partner_id, journal_id, amount,
                                currency_id, ttype, date)
        res = res or {'value': {}}
        res['value']['transdebt_partner_id'] = False
        res['value']['is_transdebt'] = False
        # res['domain'] = 'domain' in res and res['domain'] or {}
        # if partner_id:
        #     partner = self.env['res.partner'].browse(partner_id)
        #     res['domain']['transdebt_partner_id'] = \
        #         [('id', 'in', partner.transdebt_partner_ids.ids)]
        # else:
        #     res['domain']['transdebt_partner_id'] = [('id', 'in', [])]
        return res

    @api.onchange('is_transdebt', 'transdebt_partner_id')
    def _onchange_transdebt(self):
        self.supplier_bank_id = False
        _ids = self.partner_id.transdebt_partner_ids.ids
        return {'domain': {'transdebt_partner_id': [('id', 'in', _ids)]}}
