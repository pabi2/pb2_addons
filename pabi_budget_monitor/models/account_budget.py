# -*- coding: utf-8 -*-
from openerp import models, api, _, fields
from openerp.exceptions import ValidationError


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    BUDGET_LEVEL = {
        # Code not cover Activity level yet
        # 'activity_group_id': 'Activity Group',
        # 'activity_id': 'Activity',
        # Fund
        'fund_id': 'Fund (for all)',
        # Project Based
        'spa_id': 'SPA',
        'mission_id': 'Mission',
        'functional_area_id': 'Functional Area',
        'program_group_id': 'Program Group',
        'program_id': 'Program',
        'project_group_id': 'Project Group',
        'project_id': 'Project',
        # Unit Based
        'org_id': 'Org',
        'sector_id': 'Sector',
        'subsector_id': 'Subsector',
        'division_id': 'Division',
        'section_id': 'Section',
        'costcenter_id': 'Costcenter',
        # Personnel
        'personnel_costcenter_id': 'Personnel Budget',
        # Investment
        # - Asset
        # 'invest_asset_categ_id': 'Invest. Asset Category',  # (not dimension)
        'invest_asset_id': 'Invest. Asset',
        # - Construction
        'invest_construct_id': 'Construction',
        'invest_construction_phase_id': 'Construction Phase',
    }

    BUDGET_LEVEL_MODEL = {
        # Code not cover Activity level yet
        # 'activity_group_id': 'account.activity.group',
        # 'activity_id': 'Activity'  # No Activity Level{
        'fund_id': 'res.fund',

        'spa_id': 'res.spa',
        'mission_id': 'res.mission',
        'tag_type_id': 'res.tag.type',
        'tag_id': 'res.tag',
        # Project Based
        'functional_area_id': 'res.functional.area',
        'program_group_id': 'res.program.group',
        'program_id': 'res.program',
        'project_group_id': 'res.project.group',
        'project_id': 'res.project',
        # Unit Based
        'org_id': 'res.org',
        'sector_id': 'res.sector',
        'subsector_id': 'res.subsector',
        'division_id': 'res.division',
        'section_id': 'res.section',
        'costcenter_id': 'res.costcenter',
        # Personnel
        'personnel_costcenter_id': 'res.personnel.costceter',
        # Investment
        # - Asset
        # 'invest_asset_categ_id': 'res.invest.asset.category',
        'invest_asset_id': 'res.invest.asset',
        # - Construction
        'invest_construction_id': 'res.invest.construction',
        'invest_construction_phase_id': 'res.invest.construction.phase',
    }

    BUDGET_LEVEL_TYPE = {
        'project_base': 'Project Based',
        'unit_base': 'Unit Based',
        'personnel': 'Personnel',
        'invest_asset': 'Investment Asset',
        'invest_construction': 'Investment Construction',
    }

    @api.multi
    def _validate_budget_level(self, budget_type='check_budget'):
        for rec in self:
            budget_type = rec.chart_view
            super(AccountBudget, rec)._validate_budget_level(budget_type)

    @api.model
    def _get_budget_monitor(self, fiscal, budget_type,
                            budget_level, resource,
                            ext_field=False,
                            ext_res_id=False):
        # For funding level, we go deeper
        if budget_level == 'fund_id':
            budget_type_dict = {
                'unit_base': 'monitor_section_ids',
                'project_base': 'monitor_project_ids',
                'personnel': 'monitor_personnel_costcenter_ids',
                'invest_asset': 'monitor_invest_asset_ids',
                'invest_construction':
                'monitor_invest_construction_phase_ids'}
            return resource[budget_type_dict[budget_type]].\
                filtered(lambda x:
                         (x.fiscalyear_id == fiscal and
                          x[ext_field].id == ext_res_id))
            raise ValidationError(
                _('Budget Check at Fund level require a compliment dimension'))
        else:
            return super(AccountBudget, self).\
                _get_budget_monitor(fiscal, budget_type,
                                    budget_level, resource)

#     @api.model
#     def get_document_query(self, head_table, line_table):
#         query = """
#             select %(sel_fields)s,
#                 coalesce(sum(l.price_subtotal), 0.0) amount
#             from """ + line_table + """ l
#             join """ + head_table + """ h on h.id = l.invoice_id
#             where h.id = %(active_id)s
#             group by %(sel_fields)s
#         """
#         return query


#     @api.model
#     def get_fiscal_and_budget_level(self, budget_date=False):
#         if not budget_date:
#             budget_date = fields.Date.context_today(self)
#         Fiscal = self.env['account.fiscalyear']
#         fiscal_id = Fiscal.find(budget_date)
#         res = {'fiscal_id': fiscal_id}
#         for level in Fiscal.browse(fiscal_id).budget_level_ids:
#             res[level.type] = level.budget_level
#         return res

    @api.model
    def _get_doc_field_combination(self, doc_lines, args):
        combinations = []
        for l in doc_lines:
            val = ()
            for f in args:
                val += (l[f],)
            if False not in val:
                combinations.append(val)
        return combinations

    @api.model
    def document_check_budget(self, doc_date, doc_lines, amount_field):
        res = {'budget_ok': True,
               'message': False}
        Budget = self.env['account.budget']
        budget_level_info = Budget.get_fiscal_and_budget_level(doc_date)
        if False in budget_level_info.values():
            raise ValidationError(_('Budget level is not set!'))
        fiscal_id = budget_level_info['fiscal_id']
        # Check for all budget types
        for budget_type in dict(Budget.BUDGET_LEVEL_TYPE).keys():
            if budget_type not in budget_level_info:
                raise ValidationError(_('Budget level is not set!'))
            budget_level = budget_level_info[budget_type]
            sel_fields = [budget_level]
            if budget_level == 'fund_id':
                budget_type_dict = {
                    'unit_base': 'section_id',
                    'project_base': 'project_id',
                    'personnel': 'personnel_costcenter_id',
                    'invest_asset': 'investment_asset_id',
                    'invest_construction': 'invest_construction_phase_id'}
                sel_fields.append(budget_type_dict[budget_type])
            group_vals = self._get_doc_field_combination(doc_lines, sel_fields)
            for val in group_vals:
                res_id = val[0]
                ext_field = False
                ext_res_id = False
                if not res_id:
                    continue
                filtered_lines = doc_lines
                i = 0
                for f in sel_fields:
                    filtered_lines = filter(lambda l:
                                            f in l and l[f] and l[f] == val[i],
                                            filtered_lines)
                    i += 1
                amount = sum(map(lambda l: l[amount_field], filtered_lines))
                # For funding case, add more dimension
                if len(sel_fields) == 2:
                    ext_res_id = val[1]
                    ext_field = sel_fields[1]
                res = Budget.check_budget(fiscal_id,
                                          budget_type,  # eg, project_base
                                          budget_level,  # eg, project_id
                                          res_id,
                                          amount,
                                          ext_field=ext_field,
                                          ext_res_id=ext_res_id)
                if not res['budget_ok']:
                    return res
        return res

class AccountBudgetLine(models.Model):
    _inherit = 'account.budget.line'

    @api.depends(
        'budget_id.section_id',
        'section_id',
        'section_id.rpt_program_id',
        'project_id',
        'project_id.rpt_program_id')
    def _compute_rpt_program_id(self):
        for line in self:
            if line.budget_id.chart_view == 'unit_base':
                if line.section_id:
                    line.rpt_program_id = line.section_id.rpt_program_id
            elif line.budget_id.chart_view == 'project_base':
                if line.project_id:
                    line.rpt_program_id = line.project_id.rpt_program_id

    rpt_program_id = fields.Many2one(
        'res.program',
        compute='_compute_rpt_program_id',
        string='Report Program',
        store=True,
    )
    