# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api
from openerp.exceptions import Warning as UserError
from openerp import tools


class PABICustomerDunningReport(models.Model):
    _name = 'pabi.customer.dunning.report'
    _auto = False

    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item',
    )
    amount_residual = fields.Float(
        related='move_line_id.amount_residual',
        string='Balance',
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        related='move_line_id.invoice',
        string='Invoice',
    )
    reconcile_id = fields.Many2one(
        'account.move.reconcile',
        related='move_line_id.reconcile_id',
        string='Reconcile',
    )
    date_maturity = fields.Date(
        string='Due Date',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    date_run = fields.Date(
        string='Runing Date',
        compute='_compute_date',
    )
    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_date',
    )

    @api.multi
    @api.depends()
    def _compute_date(self):
        today = fields.Date.context_today(self)
        DATETIME_FORMAT = "%Y-%m-%d"
        for rec in self:
            rec.date_run = self._context.get('date_run', today)
            date_run = datetime.strptime(rec.date_run, DATETIME_FORMAT)
            date_maturity = datetime.strptime(rec.date_maturity,
                                              DATETIME_FORMAT)
            delta = date_run - date_maturity
            rec.days_overdue = delta.days

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)

        _sql = """
            select aml.id, aml.id as move_line_id, date_maturity,
            aml.org_id, aml.partner_id
            from account_move_line aml
            join account_account aa on aa.id = aml.account_id
            where aml.state = 'valid' and aa.type = 'receivable'
            and aml.date_maturity is not null
        """

        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, _sql,))
