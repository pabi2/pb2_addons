# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

IMPORT_ACTION = {
    'budget_breakdown_line': {
        'model': 'budget.breakdown.line',
        'header_map': {
            'id': 'id',
            'policy amount': 'policy_amount'
        },
        'extra_columns': [],
    }
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
        import_action = 'budget_breakdown_line'
        model = IMPORT_ACTION[import_action]['model']
        header_map = IMPORT_ACTION[import_action].get('header_map', False)
        extra_columns = IMPORT_ACTION[import_action].get('extra_columns',
                                                         False)
        return self.env['pabi.utils.xls'].\
            import_xls(model, self.import_file, header_map=header_map,
                       extra_columns=extra_columns, auto_id=False)
