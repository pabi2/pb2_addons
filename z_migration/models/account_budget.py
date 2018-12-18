# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.exceptions import ValidationError


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    @api.multi
    def mork_budget_done(self):
        self.budget_done()
        return True

    @api.model
    def mock_update_related_dimension(self, model, res_id,
                                      analytic_field, dimensions):
        line = self.env[model].browse(res_id)

        # get new dimension id
        def new_obj_id(code, field, model):
            new_code = dimensions.get(field, {}).get(code, False)
            new_obj = \
                self.env[model].search([('code', '=', new_code)]) or False
            return new_obj.id

        Analytic = self.env['account.analytic.account']
        # update to new dimension
        vals = {}
        if line.section_id:
            vals['section_id'] = new_obj_id(line.section_id.code,
                                            'section_id',
                                            'res.section')
        elif line.project_id:
            vals['project_id'] = new_obj_id(line.project_id.code,
                                            'project_id',
                                            'res.project')
        elif line.invest_asset_id:
            vals['invest_asset_id'] = new_obj_id(line.invest_asset_id.code,
                                                 'invest_asset_id',
                                                 'res.invest.asset')
        elif line.invest_construction_phase_id:
            vals['invest_construction_phase_id'] = new_obj_id(
                line.invest_construction_phase_id.code,
                'invest_construction_phase_id',
                'res.invest.construction.phase')
        elif line.personnel_costcenter_id:
            vals['personnel_costcenter_id'] = new_obj_id(
                line.personnel_costcenter_id.code,
                'personnel_costcenter_id', 'res.personnel.costcenter')
        else:
            raise ValidationError('New dimension not found!')
        # do the job
        line.write(vals)
        line.update_related_dimension(vals)
        analytic = Analytic.create_matched_analytic(line)
        line.write({analytic_field: analytic.id})
        return True
