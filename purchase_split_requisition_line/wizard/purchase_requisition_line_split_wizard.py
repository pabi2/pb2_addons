# -*- coding: utf-8 -*-
from openerp import api, models, fields
import itertools


class PurchaseRequisitionLineSplitWizard(models.TransientModel):
    _name = "purchase.requisition.line.split.wizard"

    requisition_line_ids = fields.One2many(
        'purchase.requisition.line.split.line',
        'wizard_id',
        string='Tax Lines',
    )

    @api.model
    def default_get(self, fields):
        res = super(PurchaseRequisitionLineSplitWizard, self).\
            default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        requisition = self.env[active_model].browse(active_id)
        res['requisition_line_ids'] = []
        for line in requisition.line_ids:
            vals = {
                'requisition_line_id': line.id,
                'number_split': 1,
            }
            res['requisition_line_ids'].append((0, 0, vals))
        return res

    @api.multi
    def split_requisition_line(self):
        self.ensure_one()
        for line in self.requisition_line_ids:
            # If number_split > 1
            if line.number_split > 1:
                for _ in itertools.repeat(None, line.number_split-1):
                    line.requisition_line_id.copy()
        return True


class PurchaseRequisitionLineSplitLine(models.TransientModel):
    _name = "purchase.requisition.line.split.line"

    wizard_id = fields.Many2one(
        'purchase.requisition.line.split.wizard',
        string='Wizard',
        ondelete='cascade',
        index=True,
        required=True,
    )
    requisition_line_id = fields.Many2one(
        'purchase.requisition.line',
        string='Requisition Line',
        readonly=True,
    )
    number_split = fields.Integer(
        string='Number Split',
    )
