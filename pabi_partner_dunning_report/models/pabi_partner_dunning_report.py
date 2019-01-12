# -*- coding: utf-8 -*-
import psycopg2
from datetime import datetime
from openerp import models, fields, api
from openerp import tools

OVERDUE_DAYS = {'l1': 7, 'l2': 14, 'l3': 19}


class PABIPartnerDunningReport(models.Model):
    _name = 'pabi.partner.dunning.report'
    _order = 'partner_id, date_maturity desc'
    _auto = False

    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item',
        readonly=True,
    )
    amount_residual = fields.Float(
        # related='move_line_id.amount_residual',
        compute='_compute_amount_residual',
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
        string='Reconcile',
        readonly=True,
    )
    date_maturity = fields.Date(
        string='Due Date',
        readonly=True,
    )
    date = fields.Date(
        string='Date',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )
    category_id = fields.Many2one(
        'res.partner.category',
        string='Partner Category',
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
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        readonly=True,
    )
    validate_user_id = fields.Many2one(
        'res.users',
        # compute='_compute_validate_user_id',
        string='Validator',
        readonly=True,
    )
    l1 = fields.Boolean(
        string='#1',
        readonly=True,
        help="Letter 1 (7 days) has been created",
    )
    l1_date = fields.Date(
        string='#1 Date'
    )
    l2 = fields.Boolean(
        string='#2',
        readonly=True,
        help="Letter 2 (14 days) has been created",
    )
    l2_date = fields.Date(
        string='#2 Date'
    )
    l3 = fields.Boolean(
        string='#3',
        readonly=True,
        help="Letter 3 (19 days) has been created",
    )
    l3_date = fields.Date(
        string='#3 Date'
    )

    @api.multi
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

    @api.multi
    def _compute_amount_residual(self):
        for rec in self:
            move_line = rec.move_line_id
            sign = move_line.debit - move_line.credit < 0 and -1 or 1
            rec.amount_residual = sign * abs(move_line.amount_residual)

    def init(self, cr):
        try:
            with cr.savepoint():
                cr.execute("CREATE EXTENSION tablefunc")
        except psycopg2.Error:
            pass
        cr.commit()
        # View
        tools.drop_view_if_exists(cr, self._table)
        _sql = """
            select case when split_part(am.document_id, ',', 1) =
                'interface.account.entry' then
                (select validate_user_id from interface_account_entry where
                 id = split_part(am.document_id, ',', 2) :: int) else
                 am.create_uid end as validate_user_id, aml.id,
                aml.id as move_line_id, aml.reconcile_id as reconcile_id,
                aml.date_maturity, aml.date, aml.partner_id, rp.category_id,
                aa.type account_type, aa.id account_id, new_title,
                case when letter.l1 is not null then true else false end as l1,
                letter.l1 l1_date,
                case when letter.l2 is not null then true else false end as l2,
                letter.l2 l2_date,
                case when letter.l3 is not null then true else false end as l3,
                letter.l3 l3_date
            from account_move_line aml
            join account_move am on aml.move_id = am.id
            join account_account aa on aa.id = aml.account_id
            join res_partner rp on rp.id = aml.partner_id
            left outer join pabi_dunning_config_title pdct
                on rp.title = pdct.title_id
            -- Crosstab table
            left outer join (
                select move_line_id, l1, l2, l3
                from crosstab('
                select move_line_id, letter_type, date_run
                from pabi_partner_dunning_letter_line order by 1, 2
                ') AS final_result(
                    move_line_id integer, l1 date, l2 date, l3 date)
            )as letter on letter.move_line_id = aml.id
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

    @api.model
    def _new_title(self, title):
        company = self.env['res.company'].search([])[0]
        titles = company.title_ids.filtered(lambda l: l.title_id == title)
        return titles and titles[0].new_title or False

    @api.multi
    def _create_dunning_letter(self, letter_type):
        # Sorting first
        dunnings = self.sorted(key=lambda a: (a.partner_id, a.date))
        # Create 1 letter for 1 parnter + multiple lines
        partners = dunnings.mapped('partner_id')
        for partner in partners:
            dunning_lines = []
            partner_dunnings = dunnings.filtered(lambda l:
                                                 l.partner_id == partner)
            for partner_dunning in partner_dunnings:
                line = {'move_line_id': partner_dunning.move_line_id.id}
                dunning_lines.append((0, 0, line))
            dunning_letter = {'letter_type': letter_type,
                              'partner_id': partner.id,
                              'date_run': fields.Date.context_today(self),
                              'to_whom_title': self._new_title(partner.title),
                              'line_ids': dunning_lines,
                              }
            self.env['pabi.partner.dunning.letter'].create(dunning_letter)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(PABIPartnerDunningReport, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        if 'amount_residual' in fields:
            for line in res:
                if '__domain' in line:
                    line['amount_residual'] = \
                        sum(self.search(line['__domain'])
                            .mapped('amount_residual'))
        return res


class PABIPartnerDunningPrintHistory(models.Model):
    _name = 'pabi.partner.dunning.print.history'

    dunning_id = fields.Many2one(
        'pabi.partner.dunning.report',
        string='Dunning',
    )
    report_type = fields.Selection(
        [('l1', 'Overdue 7 Days'),
         ('l2', 'Overdue 14 Days'),
         ('l3', 'Overdue 19 Days')],
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
