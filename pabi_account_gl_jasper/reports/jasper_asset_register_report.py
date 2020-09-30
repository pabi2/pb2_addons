# -*- coding: utf-8 -*-
from openerp import models, fields, api

class JasperAssetRegisterReport(models.TransientModel):
    _name = 'jasper.asset.register.report'
    _inherit = 'asset.register.report'
    
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        dom = []
        # Prepare DOM to filter assets
        if self.asset_filter:
            self._onchange_asset_filter()
        if self.asset_ids:
            dom += [(' asset.id in ({})'.\
                     format(','.join(map(str, (self.asset_ids.ids)))))]
        if self.asset_profile_ids:
            dom += [(' asset.profile_id in ({})'.\
                     format(','.join(map(str, (self.asset_profile_ids.ids)))))]
        if self.responsible_person_ids:
            dom += [(' asset.responsible_user_id in ({})'.\
                     format(','.join(map(str, (self.responsible_person_ids.ids)))))]
        if self.org_ids:
            dom += [(' asset.owner_org_id in ({})'.\
                     format(','.join(map(str, (self.org_ids.ids)))))]
        if self.asset_status_ids:
            dom += [(' asset.status in ({})'.\
                     format(','.join(map(str, (self.asset_status_ids.ids)))))]
        if self.account_ids:
            dom += [(' asset.account_asset_id in ({})'.\
                     format(','.join(map(str, (self.account_ids.ids)))))]
        if self.budget:
            dom_budget = \
                ["%s,%s" % ((x.model).encode('utf-8'), x.res_id)
                 for x in self.budget]
            dom += [('asset.budget in {}'.format(tuple(dom_budget)))]
        if self.owner_budget:
            dom_owner = \
                ["%s,%s" % ((x.model).encode('utf-8'), x.res_id)
                 for x in self.owner_budget]
            dom += [('asset.owner_budget in {}'.format(tuple(dom_owner)))]
        if self.costcenter_ids:
            dom += [(' asset.owner_costcenter_id in ({})'.\
                     format(','.join(map(str, (self.costcenter_ids.ids)))))]
        if self.division_ids:
            dom += [(' asset.owner_division_id in ({})'.\
                     format(','.join(map(str, (self.division_ids.ids)))))]
        if self.sector_ids:
            dom += [(' asset.owner_sector_id in ({})'.\
                     format(','.join(map(str, (self.sector_ids.ids)))))]
        if self.subsector_ids:
            dom += [(' asset.owner_subsector_id in ({})'.\
                     format(','.join(map(str, (self.subsector_ids.ids)))))]
        if self.asset_state:
            res, state_name = [], self.asset_state
            for state in self.asset_state:
                state_name = self.env['xlsx.report.status'].\
                search([('id', '=', state.id)])
                res += [str(state_name.status)]
            if len(self.asset_state) == 1 : 
                dom += [('asset.state in (\'{}\')'.format(str(state_name.status)))]
            else : 
                dom += [('asset.state in {}'.format(tuple(res)))]

        if self.building_ids:
            dom += [(' asset.building_id in ({})'.\
                     format(','.join(map(str, (self.building_ids.ids)))))]
        if self.floor_ids:
            dom += [(' asset.floor_id in ({})'.\
                     format(','.join(map(str, (self.floor_ids.ids)))))]
        if self.room_ids:
            dom += [(' asset.room_id in ({})'.\
                     format(','.join(map(str, (self.room_ids.ids)))))]
        if self.asset_active:
            if self.asset_active == 'active':
                dom += [('asset.active = {}'.format(True))]
            elif self.asset_active == 'inactive':
                dom += [('asset.active = {}'.format(False))]
        # date_start <= date_end
#         if self.date_end:
#             dom += [('asset.date_start <= \'{}\''.format(self.date_end))]

        # Prepare fixed params
        date_start = False
        date_end = False
        accum_depre_account_ids = False
        depre_account_ids = False
        fiscalyear_start = self.fiscalyear_start_id.name
        
        if self.filter == 'filter_date':
            date_start = self.date_start #self.fiscalyear_start_id.date_start
            date_end = self.date_end
        if self.filter == 'filter_period':
            date_start = self.period_start_id.date_start
            date_end = self.period_end_id.date_stop
        if not date_start or not date_end:
            raise ValidationError(_('Please provide from and to dates.'))
        accum_depre_account_ids = tuple(self.env['account.account'].search(
            [('user_type', '=', self.accum_depre_account_type.id)]).ids)
        depre_account_ids = tuple(self.env['account.account'].search(
            [('user_type', '=', self.depre_account_type.id)]).ids)
        
        
        return dom,date_start,date_end,accum_depre_account_ids\
            ,depre_account_ids,fiscalyear_start
    
    @api.multi
    def start_report(self):
        self.ensure_one()
        dom,date_start,date_end,accum_depre_account_ids,depre_account_ids,\
        fiscalyear_start = self._compute_results()
        params = {}
        params['date_start'] = date_start
        params['date_end'] = date_end
        params['accum_depre_account_ids'] = str(accum_depre_account_ids)
        params['depre_account_ids'] = str(depre_account_ids)
        params['fiscalyear_start'] = fiscalyear_start
        params['condition'] = ' where ' +  (' and '.join(map(str, dom)))
        return { 
            'type': 'ir.actions.report.xml',
            'report_name': 'report_asset_register',
            'datas': params,
        }  