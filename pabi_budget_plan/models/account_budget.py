# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.tools.float_utils import float_compare
from openerp.exceptions import ValidationError


class AccountBudget(models.Model):
    _inherit = 'account.budget'
    _order = 'create_date desc'

    policy_amount = fields.Float(
        string='Policy Amount',
        readonly=True,
    )
    remarks = fields.Text(
        compute='_compute_remarks',
        reaonly=True,
        size=1000,
    )

    @api.multi
    def _compute_remarks(self):
        for rec in self:
            # Rolling > Released
            if float_compare(rec.rolling, rec.released_amount, 2) == 1:
                rolling = '{:,.2f}'.format(rec.rolling)
                diff = '{:,.2f}'.format(rec.rolling - rec.released_amount)
                rec.remarks = _('Rolling Amount: %s\n'
                                'Rolling > Released = %s') % (rolling, diff)
            # Rolling < Released
            if float_compare(rec.rolling, rec.released_amount, 2) == -1:
                rolling = '{:,.2f}'.format(rec.rolling)
                diff = '{:,.2f}'.format(rec.released_amount - rec.rolling)
                rec.remarks = _('Rolling Amount: %s\n'
                                'Rolling < Released = %s') % (rolling, diff)

    @api.multi
    def _get_doc_number(self):
        self.ensure_one()
        _prefix = 'CTRL'
        _prefix2 = {'unit_base': 'UNIT',
                    'invest_asset': 'ASSET',
                    'project_base': 'PROJ',
                    'invest_construction': 'CONST',
                    'personnel': 'PERSONNEL'}
        _prefix3 = {'unit_base': 'section_id',
                    'invest_asset': 'org_id',
                    'project_base': 'program_id',
                    'invest_construction': 'org_id',
                    'personnel': False}
        prefix2 = _prefix2[self.chart_view]
        prefix3 = 'NSTDA'
        if _prefix3[self.chart_view]:
            obj = self[_prefix3[self.chart_view]]
            prefix3 = obj.code or obj.name_short or obj.name
        name = '%s/%s/%s/%s' % (_prefix, prefix2,
                                self.fiscalyear_id.code, prefix3)
        return name

    @api.model
    def create(self, vals):
        budget = super(AccountBudget, self).create(vals)
        budget_level = budget.budget_level_id
        if budget_level.budget_release == 'manual_header' and \
                budget_level.release_follow_policy and \
                'policy_amount' in vals:
            vals['to_release_amount'] = vals['policy_amount']
            budget.write(vals)
        # Numbering
        budget.name = budget._get_doc_number()
        # --
        return budget

    @api.multi
    def write(self, vals):
        if 'policy_amount' in vals:
            for budget in self:
                budget_level = budget.budget_level_id
                if budget_level.budget_release == 'manual_header' and \
                        budget_level.release_follow_policy:
                    vals['to_release_amount'] = vals['policy_amount']
                super(AccountBudget, budget).write(vals)
        else:
            super(AccountBudget, self).write(vals)
        for rec in self:
            # Name
            if rec.name != rec._get_doc_number():
                rec._write({'name': rec._get_doc_number()})
            # If there is policy amount, some fields can't be changed.
            if rec.policy_amount:
                no_edit_fields = ['section_id', 'fiscalyear_id']
                if set(no_edit_fields) & set(vals.keys()):
                    raise ValidationError(
                        _('With policy amount, fields edit not allow for: %s')
                        % ', '.join(no_edit_fields))
        return True

    @api.multi
    @api.constrains('chart_view', 'fiscalyear_id', 'section_id', 'program_id',
                    'org_id', 'personnel_costcenter_id')
    def _check_fiscalyear_section_unique(self):
        for budget in self:
            budget = self.search(
                [('chart_view', '=', budget.chart_view),
                 ('fiscalyear_id', '=', budget.fiscalyear_id.id),
                 ('section_id', '=', budget.section_id.id),
                 ('program_id', '=', budget.program_id.id),
                 ('org_id', '=', budget.org_id.id),
                 ('personnel_costcenter_id', '=',
                  budget.personnel_costcenter_id.id),
                 ])
            if len(budget) > 1:
                raise ValidationError(
                    _('Duplicated budget on the same fiscal year!'))

    @api.multi
    def unlink(self):
        for policy in self:
            if policy.state not in ('draft', 'cancel'):
                raise ValidationError(
                    _('Cannot delete budget(s)\
                    which are not in draft or cancelled.'))
        return super(AccountBudget, self).unlink()

    @api.model
    def generate_project_base_controls(self, fiscalyear_id=None):
        if not fiscalyear_id:
            raise ValidationError(_('No fiscal year provided!'))
        fiscal = self.env['account.fiscalyear'].browse(fiscalyear_id)
        # Find existing controls, and exclude them
        controls = self.search([('fiscalyear_id', '=', fiscalyear_id),
                                ('chart_view', '=', 'project_base')])
        _ids = controls.mapped('program_id')._ids
        # Find Programs
        programs = self.env['res.program'].search([('id', 'not in', _ids),
                                                   ('special', '=', False)])
        control_ids = []
        for program in programs:
            control = self.create({'chart_view': 'project_base',
                                   'fiscalyear_id': fiscalyear_id,
                                   'date_from': fiscal.date_start,
                                   'date_to': fiscal.date_stop,
                                   'program_id': program.id, })
            control_ids.append(control.id)
        return control_ids

    @api.model
    def generate_invest_construction_controls(self, fiscalyear_id=None):
        if not fiscalyear_id:
            raise ValidationError(_('No fiscal year provided!'))
        fiscal = self.env['account.fiscalyear'].browse(fiscalyear_id)
        # Find existing controls, and exclude them
        controls = self.search([('fiscalyear_id', '=', fiscalyear_id),
                                ('chart_view', '=', 'invest_construction')])
        _ids = controls.mapped('org_id')._ids
        # Find orgs
        orgs = self.env['res.org'].search([('id', 'not in', _ids),
                                           ('special', '=', False)])
        control_ids = []
        for org in orgs:
            control = self.create({'chart_view': 'invest_construction',
                                   'fiscalyear_id': fiscalyear_id,
                                   'date_from': fiscal.date_start,
                                   'date_to': fiscal.date_stop,
                                   'org_id': org.id,
                                   'user_id': False})
            control_ids.append(control.id)
        return control_ids

    @api.multi
    def budget_done(self):
        # For Invest Asset, activation will set code for all assets
        for rec in self:
            assets = \
                rec.budget_expense_line_invest_asset.mapped('invest_asset_id')
            assets.with_context(
                {'fiscalyear_id': rec.fiscalyear_id.id}).generate_code()
        return super(AccountBudget, self).budget_done()


class AccountBudgetLine(models.Model):
    _inherit = 'account.budget.line'

    # Chart Fields
    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        domain="[('invest_construction_id', '=', invest_construction_id)]",
    )

    @api.onchange('invest_construction_id')
    def _onchange_invest_construction_id(self):
        self.invest_construction_phase_id = False

    @api.model
    def create(self, vals):
        """ Assign default AG for some Budget Type """
        rec = super(AccountBudgetLine, self).create(vals)
        if not rec.activity_group_id:
            ag_dict = {
                'unit_base': 'default_ag_unit_base_id',
                'invest_asset': 'default_ag_invest_asset_id',
                'invest_construction': 'default_ag_invest_construction_id',
            }
            company = self.env.user.company_id
            ag_field = ag_dict.get(rec.budget_id.chart_view, False)
            if ag_field:
                rec.activity_group_id = company[ag_field]
        if not rec.fund_id:
            rec.fund_id = self.env.ref('base.fund_nstda', False)
        return rec

    @api.multi
    def _filter_line_to_release(self):
        """ HOOK for use with charge_type = internal/external """
        budget_lines = super(AccountBudgetLine, self)._filter_line_to_release()
        lines = budget_lines.filtered(lambda l: l.charge_type == 'external')
        if not lines:
            raise ValidationError(
                _('No external expense lines for release amount'))
        return lines
