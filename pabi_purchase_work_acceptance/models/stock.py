# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    acceptance_id = fields.Many2one(
        'purchase.work.acceptance',
        string='Work Acceptance',
        domain="[('state', 'not in', ('done','cancel')),"
               "('order_id', '=', origin)]",
        copy=False,
    )
    ref_invoice_ids = fields.Many2many(
        'account.invoice',
        'stock_picking_invoice_rel',
        'picking_id', 'invoice_id',
        string='Ref Invoices',
        readonly=True,
        copy=False,
        help="Reference invoices created from picking.",
    )
    ref_invoice_count = fields.Integer(
        string='Supplier Invoice',
        compute='_compute_ref_invoice_count',
    )

    @api.multi
    def _compute_ref_invoice_count(self):
        for rec in self:
            rec.ref_invoice_count = len(rec.ref_invoice_ids)

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        acceptance = picking.acceptance_id
        if acceptance:
            vals.update({
                'origin': "%s:%s" % (
                    vals['origin'],
                    acceptance.name,
                ),
                'date_invoice': acceptance.date_invoice,
                'supplier_invoice_number': acceptance.supplier_invoice,
                'reference': acceptance.order_id.name,
            })
        res = super(StockPicking,
                    self)._create_invoice_from_picking(picking, vals)
        return res

    @api.multi
    def invoice_open(self):
        self.ensure_one()
        ACTIONS = {'out_invoice': 'account.action_invoice_tree1',
                   'out_refund': 'account.action_invoice_tree3',
                   'in_invoice': 'account.action_invoice_tree2',
                   'in_refund': 'account.action_invoice_tree4'}
        action_str = False
        invoices = self.ref_invoice_ids
        if invoices:
            action_str = ACTIONS[invoices[0].type]
        else:
            raise ValidationError(_('No invoice reference.'))
        action = self.env.ref(action_str)
        result = action.read()[0]
        invoices = self.ref_invoice_ids
        result['domain'] = [('id', 'in', invoices.ids)]
        return result
