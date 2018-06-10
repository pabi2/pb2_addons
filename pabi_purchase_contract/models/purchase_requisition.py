# -*- coding: utf-8 -*-
from openerp import api, fields, models, _


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    contract_ids = fields.One2many(
        'purchase.contract',
        'requisition_id',
        string='Contract',
        readonly=False,
    )
    count_contract = fields.Integer(
        string='Count Contract',
        compute='_count_contract',
        store=True,
    )

    @api.one
    @api.depends('contract_ids')
    def _count_contract(self):
        PContract = self.env['purchase.contract']
        contract = PContract.search([('requisition_id', '=', self.id)])
        self.count_contract = len(contract)

    @api.multi
    def contract_open(self):
        return {
            'name': _('PO Contracts'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.contract',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('requisition_id', '=', " + str(self.id) + ")]",
        }
