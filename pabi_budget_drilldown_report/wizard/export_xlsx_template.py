from openerp import models, api


class ExportXlsxTemplate(models.TransientModel):
    _inherit = 'export.xlsx.template'

    @api.model
    def _get_template_fname(self):
        template_fname = super(ExportXlsxTemplate, self)._get_template_fname()
        if self._context.get('select_template_by_report_type', False):
            active_id = self._context.get('active_id', False)
            report = self.env['budget.drilldown.report'].browse(active_id)
            report_type = report.report_type
            template_fname = dict(overall="budget_overall_report.xlsx",
                                  unit_base="budget_unit_base_report.xlsx",
                                  project_base="budget_overall_report.xlsx",
                                  invest_asset="budget_overall_report.xlsx",
                                  invest_construction=+
                                  "budget_overall_report.xlsx")[report_type]

        return template_fname
