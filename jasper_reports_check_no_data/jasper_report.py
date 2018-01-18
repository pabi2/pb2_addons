# -*- encoding: utf-8 -*-
from openerp.osv import osv
import os
import openerp
from openerp import release, report, _
from openerp.addons.jasper_reports.jasper_report import Report
from openerp.exceptions import except_orm


class Report(Report, object):

    def executeReport(self, dataFile, outputFile, subreportDataFiles,
                      copy, force_locale):
        pages = super(Report, self).executeReport(
            dataFile, outputFile, subreportDataFiles, copy, force_locale)
        if not pages:
            raise except_orm(_('Error !'), _('No data available'))
        return pages


class report_jasper(report.interface.report_int):
    def __init__(self, name, model, parser=None):
        # Remove report name from list of services if it already
        # exists to avoid report_int's assert. We want to keep the
        # automatic registration at login, but at the same time we
        # need modules to be able to use a parser for certain reports.
        if release.major_version == '5.0':
            if name in openerp.report.interface.report_int._reports:
                del openerp.report.interface.report_int._reports[name]
        else:
            if name in openerp.report.interface.report_int._reports:
                del openerp.report.interface.report_int._reports[name]
#             openerp.report.interface.report_int._reports[name] =
        super(report_jasper, self).__init__(name)
        self.model = model
        self.parser = parser

    def create(self, cr, uid, ids, data, context):
        name = self.name
        if self.parser:
            d = self.parser(cr, uid, ids, data, context)
            ids = d.get('ids', ids)
            name = d.get('name', self.name)
            # Use model defined in report_jasper definition.
            # Necesary for menu entries.
            data['model'] = d.get('model', self.model)
            data['records'] = d.get('records', [])
            # data_source can be 'model' or 'records' and lets parser to return
            # an empty 'records' parameter
            # while still executing using 'records'
            data['data_source'] = d.get('data_source', 'model')
            data['parameters'] = d.get('parameters', {})
        r = Report(name, cr, uid, ids, data, context)
        # return ( r.execute(), 'pdf' )
        return r.execute()


if release.major_version == '5.0':
    # Version 5.0 specific code

    # Ugly hack to avoid developers the need to register reports
    import pooler
    import report

    def register_jasper_report(name, model):
        name = 'report.%s' % name
        # Register only if it didn't exist another "jasper_report"
        # with the same name given that developers might prefer/need
        # to register the reports themselves. For example, if they need their
        # own parser.
        if name in openerp.report.interface.report_int._reports:
            if isinstance(openerp.report.interface.report_int._reports[name],
                          report_jasper):
                return openerp.report.interface.report_int._reports[name]
            del openerp.report.interface.report_int._reports[name]
        report_jasper(name, model)

    # This hack allows automatic registration of jrxml files without
    # the need for developers to register them programatically.

    old_register_all = report.interface.register_all

    def new_register_all(db):
        value = old_register_all(db)

        cr = db.cursor()
        # Originally we had auto=true in the SQL filter but we will
        # register all reports.
        cr.execute(
            "SELECT * FROM ir_act_report_xml \
            WHERE report_rml ilike '%.jrxml' ORDER BY id")
        records = cr.dictfetchall()
        cr.close()
        for record in records:
            register_jasper_report(record['report_name'], record['model'])
        return value

    report.interface.register_all = new_register_all


def register_jasper_report(report_name, model_name):
    name = 'report.%s' % report_name
    # Register only if it didn't exist another "jasper_report"
    # with the same name given that developers might prefer/need to register
    # the reports themselves. For example, if they need their own parser.
    if name in openerp.report.interface.report_int._reports:
        if isinstance(openerp.report.interface.report_int._reports[name],
                      report_jasper):
            return openerp.report.interface.report_int._reports[name]
        del openerp.report.interface.report_int._reports[name]
    return report_jasper(name, model_name)


class ir_actions_report_xml(osv.osv):
    _inherit = 'ir.actions.report.xml'

    def _lookup_report(self, cr, name):
        """
        Look up a report definition.
        """
        opj = os.path.join
        # First lookup in the deprecated place, because
        # if the report definition has not been updated , it is more likely
        # the correct definition is there. Only reports with custom parser
        # sepcified in Python are still there.
        cr.execute(
            "SELECT * FROM ir_act_report_xml \
             WHERE jasper_report='t' and report_name=%s limit 1", (name,))
        record = cr.dictfetchone()
        if not record:
            return super(ir_actions_report_xml, self)._lookup_report(cr, name)
        # Calling Jasper
        new_report = register_jasper_report(name, record['model'])
        return new_report
