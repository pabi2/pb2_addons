# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _count_acceptances(self):
        PWAcceptance = self.env['purchase.work.acceptance']
        acceptance = PWAcceptance.search([('order_id', '=', self.id)])
        return {
            self.id: {
                'count_acceptance': len(acceptance),
            }
        }

    fine_condition = fields.Selection(
        selection=[
            ('day', 'Day'),
            ('date', 'Date'),
        ],
        string='Fine Condition',
        default='day',
        required=True,
    )
    date_fine = fields.Date(
        string='Fine Date',
        default=fields.Date.today(),
    )
    fine_num_days = fields.Integer(
        string='No. of Days',
        default=15,
    )
    fine_rate = fields.Float(
        string='Fine Rate',
        default=0.1,
    )
    acceptance_ids = fields.One2many(
        'purchase.work.acceptance',
        'order_id',
        string='Acceptance',
        readonly=False,
    )
    count_acceptance = fields.Integer(
        string='Count Acceptance',
        compute="_count_acceptances",
        store=True,
    )

    @api.multi
    def acceptance_open(self):
        return {
            'name': _('Purchase Work Acceptance'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.work.acceptance',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('order_id', '=', "+str(self.id)+")]",
        }
        return result


class PurchaseWorkAcceptance(models.Model):
    _name = 'purchase.work.acceptance'
    _description = 'Purchase Work Acceptance'

    name = fields.Char(
        string="Acceptance No.",
    )
    date_scheduled_end = fields.Date(
        string="Scheduled End Date",
    )
    date_contract_end = fields.Date(
        string="Contract End Date",
    )
    date_received = fields.Date(
        string="Receive Date",
    )
    is_manual_fine = fields.Boolean(
        string="Use Manual Fine",
    )
    manual_fine = fields.Float(
        string="Manual Fine",
        default=0.0,
    )
    manual_days = fields.Integer(
        string="No. of Days",
        default=1,
    )
    total_fine = fields.Float(
        string="Total Fine",
    )
    acceptance_line_ids = fields.One2many(
        'purchase.work.acceptance.line',
        'acceptance_id',
        string='Work Acceptance',
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )
    eval_receiving = fields.Selection(
        selection=[
            ('3', 'On time'),
            ('2', 'Late for 1-7 days'),
            ('1', 'Late for 8-14 days'),
            ('0', 'Late more than 15 days'),
        ],
        string='Rate - Receiving',
    )
    eval_quality = fields.Selection(
        selection=[
            ('2', 'Better than expectation'),
            ('1', 'As expectation'),
        ],
        string='Rate - Quality',
    )
    eval_service = fields.Selection(
        selection=[
            ('3', 'Excellent'),
            ('2', 'Good'),
            ('1', 'Satisfactory'),
            ('0', 'Needs Improvement'),
        ],
        string='Rate - Service',
    )


class PurchaseWorkAcceptanceLine(models.Model):
    _name = 'purchase.work.acceptance.line'
    _description = 'Purchase Work Acceptance Line'

    acceptance_id = fields.Many2one(
        'purchase.work.acceptance',
        string='Acceptance Reference',
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
    )
    name = fields.Char(
        string='Description',
        required=True,
    )
    balance_qty = fields.Float(
        string='Balance Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        readonly=True,
        required=True,
    )
    to_receive_qty = fields.Float(
        string='To Receive Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    product_uom = fields.Many2one(
        'product.uom',
        string='UoM',
    )
