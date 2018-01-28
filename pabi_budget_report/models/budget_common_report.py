from openerp import fields


class BudgetCommonReport(object):

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
    )
    date_stop = fields.Date(
        string='End of Period',
        readonly=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        readonly=True,
    )
    chart_view = fields.Selection(
        [('personnel', 'Personnel'),
         ('invest_asset', 'Investment Asset'),
         ('unit_base', 'Unit Based'),
         ('project_base', 'Project Based'),
         ('invest_construction', 'Investment Construction')],
        string='Budget View',
        readonly=True,
    )
    budget_id = fields.Reference(
        [('res.section', 'Section'),
         ('res.project', 'Project'),
         ('res.invest.asset', 'Investment Asset'),
         ('res.invest.construction', 'Investment Construction'),
         ('res.personnel.costcenter', 'Personnel and Welfare')],
        string='Budget Structure',
        readonly=True,
    )
    planned_amount = fields.Float(
        string='Budget Control',
        readonly=True,
    )
    released_amount = fields.Float(
        string='Budget Release',
        readonly=True,
    )
    amount_exp_commit = fields.Float(
        string='EX',
        readonly=True,
    )
    amount_pr_commit = fields.Float(
        string='PR',
        readonly=True,
    )
    amount_po_commit = fields.Float(
        string='PO',
        readonly=True,
    )
    amount_actual = fields.Float(
        string='Actual',
        readonly=True,
    )
