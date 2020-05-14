# -*- coding: utf-8 -*-
import ast
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class CreateJournalEntryWizard(models.TransientModel):
    _name = 'create.journal.entry.wizard'

    type = fields.Selection(
        [('budget', 'Adjust Budget (JV)'),
         ('no_budget', 'Adjust No-Budget (JN)')],
        string='Type of Adjustment',
        required=True,
        readonly=False,
        default='no_budget',
    )
    use_finlease_model = fields.Boolean(
        string='Use Finlease Model',
        default=False,
    )
    model_id = fields.Many2one(
        'account.model',
        string='Model',
        domain=[('special_type', '=', 'invoice_plan_fin_lease')],
    )

    @api.model
    def view_init(self, fields_list):
        invoice_id = self._context.get('active_id')
        invoice = self.env['hr.salary.expense'].browse(invoice_id)
        if invoice.state not in ('open', 'paid'):
            raise ValidationError(
                _('Only open invoice allowed!'))
        # if invoice.adjust_move_id:
        #     raise ValidationError(
        #         _('The adjustmnet journal entry already created!'))

    @api.multi
    def create_journal_entry(self):
        self.ensure_one()
        TYPES = {
            'budget': {'action': 'pabi_account_move_adjustment.'
                                 'action_journal_adjust_budget',
                       'view': 'pabi_account_move_adjustment.'
                               'view_journal_adjust_budget_form'},
            'no_budget': {'action': 'pabi_account_move_adjustment.'
                                    'action_journal_adjust_no_budget',
                          'view': 'pabi_account_move_adjustment.'
                                  'view_journal_adjust_no_budget_form'},
        }
        action = self.env.ref(TYPES[self.type]['action'])
        view = self.env.ref(TYPES[self.type]['view'])
        result = action.read()[0]
        result.update({'view_mode': 'form',
                       'target': 'current',
                       'view_id': view.id,
                       'view_ids': False,
                       'views': False})
        ctx = ast.literal_eval(result['context'])
        invoice_id = self._context.get('active_id')
        invoice = self.env['hr.salary.expense'].browse(invoice_id)
        ctx.update({'default_ref': invoice.number,
                    'src_invoice_id': invoice.id})
        # If use fin lease model
        if self.use_finlease_model and self.model_id:
            invline = invoice.invoice_line and invoice.invoice_line[0]
            chartfield = invline and invline.chartfield_id
            # --
            section_id = False
            project_id = False
            invest_construction_phase_id = False
            invest_asset_id = False
            personnel_costcenter_id = False
            res_id = chartfield and chartfield.res_id
            if chartfield.model == 'res.section':
                section_id = res_id
            elif chartfield.model == 'res.project':
                project_id = res_id
            elif chartfield.model == 'res.invest.construction.phase':
                invest_construction_phase_id = res_id
            elif chartfield.model == 'res.invest.asset':
                invest_asset_id = res_id
            elif chartfield.model == 'res.personnel.costcenter':
                personnel_costcenter_id = res_id
            # --
            Section = self.env['res.section']
            Project = self.env['res.project']
            ConstructionPhase = self.env['res.invest.construction.phase']
            InvestAsset = self.env['res.invest.asset']
            Personnel = self.env['res.personnel.costcenter']
            fund_id = False
            funds = []
            if section_id:
                funds = Section.browse(section_id).fund_ids
            elif project_id:
                funds = Project.browse(project_id).fund_ids
            elif invest_construction_phase_id:
                funds = ConstructionPhase.browse(
                    invest_construction_phase_id).fund_ids
            elif invest_asset_id:
                funds = InvestAsset.browse(invest_asset_id).fund_ids
            elif personnel_costcenter_id:
                funds = Personnel.browse(personnel_costcenter_id).fund_ids
            # Get default fund
            if len(funds) == 1:
                fund_id = funds[0].id
            else:
                fund_id = False
            # --
            move_lines = [
                {'account_id': self.model_id.debit_account_id.id,
                 'debit': invoice.amount_untaxed,
                 'name': invline and invline.name,
                 'chartfield_id': chartfield and chartfield.id,
                 'costcenter_id': chartfield and chartfield.costcenter_id.id,
                 'section_id': section_id,
                 'project_id': project_id,
                 'invest_construction_phase_id': invest_construction_phase_id,
                 'invest_asset_id': invest_asset_id,
                 'personnel_costcenter_id': personnel_costcenter_id,
                 'fund_id': fund_id},
                {'account_id': self.model_id.credit_account_id.id,
                 'credit': invoice.amount_untaxed,
                 'name': invline and invline.name,
                 'chartfield_id': chartfield and chartfield.id,
                 'costcenter_id': chartfield and chartfield.costcenter_id.id,
                 'section_id': section_id,
                 'project_id': project_id,
                 'invest_construction_phase_id': invest_construction_phase_id,
                 'invest_asset_id': invest_asset_id,
                 'personnel_costcenter_id': personnel_costcenter_id,
                 'fund_id': fund_id},
            ]
            if self.model_id.fin_debit_account_id:
                move_lines.append({
                    'account_id': self.model_id.fin_debit_account_id.id,
                    'debit': invoice.amount_untaxed,
                    'name': invline and invline.name,
                    'chartfield_id': chartfield and chartfield.id,
                    'costcenter_id':
                        chartfield and chartfield.costcenter_id.id,
                    'section_id': section_id,
                    'project_id': project_id,
                    'invest_construction_phase_id':
                        invest_construction_phase_id,
                    'invest_asset_id': invest_asset_id,
                    'personnel_costcenter_id': personnel_costcenter_id,
                    'fund_id': fund_id})
            if self.model_id.fin_credit_account_id:
                move_lines.append({
                    'account_id': self.model_id.fin_credit_account_id.id,
                    'credit': invoice.amount_untaxed,
                    'name': invline and invline.name,
                    'chartfield_id': chartfield and chartfield.id,
                    'costcenter_id':
                        chartfield and chartfield.costcenter_id.id,
                    'section_id': section_id,
                    'project_id': project_id,
                    'invest_construction_phase_id':
                        invest_construction_phase_id,
                    'invest_asset_id': invest_asset_id,
                    'personnel_costcenter_id': personnel_costcenter_id,
                    'fund_id': fund_id})
            ctx.update({'default_line_id': move_lines})
        # --
        result['context'] = ctx
        return result
