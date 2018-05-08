# -*- coding: utf-8 -*-
from openerp import models, fields, api


class IRActionReportXML(models.Model):
    _inherit = 'ir.actions.report.xml'

    context = fields.Char(
        string='Context',
        copy=False,
        default={},
    )


class Report(models.Model):
    _inherit = 'report'

    @api.multi
    def render(self, template, values=None):
        ctx = self._context.copy()
        report_action = self.get_action(self, template, values)
        report_action = self.env['ir.actions.report.xml'].search(
            [('report_name', '=', template)], limit=1)
        if report_action:
            ctx.update(report_action=report_action)
        return super(Report, self.with_context(ctx)).render(template,
                                                            values=values)

    def translate_doc(self, cr, uid, doc_id, model,
                      lang_field, template, values, context=None):
        """Helper used when a report should be translated into a specific lang.

        <t t-foreach="doc_ids" t-as="doc_id">
        <t t-raw="translate_doc(doc_id, doc_model, 'partner_id.lang',
                                account.report_invoice_document')"/>
        </t>

        :param doc_id: id of the record to translate
        :param model: model of the record to translate
        :param lang_field': field of the record containing the lang
        :param template: name of the template to translate into the lang_field
        """
        ctx = context.copy()
        report_action = False
        if ctx.get('report_action', False):
            report_action = ctx['report_action']
            report_action_ctx = eval(report_action.context)
            if report_action_ctx and report_action_ctx.get('lang', False):
                ctx['lang'] = report_action_ctx['lang']
                report_action = report_action_ctx['lang']

        doc = self.pool[model].browse(cr, uid, doc_id, context=ctx)
        qcontext = values.copy()
        # Do not force-translate if we chose to display
        # the report in a specific lang
        if ctx.get('translatable') is True:
            qcontext['o'] = doc
        else:
            # Reach the lang we want to translate the doc into
            if not report_action:
                ctx['lang'] = eval('doc.%s' % lang_field, {'doc': doc})
            qcontext['o'] = \
                self.pool[model].browse(cr, uid, doc_id, context=ctx)
        return self.pool['ir.ui.view'].render(cr, uid, template,
                                              qcontext, context=ctx)
