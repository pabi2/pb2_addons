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
