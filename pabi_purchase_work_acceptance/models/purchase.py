# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
import datetime
from dateutil.relativedelta import relativedelta


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
        # readonly=True,
        # states={'draft': [('readonly', False)]},
    )
    date_fine = fields.Date(
        string='Fine Date',
        default=lambda self: fields.Date.context_today(self),
        # readonly=True,
        # states={'draft': [('readonly', False)]},
    )
    fine_num_days = fields.Integer(
        string='Delivery Within (Days)',
        default=15,
        # readonly=True,
        # states={'draft': [('readonly', False)]},
    )
    fine_num_months = fields.Integer(
        string='Delivery Within (Months)',
        default=1,
        # readonly=True,
        # states={'draft': [('readonly', False)]},
    )
    fine_rate = fields.Float(
        string='Fine Rate',
        required=True,
        default=0.0,
        # readonly=True,
        # states={'draft': [('readonly', False)]},
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
    date_contract_end = fields.Date(
        string='Contract End Date',
        # default=lambda self: fields.Date.context_today(self),
        track_visibility='onchange',
        required=False,
        # readonly=True,
        # states={
        #     'draft': [('readonly', False)],
        #     'sent': [('readonly', False)],
        #     'bid': [('readonly', False)],
        #     'confirmed': [('readonly', False)],
        # },
    )

    @api.model
    @api.onchange('date_contract_start', 'fine_condition', 'fine_num_days',
                  'fine_num_months', 'date_fine')
    def _onchange_contract_end_date(self):
        self.ensure_one()
        # THHoliday = self.env['thai.holiday']
        if not self.date_contract_start:
            raise ValidationError(_('No contract start date!'))
        start_date = datetime.datetime.strptime(
            self.date_contract_start,
            "%Y-%m-%d",
        )
        if self.fine_condition == 'day':
            num_of_day = self.fine_num_days
            end_date = start_date + datetime.timedelta(days=num_of_day)
            date_scheduled_end = "{:%Y-%m-%d}".format(end_date)
            # next_working_end_date = THHoliday.\
            #     find_next_working_day(date_scheduled_end)
        if self.fine_condition == 'month':
            num_months = self.fine_num_months
            end_date = start_date + relativedelta(months=+num_months)
            date_scheduled_end = "{:%Y-%m-%d}".format(end_date)
            # next_working_end_date = THHoliday.\
            #     find_next_working_day(date_scheduled_end)
        if self.fine_condition == 'date':
            date_scheduled_end = self.date_fine
            # next_working_end_date = THHoliday.\
            #     find_next_working_day(self.date_fine)
        self.date_contract_end = date_scheduled_end

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


class PurchaseType(models.Model):
    _inherit = 'purchase.type'

    to_receive = fields.Boolean(
        string='To Receive Product',
    )

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
  

    @api.model
    def default_get(self,fields):
        res = super(PurchaseOrderLine, self).default_get(fields)
        active_id = self._context.get('active_id')
        if self.browse(active_id)._context.get('order_line') is not None:
            order_id = max(self.browse(active_id)._context.get('order_line'))[1]
            last_rec = self.search([('id','=',order_id)], order='id desc', limit=1)
            date_now = datetime.datetime.now().strftime('%Y-%m-%d')
            if last_rec:
                res['product_id'] = last_rec.product_id.id
                res['name'] = last_rec.name            
        return res
            
    @api.multi
    def onchange_product_id(
            self, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft'):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name,
            price_unit=price_unit, state=state)
          
        active_id = self._context.get('active_id')
        if self.browse(active_id)._context.get('order_line') is not None:
            order_id = max(self.browse(active_id)._context.get('order_line'))[1]
            last_rec = self.search([('id','=',order_id)], order='id desc', limit=1)
            date_now = datetime.datetime.now().strftime('%Y-%m-%d')
            if last_rec.product_id.name == res['value']['name'] or last_rec.name == res['value']['name']:
                res['value']['product_id'] = last_rec.product_id.id
                res['value']['name'] = last_rec.name
                res['value']['date_planned'] = date_now
                res['value']['activity_group_id'] = last_rec.activity_group_id.id
                res['value']['activity_rpt_id'] = last_rec.activity_rpt_id.id
                res['value']['chartfield_id'] = last_rec.chartfield_id.id
                res['value']['fund_id'] = last_rec.fund_id.id
                res['value']['cost_control_id'] = last_rec.cost_control_id.id
                res['value']['product_qty'] = last_rec.product_qty
                res['value']['product_uom'] = last_rec.product_uom.id
                res['value']['price_unit'] = last_rec.price_unit
                res['value']['taxes_id'] = last_rec.taxes_id.ids
                res['value']['price_subtotal'] = last_rec.price_subtotal
                res['value']['fiscalyear_id'] = last_rec.fiscalyear_id.id             
        return res