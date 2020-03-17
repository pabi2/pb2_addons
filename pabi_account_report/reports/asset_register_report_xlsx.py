# -*- coding: utf-8 -*-
# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from openerp.addons.pabi_report_xlsx_helper.report.report_xlsx_abstract \
    import ReportXlsxAbstract
from openerp import _, fields

STATE = [
    ('draft', 'Draft'),
    ('open', 'Running'),
    ('close', 'Close'),
    ('removed', 'Removed')
]


class AssetRegisterXlsx(ReportXlsxAbstract):
    def _get_ws_params(self, wb, data, assets):
        asset_filters = {
            '01_filter_org': {
                'header': {
                    'value': 'Org',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.org_ids, 'name_short'),
                },
            },
            '02_filter_fiscal_year': {
                'header': {
                    'multi': [
                        {'value': _('Fiscal Year')},
                        {'value': _('To')},
                    ],
                },
                'data': {
                    'multi': [
                        {'value': assets.fiscalyear_start_id.name},
                        {'value': assets.fiscalyear_end_id.name},
                    ],
                },
            },
            '03_filter_date_start': {
                'header': {
                    'multi': [
                        {'value': _('Date')},
                        {'value': _('To')},
                    ]
                },
                'data': {
                    'multi': [
                        {
                            'value': assets.date_start,
                            'type': 'datetime',
                        },
                        {
                            'value': assets.date_end,
                            'type': 'datetime'
                        }
                    ]
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
            },
            '05_filter_asset_ids': {
                'header': {
                    'value': 'Asset Code',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.asset_ids, 'name'),
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
            },
            '07_filter_responsible_person_ids': {
                'header': {
                    'value': 'Responsible Person',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.responsible_person_ids, 'name'),
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
            },
            '09_filter_floor': {
                'header': {
                    'value': 'Floor',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.floor_ids, 'name'),
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
            },
            '11_filter_state': {
                'header': {
                    'value': 'State',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.asset_state, 'name'),
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
            },
            '13_filter_source_budget': {
                'header': {
                    'value': 'Source of Budget',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.budget, 'code'),
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
            },
            '15_filter_cost_center': {
                'header': {
                    'value': 'Cost Center',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.costcenter_ids, 'code'),
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
            },
            '17_filter_sector': {
                'header': {
                    'value': 'Sector',
                },
                'data': {
                    'value': assets._get_filter_many2many(
                        assets.sector_ids, 'code'),
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
            },
            '19_filter_current_year': {
                'header': {
                    'value': 'Current Year',
                },
                'data': {
                    'value': assets.current_year.name,
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
            },
            '21_filter_run_date': {
                'header': {
                    'value': 'Run Date',
                },
                'data': {
                    'value': fields.Datetime.now(),
                    'type': 'datetime',
                },
            },
        }
        asset_template = {
            '01_org_owner': {
                'header': {
                    'value': _('Org Owner'),
                },
                'data': {
                    'value':
                        self._render(
                            'object.owner_budget.org_id.name_short'),
                },
                'width': 18,
            },
            '02_product_category': {
                'header': {
                    'value': _('Product Category'),
                },
                'data': {
                    'value': self._render(
                        'object.profile_id.product_categ_id.name'),
                },
                'width': 20,
            },
            '03_account_code': {
                'header': {
                    'value': _('Account Code'),
                },
                'data': {
                    'value': self._render('object.account_code'),
                },
                'width': 15,
            },
            '04_account_name': {
                'header': {
                    'value': _('Account Name'),
                },
                'data': {
                    'value': self._render('object.account_name'),
                },
                'width': 20,
            },
            '05_asset_profile_code': {
                'header': {
                    'value': _('Asset Profile Code'),
                },
                'data': {
                    'value': self._render('object.profile_id.code'),
                },
                'width': 15,
            },
            '06_asset_profile_name': {
                'header': {
                    'value': _('Asset Profile Name'),
                },
                'data': {
                    'value': self._render('object.profile_id.name'),
                },
                'width': 20,
            },
            '07_asset_code': {
                'header': {
                    'value': _('Asset Code'),
                },
                'data': {
                    'value': self._render('object.code'),
                },
                'width': 15,
            },
            '08_asset_name': {
                'header': {
                    'value': _('Asset Name'),
                },
                'data': {
                    'value': self._render('object.name'),
                },
                'width': 25,
            },
            '09_asset_parent': {
                'header': {
                    'value': _('Asset Parent'),
                },
                'data': {
                    'value': self._render('object.parent_id.name'),
                },
                'width': 20,
            },
            '10_asset_type': {
                'header': {
                    'value': _('Asset Type'),
                },
                'data': {
                    'value': self._render('object.product_id.name'),
                },
                'width': 20,
            },
            '11_code_legacy': {
                'header': {
                    'value': _('Code (legacy)'),
                },
                'data': {
                    'value': self._render('object.code2'),
                },
                'width': 15,
            },
            '12_acceptance_date': {
                'header': {
                    'value': _('Acceptance Date'),
                },
                'data': {
                    'value': self._render(
                        'object.picking_id.acceptance_id.date_accept'),
                    'type': 'datetime',
                },
                'width': 15,
            },
            '13_asset_start_date': {
                'header': {
                    'value': _('Asset Start Date'),
                },
                'data': {
                    'value': self._render('object.date_start'),
                    'type': 'datetime',
                },
                'width': 15,
            },
            '14_picking_date': {
                'header': {
                    'value': _('Picking Date'),
                },
                'data': {
                    'value': self._render('object.date_picking'),
                    'type': 'datetime',
                },
                'width': 15,
            },
            '15_picking_number': {
                'header': {
                    'value': _('Picking Number'),
                },
                'data': {
                    'value': self._render('object.picking_id.name'),
                },
                'width': 15,
            },
            '16_budget_type': {
                'header': {
                    'value': _('Budget Type'),
                },
                'data': {
                    'value': self._render('object.budget_type'),
                },
                'width': 15,
            },
            '17_source_budget_code': {
                'header': {
                    'value': _('Source of Budget Code'),
                },
                'data': {
                    'value': self._render('object.budget.code'),
                },
                'width': 15,
            },
            '18_source_budget_name': {
                'header': {
                    'value': _('Source of Budget Name'),
                },
                'data': {
                    'value': self._render('object.budget.name'),
                },
                'width': 20,
            },
            '19_owner_code': {
                'header': {
                    'value': _('Owner Code'),
                },
                'data': {
                    'value': self._render('object.owner_budget.code'),
                },
                'width': 15,
            },
            '20_owner_name': {
                'header': {
                    'value': _('Owner Name'),
                },
                'data': {
                    'value': self._render('object.owner_budget.name'),
                },
                'width': 20,
            },
            '21_cost_center_code': {
                'header': {
                    'value': _('Cost Center Code'),
                },
                'data': {
                    'value':
                        self._render('object.owner_budget.costcenter_id.code'),
                },
                'width': 15,
            },
            '22_cost_center_name': {
                'header': {
                    'value': _('Cost Center Name'),
                },
                'data': {
                    'value':
                        self._render('object.owner_budget.costcenter_id.name'),
                },
                'width': 20,
            },
            '23_fund_owner': {
                'header': {
                    'value': _('Fund of Owner'),
                },
                'data': {
                    'value': self._render('", ".join(x for x in \
                        object.owner_budget.fund_ids.mapped("name"))'),
                },
                'width': 10,
            },
            '24_division': {
                'header': {
                    'value': _('Division'),
                },
                'data': {
                    'value': self._render(
                        'object.owner_section_id.division_id.name'),
                },
                'width': 15,
            },
            '25_subsector': {
                'header': {
                    'value': _('Subsector'),
                },
                'data': {
                    'value': self._render(
                        'object.owner_section_id.subsector_id.name'),
                },
                'width': 15,
            },
            '26_sector': {
                'header': {
                    'value': _('Sector'),
                },
                'data': {
                    'value': self._render(
                        'object.owner_section_id.sector_id.name'),
                },
                'width': 15,
            },
            '27_building': {
                'header': {
                    'value': _('Building'),
                },
                'data': {
                    'value': self._render('object.building_id.name'),
                },
                'width': 10,
            },
            '28_floor': {
                'header': {
                    'value': _('Floor'),
                },
                'data': {
                    'value': self._render('object.floor_id.name'),
                },
                'width': 10,
            },
            '29_room': {
                'header': {
                    'value': _('Room'),
                },
                'data': {
                    'value': self._render('object.room_id.name'),
                },
                'width': 10,
            },
            '30_responsible_person_id': {
                'header': {
                    'value': _('Responsible Person ID'),
                },
                'data': {
                    'value': self._render('object.responsible_user_id.login'),
                },
                'width': 15,
            },
            '31_responsible_person_name': {
                'header': {
                    'value': _('Responsible Person Name'),
                },
                'data': {
                    'value': self._render('object.responsible_user_id.name'),
                },
                'width': 20,
            },
            '32_partner_code': {
                'header': {
                    'value': _('Partner Code'),
                },
                'data': {
                    'value': self._render('object.partner_id.search_key'),
                },
                'width': 15,
            },
            '33_partner_name': {
                'header': {
                    'value': _('Partner Name'),
                },
                'data': {
                    'value': self._render('object.partner_id.name'),
                },
                'width': 20,
            },
            '34_po_number ': {
                'header': {
                    'value': _('PO Number '),
                },
                'data': {
                    'value': self._render('object.purchase_id.name or \
                        object.adjust_id.ship_purchase_id.name'),
                },
                'width': 13,
            },
            '35_pr_number': {
                'header': {
                    'value': _('PR Number'),
                },
                'data': {
                    'value': self._render('object.purchase_request_id.name'),
                },
                'width': 13,
            },
            '36_purchase_method': {
                'header': {
                    'value': _('Purchase Method'),
                },
                'data': {
                    'value': self._render(
                        'object.asset_purchase_method_id.name'),
                },
                'width': 10,
            },
            '37_asset_request_code': {
                'header': {
                    'value': _('Asset Request Code'),
                },
                'data': {
                    'value': self._render('object.doc_request_id.name'),
                },
                'width': 15,
            },
            '38_asset_request_name': {
                'header': {
                    'value': _('Asset Request Name'),
                },
                'data': {
                    'value': self._render('object.doc_request_id.name'),
                },
                'width': 20,
            },
            '39_pr_requester_code': {
                'header': {
                    'value': _('PR Requester Code'),
                },
                'data': {
                    'value': self._render('object.pr_requester_id.login'),
                },
                'width': 10,
            },
            '40_pr_requester_name': {
                'header': {
                    'value': _('PR Requester Name'),
                },
                'data': {
                    'value': self._render('object.pr_requester_id.name'),
                },
                'width': 20,
            },
            '41_pr_approved_date': {
                'header': {
                    'value': _('PR Approved Date'),
                },
                'data': {
                    'value': self._render('object.date_request'),
                    'type': 'datetime',
                },
                'width': 10,
            },
            '42_serial_number ': {
                'header': {
                    'value': _('Serial Number '),
                },
                'data': {
                    'value': self._render('object.serial_number'),
                },
                'width': 15,
            },
            '43_warranty_start_date': {
                'header': {
                    'value': _('Warranty Start Date'),
                },
                'data': {
                    'value': self._render('object.warranty_start_date'),
                    'type': 'datetime',
                },
                'width': 10,
            },
            '44_warranty_expire_date': {
                'header': {
                    'value': _('Warranty Expire Date'),
                },
                'data': {
                    'value': self._render('object.warranty_expire_date'),
                    'type': 'datetime',
                },
                'width': 10,
            },
            '45_fiscal_year': {
                'header': {
                    'value': _('Fiscal Year'),
                },
                'data': {
                    'value': self._render('object.date_start'),
                    'type': 'datetime',
                    'pattern': '%Y',
                },
                'width': 10,
            },
            '46_purchase_value_before_current_fy': {
                'header': {
                    'value': _('Purchase Value Before Current FY'),
                },
                'data': {
                    'value': self._render('object.purchase_before_current'),
                    'type': 'number',
                },
                'width': 15,
            },
            '47_purchase_value_current_fy': {
                'header': {
                    'value': _('Purchase Value Current FY'),
                },
                'data': {
                    'value': self._render('object.purchase_current'),
                    'type': 'number',
                },
                'width': 15,
            },
            '48_purchase_value': {
                'header': {
                    'value': _('Purchase Value'),
                },
                'data': {
                    'value': self._render('object.purchase_value'),
                    'type': 'number',
                },
                'width': 15,
            },
            '49_accum_depre_bf': {
                'header': {
                    'value': _('Accum. Depre B/F'),
                },
                'data': {
                    'value': self._render('object.accumulated_bf'),
                    'type': 'number',
                },
                'width': 15,
            },
            '50_depreciation': {
                'header': {
                    'value': _('Depreciation'),
                },
                'data': {
                    'value': self._render('object.depreciation'),
                    'type': 'number',
                },
                'width': 15,
            },
            '51_accum_depre_cf': {
                'header': {
                    'value': _('Accum. Depre C/F'),
                },
                'data': {
                    'value': self._render(
                        'object.accumulated_bf + object.depreciation'),
                    'type': 'number',
                },
                'width': 15,
            },
            '52_net_book_value': {
                'header': {
                    'value': _('Net Book Value'),
                },
                'data': {
                    'value': self._render('object.purchase_value - \
                        (object.accumulated_bf + object.depreciation)'),
                    'type': 'number',
                },
                'width': 15,
            },
            '53_number_of_years': {
                'header': {
                    'value': _('Number of Years'),
                },
                'data': {
                    'value': self._render('object.method_number'),
                    'type': 'number',
                    'format': self.format_integer_right,
                },
                'width': 7,
            },
            '54_adjustment': {
                'header': {
                    'value': _('Adjustment'),
                },
                'data': {
                    'value': self._render('object.adjust_id.name'),
                },
                'width': 15,
            },
            '55_asset_status': {
                'header': {
                    'value': _('Asset Status'),
                },
                'data': {
                    'value': self._render('object.status.name'),
                },
                'width': 10,
            },
            '56_asset_removal_date': {
                'header': {
                    'value': _('Asset Removal Date'),
                },
                'data': {
                    'value': self._render('object.date_remove'),
                    'type': 'datetime',
                },
                'width': 10,
            },
            '57_asset_state': {
                'header': {
                    'value': _('Asset State'),
                },
                'data': {
                    'value': self._render("dict([\
                        ('draft', 'Draft'), ('open', 'Running'), \
                        ('close', 'Close'), ('removed', 'Removed') \
                        ])[object.state]"),
                },
                'width': 10,
            },
        }
        ws_params = {
            'ws_name': 'Asset Register',  # Sheet name
            'generate_ws_method': '_common_report',
            'title': _('Asset Register - %s') % assets.company_id.name,
            'data_filters': [str(x) for x in sorted(asset_filters.keys())],
            'col_filters': asset_filters,
            'wanted_list': [str(x) for x in sorted(asset_template.keys())],
            'col_specs': asset_template,
        }
        return [ws_params]


AssetRegisterXlsx('report.report_asset_register_xlsx', 'asset.register.report')
