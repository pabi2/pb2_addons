# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

IMPORT_ACTION = {
    'model': 'budget.breakdown',
    'header_map': {  # Must be lowercase
        'id': 'id',
        'name': 'name',
        'org': 'org_id',
        'fiscal year': 'fiscalyear_id',
        'revision': 'revision',
        'planned overall': 'planned_amount',
        'budget policy': 'new_policy_amount',
        'diff amount': 'policy_diff',
        'section': 'unit_base_line_ids/section_id',
        'planned amount': 'unit_base_line_ids/planned_amount',
        'consumed': 'unit_base_line_ids/past_consumed',
        'rolling': 'unit_base_line_ids/rolling',
        'latest policy amount': 'unit_base_line_ids/latest_policy_amount',
        'policy amount': 'unit_base_line_ids/policy_amount',
    },
    'extra_columns': [],
}


class BudgetBreakdownActionExcelImportWizard(models.TransientModel):
    _name = 'budget.breakdown.action.excel.import.wizard'

    import_file = fields.Binary(
        string='Import File (*.xls)',
        required=True,
    )

    @api.multi
    def action_import_xls(self):
        self.ensure_one()
        if not self.import_file:
            raise ValidationError(_('Please choose excel file to import!'))
        model = IMPORT_ACTION['model']
        header_map = IMPORT_ACTION.get('header_map', False)
        extra_columns = IMPORT_ACTION.get('extra_columns', False)
        return self.env['pabi.xls'].import_xls(model, self.import_file,
                                               header_map=header_map,
                                               extra_columns=extra_columns)
