# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


class AccountTrialBalanceWizard(orm.TransientModel):
    """Will launch trial balance report and pass required args"""

    _inherit = "account.common.balance.report"
    _name = "trial.balance.webkit"
    _description = "Trial Balance Report"

    _columns = {
        'charge_type': fields.selection(
            [('internal', 'Internal'),
             ('external', 'External')],
            string='Charge Type',
        ),
        'org_id': fields.many2one(
            'res.org', string='Org'),
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(AccountTrialBalanceWizard, self).\
            pre_print_report(cr, uid, ids, data, context)

        # PABI2
        vals = self.read(cr, uid, ids, ['charge_type'], context=context)[0] 
        data['form'].update(vals)
        vals = self.read(cr, uid, ids, ['org_id'], context=context)[0]
        if vals['org_id']:
            vals = vals['org_id'][0]
        else:
            vals = vals['org_id']
        data['form'].update({'org_id':vals})
        #add org_name in form
        if data['form']['org_id']:
            _org_name = self.pool.get('res.org').browse(cr,uid, data['form']['org_id']) #pdf 21/03/2019
            org_name = []
            for record in _org_name:
                org_name.append(record.name_short)
            data['form'].update({'org_name':' '.join(org_name)})
        else:
            data['form'].update({'org_name':''})       
        data['specific_report'] = True

        return data

    def _print_report(self, cursor, uid, ids, data, context=None):
        context = context or {}
        # we update form with display account value
        data = self.pre_print_report(cursor, uid, ids, data, context=context)

        return {'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_trial_balance_webkit',
                'datas': data}
