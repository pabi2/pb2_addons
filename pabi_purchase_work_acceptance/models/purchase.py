# -*- coding: utf-8 -*-

from openerp import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.one
    @api.depends('acceptance_ids')
    def _count_acceptances(self):
        PWAcceptance = self.env['purchase.work.acceptance']
        acceptance = PWAcceptance.search([('order_id', '=', self.id)])
        self.count_acceptance = len(acceptance)

    @api.one
    @api.depends('acceptance_ids')
    def _is_acceptance_done(self):
        PWAcceptance = self.env['purchase.work.acceptance']
        acceptances = PWAcceptance.search([('order_id', '=', self.id)])
        done = True
        if len(acceptances) == 0:
            done = False
        for acceptance in acceptances:
            if acceptance.state not in ('done', 'cancel'):
                done = False
                break
        self.acceptance_done = done

    fine_condition = fields.Selection(
        selection=[
            ('day', 'Day'),
            ('month', 'Month'),
            ('date', 'Date'),
        ],
        string='Fine Condition',
        default='day',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_fine = fields.Date(
        string='Fine Date',
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    fine_num_days = fields.Integer(
        string='Delivery Within (Days)',
        default=15,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    fine_num_months = fields.Integer(
        string='Delivery Within (Months)',
        default=1,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    fine_rate = fields.Float(
        string='Fine Rate',
        required=True,
        default=0.0,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    acceptance_ids = fields.One2many(
        'purchase.work.acceptance',
        'order_id',
        string='Acceptance',
        readonly=False,
    )
    acceptance_done = fields.Boolean(
        string='Work Acceptance Done',
        compute="_is_acceptance_done",
    )
    count_acceptance = fields.Integer(
        string='Count Acceptance',
        compute='_count_acceptances',
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

    @api.model
    def _prepare_inv_line(self, acc_id, line):
        res = super(PurchaseOrder, self)._prepare_inv_line(acc_id, line)
        if 'active_model' in self._context:
            if self._context['active_model'] == 'purchase.work.acceptance':
                active_id = self._context['active_id']
                WAcceptance = self.env['purchase.work.acceptance']
                acceptance = WAcceptance.browse(active_id)
                for wa_line in acceptance.acceptance_line_ids:
                    po_line_id = wa_line.line_id.id
                    if po_line_id == line.id:
                        res.update({
                            'price_unit': wa_line.price_unit or 0.0
                        })
        return res
