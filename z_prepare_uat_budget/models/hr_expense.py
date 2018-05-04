# -*- coding: utf-8 -*-
from openerp import api, models
from openerp.exceptions import ValidationError


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def prepare_data(self, action, datas=False):
        action_list = ['copy_ex_with_new_section']
        # Sample for action = copy_ex_with_new_section
        # For ศก
        sample_datas = {
            'copy_ex_with_new_section': {
                'EX18000216': ['105068', '105056', '102002', '102001',
                               '103014', '105064', '104008', '105070'],
                'EX18000218': ['305017', '305013', '302007', '301074',
                               '305007', '302005'],
                'EX18000219': ['405021', '405006'],
                'EX18000220': ['205006', '201051', '201003'],
                'EX18000221': ['605008', '605016', '601012',
                               '105015', '105017', '105014']
            }
        }

        if action not in action_list:
            raise ValidationError('%s is not a valid action')

        if not datas:
            datas = sample_datas[action]

        for ex in datas.keys():
            expense = self.search([('number', '=', ex)])
            if not expense:
                raise ValidationError('%s not found' % ex)
            for s in datas[ex]:
                section = self.env['res.section'].search([('code', '=', s)])
                expense.with_context(new_section_id=section.id).copy()


class HRExpenseLine(models.Model):
    _inherit = 'hr.expense.line'

    @api.model
    def create(self, vals):
        if self._context.get('new_section_id', False):
            vals['section_id'] = self._context.get('new_section_id')
        return super(HRExpenseLine, self).create(vals)
