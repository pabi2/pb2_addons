from openerp import models, fields, tools


class Common(object):

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    account_code = fields.Char(
        string='Account Code',
        readonly=True,
    )
    account_name = fields.Char(
        string='Account Name',
        readonly=True,
    )
    initial = fields.Float(
        string='Initial',
        readonly=True,
    )
    debit = fields.Float(
        string='Debit',
        readonly=True,
    )
    credit = fields.Float(
        string='Credit',
        readonly=True,
    )
    balance = fields.Float(
        string='Balance',
        readonly=True,
    )
    final_balance = fields.Float(
        string='Current Balance',
        readonly=True,
    )
    report_id = fields.Many2one(
        'account.trial.balance.report',
        string='Report',
        readonly=True,
    )

    def _get_sql_query(self, template_name):
        sql = \
            """
            SELECT ROW_NUMBER() OVER (ORDER BY l.report_id, m.out_value) AS ID,
                   SPLIT_PART(m.out_value, ' - ', 1) AS account_code,
                   SPLIT_PART(m.out_value, ' - ', 2) AS account_name,
                   SUM(l.initial) AS initial,
                   SUM(l.debit) AS debit,
                   SUM(l.credit) AS credit,
                   SUM(l.balance) AS balance,
                   SUM(l.final_balance) AS final_balance,
                   l.report_id
            FROM account_trial_balance_line l
            LEFT JOIN account_account a ON l.account_id = a.id
            LEFT JOIN pabi_data_map m ON a.code = m.in_value
            LEFT JOIN pabi_data_map_type t ON m.map_type_id = t.id
            WHERE t.app_name = 'tb_external' AND t.name = '%s'
            GROUP BY l.report_id, m.out_value
            ORDER BY l.report_id, m.out_value
            """ % (template_name, )
        return sql


class AccountTrialBalanceReport(models.Model):
    _inherit = 'account.trial.balance.report'

    gfmis_line_ids = fields.One2many(
        'gfmis.account.trial.balance.line',
        'report_id',
        string='Details',
    )
    cfo_line_ids = fields.One2many(
        'cfo.account.trial.balance.line',
        'report_id',
        string='Details',
    )


class GFMISAccountTrialBalanceLine(models.Model, Common):
    _name = 'gfmis.account.trial.balance.line'
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_query('GFMIS Report')))


class CFOAccountTrialBalanceLine(models.Model, Common):
    _name = 'cfo.account.trial.balance.line'
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_query('CFO Report')))
