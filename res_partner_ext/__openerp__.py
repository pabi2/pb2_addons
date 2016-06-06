# -*- coding: utf-8 -*-
{
    'name': 'Common Extension of Partner Data',
    'version': '1.0',
    'author': 'Ecosoft',
    'summary': 'Common Extension of Partner Data',
    'description': """

New Fields:
===========

Partner:

* id: Make database ID callable, it will be used to make search_key
* search_key: Partner Code, contructed from ID with 7 digits and is serachable
* name_en: Partner name in English
* vat: Tax ID, 13 digits
* taxbranch: Tax Branc, 5 digits
* create_date: Make create date callable
* single_category_id: Display only 1 partner tag is allowed in this system
* require_taxid: whether Tax ID is required, based on Partner Tag
* require_taxbranch: Whether Tax Branch is required, based on Partner Tag
* is_government: Whether this partner is government, based on Partner Tag

Partner Tag:

* payable_account_id: Partner Tag's default payable account.
* receivable_account_id: Partner Tag's default receivable account.
* require_taxid: Flag, as default value for partner with this tag.
* require_taxbranch: Flag, as default value for partner with this tag.
* fiscal_position_id: For customer with this Partner Tag, use this.
* require_tax_branch_unique: Checking this flag will ensure TaxID+Branch.

Added Feature:
==============

Make sure only 1 Partner Tag can be set for a partner

Check Partner's Tax ID + Tax Branch must be unique for non-government,
which require tax branch unique (set in parter tag)

Check Tax ID must be 13 digits, if required

Check Tax Branch must be 5 digits, if required

Check Partner to have only 2 level max,
Parent and Child (no multi level allowed)

Default Partner to use the same Partner Tag of its parent

Do not allow changing of Partner's Tag, if it result in change of accounting
(system param, no_partner_tag_change_account = True)

Partner field now searchable by many fields, i.e., Tax ID,
Tax Branch, Name (en), Search Key

Partner is a required field if patner in ('customer', supplier') (View level)

    """,
    'category': 'Base',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': ['base'],
    'demo': [],
    'data': ['data/config_data_maintenance.xml',
             'partner_view.xml',
             'security/ir.model.access.csv',
             ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
