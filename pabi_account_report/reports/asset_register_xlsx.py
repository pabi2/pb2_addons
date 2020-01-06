# -*- coding: utf-8 -*-
# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from types import CodeType
from openerp.addons.pabi_report_xlsx_helper.report.report_xlsx_abstract \
    import ReportXlsxAbstract
from openerp import fields, _

STATE = [
    ('draft', 'Draft'),
    ('open', 'Running'),
    ('close', 'Close'),
    ('removed', 'Removed')
]


class AssetRegisterXlsx(ReportXlsxAbstract):

    def _write_ws_filter(self, ws, pos, ws_params, col_specs_section=None,
                         render_space=None, default_format=None):
        col_specs = ws_params.get('col_filters')
        wl = ws_params.get('data_filters') or []
        row_pos = 2
        # pos = 0
        for col in wl:
            colspan = col_specs[col].get('colspan') or 1
            cell_spec = col_specs[col].get(col_specs_section) or {}
            cell_value = cell_spec.get('value')
            cell_type = cell_spec.get('type')
            cell_format = cell_spec.get('format') or default_format
            if not cell_type:
                cell_type = 'string'
            colspan = cell_spec.get('colspan') or colspan
            args_pos = [row_pos, pos]
            args_data = [cell_value]
            if cell_format:
                if isinstance(cell_format, CodeType):
                    cell_format = self._eval(cell_format, render_space)
                args_data.append(cell_format)
            ws_method = getattr(ws, 'write_%s' % cell_type)
            args = args_pos + args_data
            ws_method(*args)
            row_pos += colspan
        # x=1/0
        return pos + 1, row_pos

    def _get_ws_params(self, wb, data, assets):
        asset_template = {
            '01_org_owner': {
                'header': {
                    'value': _('Org Owner'),
                },
                'data': {
                    'value':
                        self._render('asset.owner_budget.org_id.name_short'),
                },
                'width': 18,
            },
            '02_product_category': {
                'header': {
                    'value': _('Product Category'),
                },
                'data': {
                    'value':
                        self._render('product_category'),
                },
                'width': 20,
            },
            '03_account_code': {
                'header': {
                    'value': _('Account Code'),
                },
                'data': {
                    'value': self._render('account_code'),
                },
                'width': 15,
            },
            '04_account_name': {
                'header': {
                    'value': _('Account Name'),
                },
                'data': {
                    'value': self._render('account_name'),
                },
                'width': 20,
            },
            '05_asset_profile_code': {
                'header': {
                    'value': _('Asset Profile Code'),
                },
                'data': {
                    'value': self._render('profile_code'),
                },
                'width': 15,
            },
            '06_asset_profile_name': {
                'header': {
                    'value': _('Asset Profile Name'),
                },
                'data': {
                    'value': self._render('profile_name'),
                },
                'width': 20,
            },
            '07_asset_code': {
                'header': {
                    'value': _('Asset Code'),
                },
                'data': {
                    'value': self._render('asset.code'),
                },
                'width': 15,
            },
            '08_asset_name': {
                'header': {
                    'value': _('Asset Name'),
                },
                'data': {
                    'value': self._render('asset.name'),
                },
                'width': 25,
            },
            '09_asset_parent': {
                'header': {
                    'value': _('Asset Parent'),
                },
                'data': {
                    'value': self._render('parent_name'),
                },
                'width': 20,
            },
            '10_asset_type': {
                'header': {
                    'value': _('Asset Type'),
                },
                'data': {
                    'value': self._render('asset_type'),
                },
                'width': 20,
            },
            '11_code_legacy': {
                'header': {
                    'value': _('Code (legacy)'),
                },
                'data': {
                    'value': self._render('code_legacy'),
                },
                'width': 15,
            },
            '12_acceptance_date': {
                'header': {
                    'value': _('Acceptance Date'),
                },
                'data': {
                    'value': self._render('acceptance_date'),
                },
                'width': 15,
            },
            '13_asset_start_date': {
                'header': {
                    'value': _('Asset Start Date'),
                },
                'data': {
                    'value': self._render('date_start'),
                    # for case data not null
                    'type': 'datetime',
                    'format': self.format_tcell_date_left,
                },
                'width': 15,
            },
            '14_picking_date': {
                'header': {
                    'value': _('Picking Date'),
                },
                'data': {
                    'value': self._render('picking_date'),
                },
                'width': 15,
            },
            '15_picking_number': {
                'header': {
                    'value': _('Picking Number'),
                },
                'data': {
                    'value': self._render('picking_number'),
                },
                'width': 15,
            },
            '16_budget_type': {
                'header': {
                    'value': _('Budget Type'),
                },
                'data': {
                    'value': self._render('asset.budget_type'),
                },
                'width': 15,
            },
            '17_source_budget_code': {
                'header': {
                    'value': _('Source of Budget Code'),
                },
                'data': {
                    'value': self._render('asset.budget.code'),
                },
                'width': 15,
            },
            '18_source_budget_name': {
                'header': {
                    'value': _('Source of Budget Name'),
                },
                'data': {
                    'value': self._render('asset.budget.name'),
                },
                'width': 20,
            },
            '19_owner_code': {
                'header': {
                    'value': _('Owner Code'),
                },
                'data': {
                    'value': self._render('asset.owner_budget.code'),
                },
                'width': 15,
            },
            '20_owner_name': {
                'header': {
                    'value': _('Owner Name'),
                },
                'data': {
                    'value': self._render('asset.owner_budget.name'),
                },
                'width': 20,
            },
            '21_cost_center_code': {
                'header': {
                    'value': _('Cost Center Code'),
                },
                'data': {
                    'value':
                        self._render('asset.owner_budget.costcenter_id.code'),
                },
                'width': 15,
            },
            '22_cost_center_name': {
                'header': {
                    'value': _('Cost Center Name'),
                },
                'data': {
                    'value':
                        self._render('asset.owner_budget.costcenter_id.name'),
                },
                'width': 20,
            },
            '23_fund_owner': {
                'header': {
                    'value': _('Fund of Owner'),
                },
                'data': {
                    'value': self._render('fund_owner'),
                },
                'width': 10,
            },
            '24_division': {
                'header': {
                    'value': _('Division'),
                },
                'data': {
                    'value': self._render('division'),
                },
                'width': 15,
            },
            '25_subsector': {
                'header': {
                    'value': _('Subsector'),
                },
                'data': {
                    'value': self._render('subsector'),
                },
                'width': 15,
            },
            '26_sector': {
                'header': {
                    'value': _('Sector'),
                },
                'data': {
                    'value': self._render('sector'),
                },
                'width': 15,
            },
            '27_building': {
                'header': {
                    'value': _('Building'),
                },
                'data': {
                    'value': self._render('building'),
                },
                'width': 10,
            },
            '28_floor': {
                'header': {
                    'value': _('Floor'),
                },
                'data': {
                    'value': self._render('floor'),
                },
                'width': 10,
            },
            '29_room': {
                'header': {
                    'value': _('Room'),
                },
                'data': {
                    'value': self._render('room'),
                },
                'width': 10,
            },
            '30_responsible_person_id': {
                'header': {
                    'value': _('Responsible Person ID'),
                },
                'data': {
                    'value': self._render('responsible_person_id'),
                },
                'width': 15,
            },
            '31_responsible_person_name': {
                'header': {
                    'value': _('Responsible Person Name'),
                },
                'data': {
                    'value': self._render('responsible_person_name'),
                },
                'width': 20,
            },
            '32_partner_code': {
                'header': {
                    'value': _('Partner Code'),
                },
                'data': {
                    'value': self._render('partner_code'),
                },
                'width': 15,
            },
            '33_partner_name': {
                'header': {
                    'value': _('Partner Name'),
                },
                'data': {
                    'value': self._render('partner_name'),
                },
                'width': 20,
            },
            '34_po_number ': {
                'header': {
                    'value': _('PO Number '),
                },
                'data': {
                    'value': self._render('po_number'),
                },
                'width': 13,
            },
            '35_pr_number': {
                'header': {
                    'value': _('PR Number'),
                },
                'data': {
                    'value': self._render('pr_number'),
                },
                'width': 13,
            },
            '36_purchase_method': {
                'header': {
                    'value': _('Purchase Method'),
                },
                'data': {
                    'value': self._render('purchase_method'),
                },
                'width': 10,
            },
            '37_asset_request_code': {
                'header': {
                    'value': _('Asset Request Code'),
                },
                'data': {
                    'value': self._render('asset_request_code'),
                },
                'width': 15,
            },
            '38_asset_request_name': {
                'header': {
                    'value': _('Asset Request Name'),
                },
                'data': {
                    'value': self._render('asset_request_name'),
                },
                'width': 20,
            },
            '39_pr_requester_code': {
                'header': {
                    'value': _('PR Requester Code'),
                },
                'data': {
                    'value': self._render('pr_requester_code'),
                },
                'width': 10,
            },
            '40_pr_requester_name': {
                'header': {
                    'value': _('PR Requester Name'),
                },
                'data': {
                    'value': self._render('pr_requester_name'),
                },
                'width': 20,
            },
            '41_pr_approved_date': {
                'header': {
                    'value': _('PR Approved Date'),
                },
                'data': {
                    'value': self._render('pr_approved_date'),
                },
                'width': 10,
            },
            '42_serial_number ': {
                'header': {
                    'value': _('Serial Number '),
                },
                'data': {
                    'value': self._render('serial_number'),
                },
                'width': 15,
            },
            '43_warranty_start_date': {
                'header': {
                    'value': _('Warranty Start Date'),
                },
                'data': {
                    'value': self._render('warranty_start_date'),
                },
                'width': 10,
            },
            '44_warranty_expire_date': {
                'header': {
                    'value': _('Warranty Expire Date'),
                },
                'data': {
                    'value': self._render('warranty_expire_date'),
                },
                'width': 10,
            },
            '45_fiscal_year': {
                'header': {
                    'value': _('Fiscal Year'),
                },
                'data': {
                    'value': self._render('fiscalyear'),
                },
                'width': 10,
            },
            '46_purchase_value_before_current_fy': {
                'header': {
                    'value': _('Purchase Value Before Current FY'),
                },
                'data': {
                    'value': self._render('asset.purchase_before_current'),
                    'type': 'number',
                    'format': self.format_tcell_amount_right,
                },
                'width': 15,
            },
            '47_purchase_value_current_fy': {
                'header': {
                    'value': _('Purchase Value Current FY'),
                },
                'data': {
                    'value': self._render('asset.purchase_current'),
                    'type': 'number',
                    'format': self.format_tcell_amount_right,
                },
                'width': 15,
            },
            '48_purchase_value': {
                'header': {
                    'value': _('Purchase Value'),
                },
                'data': {
                    'value': self._render('asset.purchase_value'),
                    'type': 'number',
                    'format': self.format_tcell_amount_right,
                },
                'width': 15,
            },
            '49_accum_depre_bf': {
                'header': {
                    'value': _('Accum. Depre B/F'),
                },
                'data': {
                    'value': self._render('asset.accumulated_bf'),
                    'type': 'number',
                    'format': self.format_tcell_amount_right,
                },
                'width': 15,
            },
            '50_depreciation': {
                'header': {
                    'value': _('Depreciation'),
                },
                'data': {
                    'value': self._render('asset.depreciation'),
                    'type': 'number',
                    'format': self.format_tcell_amount_right,
                },
                'width': 15,
            },
            '51_accum_depre_cf': {
                'header': {
                    'value': _('Accum. Depre C/F'),
                },
                'data': {
                    'value': self._render('accum_depre_cf'),
                    'type': 'number',
                    'format': self.format_tcell_amount_right,
                },
                'width': 15,
            },
            '52_net_book_value': {
                'header': {
                    'value': _('Net Book Value'),
                },
                'data': {
                    'value': self._render('net_book_value'),
                    'type': 'number',
                    'format': self.format_tcell_amount_right,
                },
                'width': 15,
            },
            '53_number_of_years': {
                'header': {
                    'value': _('Number of Years'),
                },
                'data': {
                    'value': self._render('asset.method_number'),
                    'type': 'number',
                    'format': self.format_tcell_amount_right,
                },
                'width': 7,
            },
            '54_adjustment': {
                'header': {
                    'value': _('Adjustment'),
                },
                'data': {
                    'value': self._render('adjustment'),
                },
                'width': 15,
            },
            '55_asset_status': {
                'header': {
                    'value': _('Asset Status'),
                },
                'data': {
                    'value': self._render('asset.status.name'),
                },
                'width': 10,
            },
            '56_asset_removal_date': {
                'header': {
                    'value': _('Asset Removal Date'),
                },
                'data': {
                    'value': self._render('asset_removal_date'),
                },
                'width': 10,
            },
            '57_asset_state': {
                'header': {
                    'value': _('Asset State'),
                },
                'data': {
                    'value': self._render('state'),
                },
                'width': 10,
            },
        }

        asset_filters = {
            '01_filter_org': {
                'header': {
                    'value': 'Org',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.org_ids, 'name_short'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '02_filter_fiscal_year': {
                'header': {
                    'value': 'Fiscal Year',
                },
                'data': {
                    'value': assets.fiscalyear_start_id.name,
                },
                'header2': {
                    'value': 'To',
                    'format': self.format_theader_yellow_left,
                },
                'data2': {
                    'value': assets.fiscalyear_end_id.name,
                },
            },
            '03_filter_date_start': {
                'header': {
                    'value': 'Date',
                },
                'data': {
                    'value': fields.Date.from_string(assets.date_start),
                    'type': 'datetime',
                    'format': self.format_tcell_date_left,
                },
                'header2': {
                    'value': 'To',
                    'format': self.format_theader_yellow_left,
                },
                'data2': {
                    'value': fields.Date.from_string(assets.date_end),
                    'type': 'datetime',
                    'format': self.format_tcell_date_left,
                },
            },
            '04_filter_asset_profile': {
                'header': {
                    'value': 'Asset Profile',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.asset_profile_ids, 'name'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '05_filter_asset_ids': {
                'header': {
                    'value': 'Asset Code',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.asset_ids, 'name'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '06_filter_account_ids': {
                'header': {
                    'value': 'Account Code',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.account_ids, 'code'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '07_filter_responsible_person_ids': {
                'header': {
                    'value': 'Responsible Person',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.responsible_person_ids, 'name'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '08_filter_building': {
                'header': {
                    'value': 'Building',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.building_ids, 'name'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '09_filter_floor': {
                'header': {
                    'value': 'Floor',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.floor_ids, 'name'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '10_filter_room': {
                'header': {
                    'value': 'Room',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.room_ids, 'name'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '11_filter_state': {
                'header': {
                    'value': 'State',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.asset_state, 'name'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '12_filter_asset_status': {
                'header': {
                    'value': 'Asset Status',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.asset_status_ids, 'name'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '13_filter_source_budget': {
                'header': {
                    'value': 'Source of Budget',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.budget, 'code'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '14_filter_owner': {
                'header': {
                    'value': 'Owner',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.owner_budget, 'code'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '15_filter_cost_center': {
                'header': {
                    'value': 'Cost Center',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.costcenter_ids, 'code'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '16_filter_division': {
                'header': {
                    'value': 'Division',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.division_ids, 'code'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '17_filter_sector': {
                'header': {
                    'value': 'Sector',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.sector_ids, 'code'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '18_filter_subsector': {
                'header': {
                    'value': 'Subsector',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.subsector_ids, 'code'),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '19_filter_current_year': {
                'header': {
                    'value': 'Current Year',
                },
                'data': {
                    'value': assets.current_year.name,
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '20_filter_run_by': {
                'header': {
                    'value': 'Run By',
                },
                'data': {
                    'value': assets.env.user.with_context(
                        lang="th_TH").display_name,
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
            '21_filter_run_date': {
                'header': {
                    'value': 'Run Date',
                },
                'data': {
                    'value': self.convert_to_date(fields.Datetime.now()),
                },
                'header2': {
                    'value': '',
                },
                'data2': {
                    'value': '',
                },
            },
        }
        ws_params = {
            'ws_name': 'Asset Register',
            'generate_ws_method': '_assets_report',
            'title': _('Asset Register - %s') % assets.company_id.name,
            'data_filters': [str(x) for x in sorted(asset_filters.keys())],
            'col_filters': asset_filters,
            'wanted_list': [str(x) for x in sorted(asset_template.keys())],
            'col_specs': asset_template,
        }
        return [ws_params]

    def find_fiscalyear(self, date):
        fiscalyear = self.env['account.fiscalyear'].browse(
            self.env['account.fiscalyear'].find(date))
        return fiscalyear

    def convert_to_date(self, date):
        if not date:
            return _('')
        string_to_date = fields.Date.from_string(date).strftime('%d/%m/%Y')
        return string_to_date

    def _get_po_number(self, asset):
        if not asset.purchase_id:
            return asset.adjust_id.ship_purchase_id.name or _('')
        return asset.purchase_id.name

    def _get_accum_depre_cf(self, asset):
        accum_depre_cf = asset.accumulated_bf + asset.depreciation
        return accum_depre_cf

    def _get_net_book_value(self, asset):
        net_book_value = asset.purchase_value - self._get_accum_depre_cf(asset)
        return net_book_value

    def _assets_report(self, workbook, ws, ws_params, data, assets):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers['standard'])
        ws.set_footer(self.xls_footers['standard'])
        # Set font name
        workbook.formats[0].set_font_name('Arial')

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params)
        # Create Filters data
        pos = 0
        pos, row_pos = self._write_ws_filter(
            ws, pos, ws_params, col_specs_section='header',
            default_format=self.format_theader_yellow_left)
        pos, row_pos = self._write_ws_filter(
            ws, pos, ws_params, col_specs_section='data')
        # PABI2 : FIlter2 data
        pos, row_pos = self._write_ws_filter(
            ws, pos, ws_params, col_specs_section='header2')
        pos, row_pos = self._write_ws_filter(
            ws, pos, ws_params, col_specs_section='data2')
        # Create line data
        row_pos += 1
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section='header',
            default_format=self.format_theader_yellow_center)

        for asset in assets.results:
            row_pos = self._write_line(
                ws, row_pos, ws_params, col_specs_section='data',
                render_space={
                    'asset': asset,
                    'product_category':
                        asset.profile_id.product_categ_id.name or _(''),
                    'account_code': asset.account_code or _(''),
                    'account_name': asset.account_name or _(''),
                    'profile_code': asset.profile_id.code or _(''),
                    'profile_name': asset.profile_id.name or _(''),
                    'parent_name': asset.parent_id.name or _(''),
                    'asset_type': asset.product_id.name or _(''),
                    'code_legacy': asset.code2 or _(''),
                    'acceptance_date': self.convert_to_date(
                        asset.picking_id.acceptance_id.date_accept),
                    'date_start':
                        fields.Date.from_string(asset.date_start),
                    'picking_date': self.convert_to_date(asset.date_picking),
                    'picking_number': asset.picking_id.name or _(''),
                    'fund_owner': assets._get_filter_many2many(
                        asset.owner_budget.fund_ids, 'name'),
                    'division':
                        asset.owner_section_id.division_id.name or _(''),
                    'subsector':
                        asset.owner_section_id.subsector_id.name or _(''),
                    'sector': asset.owner_section_id.sector_id.name or _(''),
                    'building': asset.building_id.name or _(''),
                    'floor': asset.floor_id.name or _(''),
                    'room': asset.room_id.name or _(''),
                    'responsible_person_id':
                        asset.responsible_user_id.login or _(''),
                    'responsible_person_name':
                        asset.responsible_user_id.name or _(''),
                    'partner_code': asset.partner_id.search_key or _(''),
                    'partner_name': asset.partner_id.name or _(''),
                    'po_number': self._get_po_number(asset),
                    'pr_number': asset.purchase_request_id.name or _(''),
                    'purchase_method':
                        asset.asset_purchase_method_id.name or _(''),
                    'asset_request_code': asset.doc_request_id.name or _(''),
                    'asset_request_name': asset.doc_request_id.name or _(''),
                    'pr_requester_code': asset.pr_requester_id.login or _(''),
                    'pr_requester_name': asset.pr_requester_id.name or _(''),
                    'pr_approved_date':
                        self.convert_to_date(asset.date_request),
                    'serial_number': asset.serial_number or _(''),
                    'warranty_start_date':
                        self.convert_to_date(asset.warranty_start_date),
                    'warranty_expire_date':
                        self.convert_to_date(asset.warranty_expire_date),
                    'fiscalyear': self.find_fiscalyear(asset.date_start).name,
                    'accum_depre_cf': self._get_accum_depre_cf(asset),
                    'net_book_value': self._get_net_book_value(asset),
                    'adjustment': asset.adjust_id.name or _(''),
                    'asset_removal_date':
                        self.convert_to_date(asset.date_remove),
                    'state': dict(STATE)[asset.state],
                })


AssetRegisterXlsx('report.report_asset_register_xlsx', 'asset.register.report')
