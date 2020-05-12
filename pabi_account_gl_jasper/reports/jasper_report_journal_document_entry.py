# -*- coding: utf-8 -*-
from openerp import models, fields, api


class JasperReportJournalDocumentEntry(models.TransientModel):
    _name = 'jasper.report.journal.document.entry'
    _inherit = 'xlsx.report.expense.ledger'
    
    doc_type = fields.Char(
        string='Doc Type',
    )
    
    doc_number_ids =  fields.Many2many(
        'account.move',
        string='Document Number',
    )
    
    doc_line_filter = fields.Text(
        string='Document Number Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    
    @api.onchange('doc_line_filter')
    def _onchange_line_filter(self):
        self.doc_number_ids = []
        am_obj = self.env['account.move']
        dom = []
        if self.doc_line_filter:
            numbers = self.doc_line_filter.split('\n')
            numbers = [x.strip() for x in numbers]
            numbers = ','.join(numbers)
            dom.append(('name', 'ilike', numbers))
            self.doc_number_ids = am_obj.search(dom, order='id')
            
    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account.move.line
        2. Check account type is expense
        """
        self.ensure_one()
#         Result = self.env['account.move.line']
        dom = []
         
#         if self.user_type:
#             dom = [('account_id.user_type', '=', self.user_type.id)]
        if self.account_ids:
#             dom += [('account_id', 'in', self.account_ids.ids)]
            dom += [(' account_id in ({}) '.format(','.join(map(str, (self.account_ids.ids)))))]
        if self.operating_unit_ids:
#             dom += [('account_id.operating_unit_id', 'in', self.operating_unit_ids.ids)]
#             dom += [('partner_id.user_id.default_operating_unit_id', 'in', self.operating_unit_ids.ids)]
            dom += [(' operating_unit_id in ({}) '.format(','.join(map(str, (self.operating_unit_ids.ids)))))]
        if self.chartfield_ids:
            # map beetween chartfield_id with chartfield type
            chartfields = [('section_id', 'sc:'),
                           ('project_id', 'pj:'),
                           ('invest_construction_phase_id', 'cp:'),
                           ('invest_asset_id', 'ia:'),
                           ('personnel_costcenter_id', 'pc:')]
            where_str = ''
            res_ids = []
            for chartfield_id, chartfield_type in chartfields:
                chartfield_ids = self.chartfield_ids.filtered(
                    lambda l: l.type == chartfield_type).mapped('res_id')
                if chartfield_ids:
                    if where_str:
                        where_str += ' or '
                    where_str += chartfield_id + ' in %s'
                    res_ids.append(tuple(chartfield_ids))
            if res_ids:
                sql = "select id from account_move_line where " + where_str
                self._cr.execute(sql, res_ids)
#                 dom += [('id', 'in', map(lambda l: l[0], self._cr.fetchall()))]
                dom += [(' id in ({}) '.format(','.join(map(str, (map(lambda l: l[0], self._cr.fetchall()))))))]
        if self.partner_ids:
#             dom += [('partner_id', 'in', self.partner_ids.ids)]
            dom += [(' partner_id in ({}) '.format(','.join(map(str, (self.partner_ids.ids)))))]
        if self.charge_type:
#             dom += [('charge_type', '=', self.charge_type)]
            dom += [(" charge_type = '{}' ".format(self.charge_type))]
        if self.fiscalyear_start_id:
#             dom += [('date', '>=', self.fiscalyear_start_id.date_start)]
#             date_start = [(" date >= '{}' ".format(self.fiscalyear_start_id.date_start))]
            date_start = self.fiscalyear_start_id.date_start
        if self.fiscalyear_end_id:
#             dom += [('date', '<=', self.fiscalyear_end_id.date_stop)]
#             date_end = [(" date <= '{}' ".format(self.fiscalyear_end_id.date_stop))]
            date_end = self.fiscalyear_end_id.date_stop
        if self.period_start_id:
#             dom += [('date', '>=', self.period_start_id.date_start)]
#             date_start = [(" date >= '{}' ".format(self.period_start_id.date_start))]
            date_start = self.period_start_id.date_start
        if self.period_end_id:
#             dom += [('date', '<=', self.period_end_id.date_stop)]
#             date_end = [(" date <= '{}' ".format(self.period_end_id.date_stop))]
            date_end = self.period_start_id.date_stop
        if self.date_start:
#             dom += [('date', '>=', self.date_start)]
#             date_start = [(" date >= '{}' ".format(self.date_start))]
            date_start = self.date_start
        if self.date_end:
#             dom += [('date', '<=', self.date_end)]
#             date_end = [(" date <= '{}' ".format(self.date_end))]
            date_end = self.date_end
        if self.doc_type:
            dom += [(" am.name like '{}%'".format(self.doc_type))]
        if self.doc_number_ids:
            dom += [(" aml.move_id in ({}) ".format(','.join(map(str, (self.doc_number_ids.ids)))))]
            
#         self.results = Result.with_context(active=False).search(dom).sorted(
#                        key=lambda l: (l.charge_type,
#                                       l.account_id.code,
#                                       l.activity_group_id.code,
#                                       l.activity_id.code,
#                                       l.period_id.fiscalyear_id.name,
#                                       l.period_id.name))
        return date_start,date_end,dom
        
            
    @api.multi
    def start_report(self):
        self.ensure_one()
        date_start,date_end,dom = self._compute_results()
        params = {}
#         params['condition'] = 'and'.join(map(str, where_str)) #error
#         params['ids'] = [3613143,3613144] #pass
#         params['condition'] = 'id in (1829948,1829949,1829950,1829951,1847763)' #pass
#         params['condition'] = "date >= \'2019-10-01\' and date <= \'2020-09-30\' and move_id in (628204,627347,626953,624181)" #error
        params['date_start'] = date_start
        params['date_end'] = date_end
        params['condition'] = 'and'.join(map(str, dom))
        return { 
            'type': 'ir.actions.report.xml',
            'report_name': 'report_journal_document_entry',
            'datas': params,
        }  
