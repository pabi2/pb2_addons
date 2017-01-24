# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api
from openerp import tools


class PABIPartnerDunningReport(models.Model):
    _name = 'pabi.partner.dunning.report'
    _order = 'partner_id, move_line_id'
    _auto = False

    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item',
        readonly=True,
    )
    amount_residual = fields.Float(
        related='move_line_id.amount_residual',
        string='Balance',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        related='move_line_id.invoice',
        string='Invoice',
        readonly=True,
    )
    reconcile_id = fields.Many2one(
        'account.move.reconcile',
        related='move_line_id.reconcile_id',
        string='Reconcile',
        readonly=True,
    )
    date_maturity = fields.Date(
        string='Due Date',
        readonly=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )
    new_title = fields.Char(
        string='New Title',
        readonly=True,
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
        readonly=True,
    )
    print_ids = fields.One2many(
        'pabi.partner.dunning.print.history',
        'dunning_id',
        string='Print History',
    )

    # @api.model
    # def fields_view_get(self, view_id=None, view_type=False,
    #                     toolbar=False, submenu=False):
    #     res = super(PABIPartnerDunningReport, self).\
    #         fields_view_get(view_id=view_id, view_type=view_type,
    #                         toolbar=toolbar, submenu=submenu)
    #     # Passing context to action on tree view
    #     actions = res.get('toolbar', {}).get('action', {})
    #     for action in actions:
    #         # if action.get('context', False):
    #         #     context = ast.literal_eval(action['context'])
    #         #     context.update(
    #         #         {'date_run': self._context.get('date_run', False)})
    #         action['context'] = {'date_run': self._context.get('date_run', False)}
    #     # res['context'] = {'date_run': self._context.get('date_run', False)}
    #     print res
    #     return res

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
            aml.org_id, aml.partner_id, aa.type account_type, new_title
            from account_move_line aml
            join account_account aa on aa.id = aml.account_id
            join res_partner rp on rp.id = aml.partner_id
            left outer join pabi_dunning_config_title pdct
                on rp.title = pdct.title_id
            where aml.state = 'valid' and aa.type in ('receivable', 'payable')
            and aml.date_maturity is not null
            and aml.partner_id is not null
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
