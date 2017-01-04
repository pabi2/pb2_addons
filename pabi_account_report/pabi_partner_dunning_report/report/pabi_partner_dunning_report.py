# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api
from openerp import tools


class PABIPartnerDunningReport(models.Model):
    _name = 'pabi.partner.dunning.report'
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
        string='Partner',
    )
    date_run = fields.Date(
        string='Runing Date',
        compute='_compute_date',
    )
    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_date',
    )
    account_type = fields.Selection(
        [('payable', 'Payable'),
         ('receivable', 'Receivable')],
        string='Account Type',
    )
    print_ids = fields.One2many(
        'pabi.partner.dunning.print.history',
        'dunning_id',
        string='Print History',
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
            aml.org_id, aml.partner_id, aa.type account_type
            from account_move_line aml
            join account_account aa on aa.id = aml.account_id
            where aml.state = 'valid' and aa.type in ('receivable', 'payable')
            and aml.date_maturity is not null
        """

        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, _sql,))

    @api.multi
    def _create_print_history(self, report_type):
        PrintHistory = self.env['pabi.partner.dunning.print.history']
        for dunning in self:
            PrintHistory.create({
                'dunning_id': dunning.id,
                'report_type': report_type,
            })
        return


class PABIPartnerDunningPrintHistory(models.Model):
    _name = 'pabi.partner.dunning.print.history'

    dunning_id = fields.Many2one(
        'pabi.partner.dunning.report',
        string='Dunning',
    )
    report_type = fields.Selection(
        [('7', 'Overdue 7 Days'),
         ('14', 'Overdue 14 Days'),
         ('19', 'Overdue 19 Days')],
        string='Type',
        readonly=True,
        required=True,
    )
    create_date = fields.Datetime(
        string='Printed Date',
        readonly=True,
        required=True,
    )
    create_uid = fields.Many2one(
        'res.users',
        string='Printed By',
        readonly=True,
        required=True,
    )

    @api.multi
    def name_get(self):
        result = []
        for history in self:
            result.append((history.id, "(%s) %s" %
                          (history.report_type, history.date_print)))
        return result
