# -*- coding: utf-8 -*-
import os
from pytz import timezone
from openerp import models, fields, api, _
from openerp.osv import osv
from openerp import SUPERUSER_ID
import datetime
from dateutil.relativedelta import relativedelta as rdelta

DRAFT = 'D'
GENERATE = 'G'
SEND = 'S'
CLOSE = 'C'
XGENERATE = 'X'
XTERMINATION = 'Y'
XDELETE = 'Z'

STATES = [(DRAFT, _("Draft")),
          (GENERATE, _("Generated")),
          (SEND, _("Sending")),
          (CLOSE, _("Closed")),
          (XGENERATE, _("Cancel Generated")),
          (XTERMINATION, _("Termination")),
          (XDELETE, _("Delete"))]
WARRANTY_TYPE = [('D', _("Day")),
                 ('M', _("Month")),
                 ('Y', _("Year"))]
REPORT_NO = 0


class PurchaseContract(models.Model):
    _name = 'purchase.contract'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    def get_admin_id(self):
        Employees = self.env["hr.employee"]
        Emp = Employees.search(
            [['user_id', '=', self._uid]],
            limit=1)
        if Emp:
            return Emp.id
        else:
            return False

    @api.multi
    def get_pd_id(self):
        if 'active_model' in self._context:
            if self._context['active_model'] == 'purchase.requisition':
                return self._context['active_id']
            else:
                return False
        else:
            return False

    @api.multi
    def get_name(self):
        if 'active_model' in self._context and 'active_id' in self._context:
            res_model = self._context['active_model']
            res_id = self._context['active_id']
            PD = self.env[res_model].browse(res_id)
            return PD.objective
        else:
            return False

    @api.multi
    def get_fine_rate(self):
        if 'active_model' in self._context and 'active_id' in self._context:
            res_model = self._context['active_model']
            res_id = self._context['active_id']
            PD = self.env[res_model].browse(res_id)
            purchase = PD.purchase_ids.search(
                [('state', '=', 'done'),
                 ('id', 'in', PD.purchase_ids._ids)], limit=1)
            if purchase:
                if purchase.order_id.fine_condition == "day":
                    return str(purchase.order_id.fine_rate) + " / " + \
                        str(purchase.order_id.fine_condition) + " / " + \
                        str(purchase.order_id.fine_num_days)
                elif purchase.order_id.fine_condition == "date":
                    return str(purchase.order_id.fine_rate) + " / " + \
                        str(purchase.order_id.fine_condition) + " / " + \
                        str(datetime.datetime.strptime(
                            purchase.order_id.date_fine,
                            '%Y-%m-%d').strftime('%m/%d/%y'))
                else:
                    return False
            else:
                return False
        else:
            return False

    @api.multi
    def _compute_fine_rate(self):
        if 'active_model' in self._context and 'active_id' in self._context:
            res_model = self._context['active_model']
            res_id = self._context['active_id']
            if res_model == 'purchase.requisition':
                PD = self.env[res_model].browse(res_id)
                purchase = PD.purchase_ids.search(
                    [('state', '=', 'done'),
                     ('id', 'in', PD.purchase_ids._ids)],
                    limit=1)
                if purchase:
                    if purchase.order_id.fine_condition == "day":
                        self.fine_rate = str(
                            purchase.order_id.fine_rate) + \
                            " / " + str(purchase.order_id.fine_condition) + \
                            " / " + str(purchase.order_id.fine_num_days)
                    elif purchase.order_id.fine_condition == "date":
                        self.fine_rate = str(
                            purchase.order_id.fine_rate) + \
                            " / " + str(purchase.order_id.fine_condition) + \
                            " / " + str(datetime.datetime.strptime(
                                purchase.order_id.date_fine,
                                '%Y-%m-%d').strftime('%m/%d/%y'))
                    else:
                        self.fine_rate = False
                else:
                    self.fine_rate = False
            elif res_model == 'purchase.contract':
                PC = self.env[res_model].browse(res_id)
                self.fine_rate = PC.fine_rate
            else:
                self.fine_rate = False
        else:
            self.fine_rate = False

    @api.multi
    def get_supplier_id(self):
        if 'active_model' in self._context and 'active_id' in self._context:
            res_model = self._context['active_model']
            res_id = self._context['active_id']
            PD = self.env[res_model].browse(res_id)
            purchase = PD.purchase_ids.search(
                [('state', '=', 'done'),
                 ('id', 'in', PD.purchase_ids._ids)], limit=1)
            if purchase.partner_id:
                return purchase.partner_id
            else:
                return False
        else:
            return False

    @api.multi
    def get_contract_amt(self):
        if 'active_model' in self._context and 'active_id' in self._context:
            res_model = self._context['active_model']
            res_id = self._context['active_id']
            PD = self.env[res_model].browse(res_id)
            return PD.total_budget_value
        else:
            return False

    @api.multi
    def get_currency_id(self):
        if 'active_model' in self._context and 'active_id' in self._context:
            res_model = self._context['active_model']
            res_id = self._context['active_id']
            PD = self.env[res_model].browse(res_id)
            return PD.currency_id
        elif self.pd_id:
            return self.pd_id.currency_id
        else:
            return False

    @api.multi
    def _compute_currency_id(self):
        for rec in self:
            if rec.pd_id:
                rec.currency_id = rec.pd_id.currency_id
            elif 'active_model' in self._context and \
                    'active_id' in self._context:
                res_model = self._context['active_model']
                res_id = self._context['active_id']
                PD = self.env[res_model].browse(res_id)
                rec.currency_id = PD.currency_id
            else:
                rec.currency_id = False

    @api.multi
    def get_purchase_type_id(self):
        if self.pd_id:
            return self.pd_id.purchase_type_id.id
        elif 'active_model' in self._context and 'active_id' in self._context:
            res_model = self._context['active_model']
            res_id = self._context['active_id']
            PD = self.env[res_model].browse(res_id)
            return PD.purchase_type_id.id
        else:
            return False

    @api.multi
    def _compute_purchase_type_id(self):
        for rec in self:
            if rec.pd_id:
                rec.purchase_type_id = rec.pd_id.purchase_type_id
            elif 'active_model' in self._context and \
                    'active_id' in self._context:
                res_model = self._context['active_model']
                res_id = self._context['active_id']
                PD = self.env[res_model].browse(res_id)
                rec.purchase_type_id = PD.purchase_type_id
            else:
                rec.purchase_type_id = False

    @api.multi
    def get_purchase_method_id(self):
        if self.pd_id:
            return self.pd_id.purchase_method_id.id
        elif 'active_model' in self._context and 'active_id' in self._context:
            res_model = self._context['active_model']
            res_id = self._context['active_id']
            PD = self.env[res_model].browse(res_id)
            return PD.purchase_method_id.id
        else:
            return False

    @api.multi
    def _compute_purchase_method_id(self):
        for rec in self:
            if rec.pd_id:
                rec.purchase_method_id = rec.pd_id.purchase_method_id
            elif 'active_model' in self._context and \
                    'active_id' in self._context:
                res_model = self._context['active_model']
                res_id = self._context['active_id']
                PD = self.env[res_model].browse(res_id)
                rec.purchase_method_id = PD.purchase_method_id
            else:
                rec.purchase_method_id = False

    @api.multi
    def get_is_central_purchase(self):
        if 'active_model' in self._context and 'active_id' in self._context:
            res_model = self._context['active_model']
            res_id = self._context['active_id']
            PD = self.env[res_model].browse(res_id)
            return PD.is_central_purchase
        elif self.pd_id:
            return self.is_central_purchase
        else:
            return False

    @api.multi
    def _compute_is_central_purchase(self):
        for rec in self:
            if rec.pd_id:
                rec.is_central_purchase = rec.pd_id.is_central_purchase
            elif 'active_model' in self._context and \
                    'active_id' in self._context:
                res_model = self._context['active_model']
                res_id = self._context['active_id']
                PD = self.env[res_model].browse(res_id)
                rec.is_central_purchase = PD.is_central_purchase
            else:
                rec.is_central_purchase = False

    @api.multi
    def get_org_groups_id(self):
        Ext_group = 'base.group_pabi_purchase_contract_user_'
        if self._uid:
            Employees = self.env["hr.employee"]
            Emp = Employees.search(
                [['user_id', '=', self._uid]], limit=1)
            gid = False
            if Emp and self.env.ref(
                'base.group_pabi_purchase_contract_user').id in \
                    self.env.user.groups_id.mapped('id'):
                if Emp.org_id.name_short == 'CT' or \
                        Emp.org_id.name_short == 'CO':
                    gid = self.env.ref(Ext_group + 'central')
                else:
                    if Emp.org_id.name_short:
                        ext_grp = Ext_group + Emp.org_id.name_short.lower()
                        gid = self.env.ref(ext_grp)
                    else:
                        raise osv.except_osv(
                            _(u'Error!!'),
                            _("You do not have permission to create.\n"
                              "Please contact your system administrator."))
                return gid
            else:
                raise osv.except_osv(
                    _(u'Error!!'),
                    _("You do not have permission to create.\n"
                      "Please contact your system administrator."))
        else:
            raise osv.except_osv(
                _(u'Error!!'),
                _("You do not have permission to create."))

    @api.model
    def create(self, vals):
        # Get 2 Digits Org
        formatCode = ""
        Employees = self.env["hr.employee"]
        Orgs = self.env['res.org']
        Emp = Employees.search([['id', '=', vals.get('admin_id', False)]],
                               limit=1)
        Org = Orgs.search([['id', '=', Emp.org_id.id]], limit=1)
        if not Org:
            msg = _('You cannot create PO contract without Org')
            raise osv.except_osv(_(u'Error!'), msg)
        three_mon_rel = rdelta(months=3)
        if vals.get('action_date', False):
            ActionDate = datetime.datetime.strptime(
                vals.get('action_date'), '%Y-%m-%d') + three_mon_rel
        RevNo = vals.get('poc_rev', 0)
        # New Contract (CENTRAL-2016-322-R1)
        if RevNo == 0:
            self.env.cr.execute("SELECT Count(id) AS c"
                                " FROM purchase_contract"
                                " WHERE poc_org = %s"
                                " AND year = %s"
                                " AND poc_rev = 0",
                                (str(Org.code),
                                 str(ActionDate.year)))
            datas = self.env.cr.fetchone()
            CountPO = datas and datas[0] or 0
            running = str(CountPO + 1)
            formatCode = str(Org.code)
            formatCode += '-' + str(ActionDate.year)
            formatCode += '-' + str(running)
        # Reversion (CO-51-2016-322-R1)
        else:
            running = vals.get('running', 0)
            formatCode = str(Org.code)
            formatCode += '-' + str(ActionDate.year)
            formatCode += '-' + str(running)
            vals.update({'poc_rev': RevNo})

        vals.update({'poc_org': str(Org.code)})
        vals.update({'poc_code': formatCode})
        vals.update({'year': str(ActionDate.year)})
        vals.update({'running': running})
        vals.update({'state': GENERATE})
        po_contract = super(PurchaseContract, self).create(vals)
        return po_contract

    @api.multi
    def write(self, vals):
        po_contract = super(PurchaseContract, self).write(vals)
        return po_contract

    @api.multi
    def name_get(self):
        result = []
        for po in self:
            if po.poc_code and po.poc_rev == 0:
                result.append((po.id, "%s" % (po.poc_code or '')))
            elif po.poc_code and po.poc_rev > 0:
                result.append(
                    (po.id, "%s-R%s" % (po.poc_code or '',
                                        str(po.poc_rev) or '')))
        return result

    id = fields.Integer(
        string="id"
    )
    display_code = fields.Char(
        string="PO No.",
        compute='_compute_display_code'
    )
    pd_id = fields.Many2one(
        'purchase.requisition',
        ondelete='set null',
        string="PD Reference",
        default=get_pd_id
    )
    is_verify = fields.Boolean(
        string="Verify",
        default=False
    )
    is_central_purchase = fields.Boolean(
        string="Central Purchase",
        compute='_compute_is_central_purchase',
        track_visibility='onchange',
        default=get_is_central_purchase
    )
    poc_code = fields.Char(
        string="PO No.",
        size=1000,
        readonly=True
    )
    name = fields.Char(
        string="PO Name",
        size=1000,
        requried=True,
        track_visibility='onchange',
        default=get_name
    )
    poc_org = fields.Char(string="Org")
    poc_rev = fields.Integer(
        string="Reversion",
        default=0,
        readonly=True
    )
    admin_id = fields.Many2one(
        "hr.employee",
        ondelete='set null',
        string="Creator",
        default=get_admin_id
    )
    admin_org_groups_id = fields.Many2one(
        'res.groups',
        ondelete='set null',
        string="Org Group",
        domain=[],
        default=get_org_groups_id
    )
    contract_type_id = fields.Many2one(
        'purchase.contract.type',
        ondelete='set null',
        string="Contract Type",
        track_visibility='onchange',
        required=True
    )
    year = fields.Char(
        string="Year",
        size=4,
        readonly=True
    )
    running = fields.Integer(
        string="YearRunning"
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('customer', '=', True)],
        track_visibility='onchange',
        default=get_supplier_id
    )
    action_date = fields.Date(
        string='Action Date',
        required=True,
        track_visibility='onchange'
    )
    start_date = fields.Date(
        string='Start Date',
        required=True,
        track_visibility='onchange'
    )
    end_date = fields.Date(
        string="End Date",
        required=True,
        track_visibility='onchange'
    )
    duration_start2end = fields.Char(
        string="Duration",
        compute='_compute_duration_start2end'
    )
    currency_id = fields.Many2one(
        'res.currency',
        ondelete='set null',
        string="Currency",
        compute='_compute_currency_id',
        track_visibility='onchange',
        default=get_currency_id,
        domain=[('name', 'in', ['THB', 'EUR', 'USD', 'JPY'])]
    )
    num_of_period = fields.Char(
        string="Period",
        size=3,
        required=True,
        track_visibility='onchange',
        default='0'
    )
    purchase_type_id = fields.Many2one(
        'purchase.type',
        string="Type",
        track_visibility='onchange',
        compute='_compute_purchase_type_id',
        method=True,
        store=False,
        default=get_purchase_type_id
    )
    purchase_method_id = fields.Many2one(
        'purchase.method',
        ondelete='set null',
        string="Purchase Method",
        track_visibility='onchange',
        compute='_compute_purchase_method_id',
        method=True,
        store=False,
        default=get_purchase_method_id
    )
    collateral_performance_amt = fields.Float(
        "Collateral performance amount",
        track_visibility='onchange',
        digits=(10, 2)
    )
    contract_amt = fields.Float(
        "Contract amount",
        track_visibility='onchange',
        digits=(10, 2),
        default=get_contract_amt
    )
    collateral_agreement_amt = fields.Float(
        "Collateral agreement amount",
        track_visibility='onchange',
        digits=(10, 2)
    )
    advance_amt = fields.Float(
        "Pay in advance",
        digits=(10, 2)
    )
    collateral_type_id = fields.Many2one(
        "purchase.contract.collateral",
        ondelete="set null",
        string="Collateral type"
    )
    check_final_date = fields.Date(
        "Final inspection period date"
    )
    contractual_fines = fields.Float(
        "Contractual fines",
        digits=(10, 2)
    )
    warranty = fields.Integer("Warranty")
    warranty_type = fields.Selection(
        WARRANTY_TYPE,
        string='Warranty type'
    )
    fine_rate = fields.Char(
        string="Fine Rate",
        compute='_compute_fine_rate',
        default='get_fine_rate'
    )
    collateral_no = fields.Char(
        "Collateral No."
    )
    contractual_amt = fields.Float(
        "Contractual Amount",
        digits=(10, 2))
    collateral_due_date = fields.Date(
        "Collateral Due date"
    )
    collateral_remand_date = fields.Date(
        "Collateral Remand date"
    )
    collateral_remand_real_date = fields.Date(
        "Collateral Remand date(Real)"
    )
    collateral_received_date = fields.Date(
        "Collateral Received date"
    )
    bank = fields.Char("Bank")
    branch = fields.Char("Branch")
    account = fields.Char("Account")
    postdating = fields.Date("Postdating")

    description = fields.Text("Description")
    state = fields.Selection(
        STATES,
        default=DRAFT
    )
    create_date = fields.Datetime("Create Date")
    create_uid = fields.Many2one(
        "res.users",
        ondelete='set null',
        string="Create User"
    )
    write_date = fields.Datetime("Write Date")
    write_uid = fields.Many2one(
        'res.users',
        ondelete='set null',
        string="Write User"
    )
    write_emp_id = fields.Many2one(
        "hr.employee",
        compute='_compute_write_emp_id'
    )
    active = fields.Boolean(
        "Active",
        default=True
    )
    send_uid = fields.Many2one(
        "hr.employee",
        string='Send By'
    )
    send_date = fields.Date('Send Date')
    close_uid = fields.Many2one(
        "hr.employee",
        string='Send By'
    )
    close_date = fields.Date("Send Date")
    verify_uid = fields.Many2one(
        "hr.employee",
        string="Verify By"
    )
    verify_date = fields.Date('Verify Date')
    cancel_uid = fields.Many2one(
        "hr.employee",
        string='Cancel By'
    )
    cancel_date = fields.Date("Cancel Date")
    termination_uid = fields.Many2one(
        "hr.employee",
        string="Termination By"
    )
    termination_date = fields.Date(
        "Termination Date")
    reflow_uid = fields.Many2one(
        "hr.employee",
        string='Reflow By'
    )
    reflow_date = fields.Date('Reflow Date')
    reversion_uid = fields.Many2one(
        "hr.employee",
        string='Reversion By'
    )
    reversion_date = fields.Date('Reversion Date')

    _order = "poc_org asc, year desc, running desc, poc_rev desc"

    @api.v7
    def action_button_verify_doc_v7(self, cr, uid, ids, context=None):
        Employees = self.pool.get("hr.employee")
        Emp = Employees.search([['user_id', '=', self._uid]], limit=1)
        verify_date = datetime.datetime.now(timezone('UTC'))
        if Emp:
            return self.write(cr,
                              uid,
                              ids,
                              {'is_verify': True,
                               'verify_uid': Emp.id,
                               'verify_date': verify_date}
                              )
        return self.write(cr,
                          uid,
                          ids,
                          {'is_verify': True,
                           'verify_uid': False,
                           'verify_date': verify_date})

    @api.multi
    def action_button_send_doc(self):
        attachment = self.env['ir.attachment']
        doc_ids = attachment.search(
            [('res_model', '=', 'purchase.contract'),
             ('res_id', '=', self.id)])
        if doc_ids:
            Employees = self.env["hr.employee"]
            Emp = Employees.search([['user_id', '=', self._uid]],
                                   limit=1)
            if Emp:
                self.send_doc_uid = Emp.id
            else:
                self.send_doc_uid = SUPERUSER_ID
            self.send_doc_date = datetime.datetime.now(timezone('UTC'))
            if self.verify_date:
                self.state = CLOSE
            else:
                self.state = SEND
        else:
            raise osv.except_osv(_(u'Error!!'),
                                 _('Please attachment(s) contract.'))
        return True

    @api.multi
    def action_button_close(self):
        if self.collateral_remand_date and self.collateral_remand_date:
            Employees = self.env["hr.employee"]
            Emp = Employees.search([['user_id', '=', self._uid]],
                                   limit=1)
            if Emp:
                self.close_uid = Emp.id
            else:
                self.close_uid = SUPERUSER_ID
            self.close_date = datetime.datetime.now(timezone('UTC'))
            self.state = CLOSE
        else:
            raise osv.except_osv(
                _(u'Error!!'),
                _("""Please enter
                    \"Collateral Received Date\" and
                    \"Collateral Remand Date\"."""))
        return True

    @api.multi
    def action_button_reflow(self):
        Employees = self.env["hr.employee"]
        Emp = Employees.search([['user_id', '=', self._uid]],
                               limit=1)
        if Emp:
            self.reflow_uid = Emp.id
        else:
            self.reflow_uid = SUPERUSER_ID
        self.reflow_date = datetime.datetime.now(timezone('UTC'))
        self.state = GENERATE
        return True

    @api.multi
    def action_button_verify_doc(self):
        Employees = self.env["hr.employee"]
        Emp = Employees.search([['user_id', '=', self._uid]],
                               limit=1)
        if Emp:
            self.verify_uid = Emp.id
        else:
            self.verify_uid = SUPERUSER_ID
        self.is_verify = True
        self.verify_date = datetime.datetime.now(timezone('UTC'))
        return True

    @api.multi
    def action_button_reversion(self):
        self.env.cr.execute("SELECT Count(id) AS c"
                            " FROM purchase_contract"
                            " WHERE poc_code = '%s'"
                            " AND state = '%s'" %
                            (str(self.poc_code), GENERATE))
        ctnGenerate = self.env.cr.fetchone()
        CountPOGenerate = ctnGenerate and ctnGenerate[0] or 0
        if CountPOGenerate == 0:
            self.env.cr.execute("SELECT Count(id) AS c"
                                " FROM purchase_contract"
                                " WHERE poc_code = '%s'" %
                                (str(self.poc_code)))
            datas = self.env.cr.fetchone()
            CountPORev = datas and datas[0] or 0
            NextRev = CountPORev
            po = self.copy({'poc_rev': NextRev,
                            'state': GENERATE})
            attachment = self.env['ir.attachment']
            doc_ids = attachment.search(
                [('res_model', '=', 'purchase.contract'),
                 ('res_id', '=', self.id)])
            for doc_id in doc_ids:
                tempname = doc_id.name.replace(
                    "_R" + str(NextRev - 1) + ".", "")
                filename, file_extension = os.path.splitext(tempname)
                name = filename + '_R' + str(NextRev) + file_extension
                doc_id.copy(
                    {'res_id': po.id, 'name': name})
            Employees = self.env["hr.employee"]
            Emp = Employees.search([['user_id', '=', self._uid]],
                                   limit=1)
            if Emp:
                self.reflow_uid = Emp.id
            else:
                self.reflow_uid = SUPERUSER_ID
            self.send_doc_date = datetime.datetime.now(timezone('UTC'))
            form = self.env.ref(
                'pabi_purchase_contract.purchase_contract_form_view',
                False
            )
            return {
                'name': 'PO Contract',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': form.id,
                'res_model': 'purchase.contract',
                'domain': [],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': po.id
            }
        else:
            raise osv.except_osv(
                _(u'Can not to be Reversion'),
                _('The contract no. %s has not send documents') %
                (self.poc_code,))

    @api.multi
    def action_button_delete_reversion(self):
        po_code = self.poc_code
        self.unlink()
        po = self.search([['poc_code', '=', str(po_code)]],
                         order="poc_rev desc",
                         limit=1)
        form = self.env.ref(
            'pabi_purchase_contract.purchase_contract_form_view',
            False
        )
        return {'name': 'PO Contract',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': form.id,
                'res_model': 'purchase.contract',
                'domain': [],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': po.id}

    @api.multi
    @api.onchange('admin_id')
    def get_admin_org_groups_id(self):
        Ext_group = 'base.group_pabi_purchase_contract_user_'
        if self.admin_id:
            Employees = self.env["hr.employee"]
            Emp = Employees.search(
                [['user_id', '=', self._uid]], limit=1)
            gid = False
            ext_id = 'base.group_pabi_purchase_contract_user'
            if Emp and self.env.ref(ext_id).id in \
                    self.env.user.groups_id.mapped('id'):
                if Emp.org_id.name_short == 'CT' or \
                        Emp.org_id.name_short == 'CO':
                    gid = self.env.ref(Ext_group + 'central')
                else:
                    if Emp.org_id.name_short:
                        ext_grp = Ext_group + Emp.org_id.name_short.lower()
                        gid = self.env.ref(ext_grp)
                    else:
                        raise osv.except_osv(
                            _(u'Error!!'),
                            _("You do not have permission to create.\n"
                              "Please contact your system administrator."))
                self.admin_org_groups_id = gid
            else:
                self.admin_org_groups_id = False
                self.admin_id = False
                raise osv.except_osv(
                    _(u'Error!!'),
                    _("""You do not have permission to access."""))
        else:
            self.admin_org_groups_id = False
            self.admin_id = False
            raise osv.except_osv(
                _(u'Error!!'),
                _("""You do not have permission to access."""))

    @api.multi
    @api.depends('write_uid')
    def _compute_write_emp_id(self):
        if self.write_uid:
            Employees = self.env["hr.employee"]
            Emp = Employees.search([['user_id', '=', self.write_uid.id]],
                                   limit=1)
            self.write_emp_id = Emp.id
        else:
            self.write_emp_id = False

    @api.multi
    @api.depends('poc_code', 'poc_rev')
    def _compute_display_code(self):
        for rec in self:
            name = False
            if rec.poc_code and rec.poc_rev == 0:
                name = ("%s" % (rec.poc_code or ''))
            elif rec.poc_code and rec.poc_rev > 0:
                name = ("%s-R%s" %
                        (rec.poc_code or '', str(rec.poc_rev) or ''))
            rec.display_code = name

    @api.multi
    @api.onchange('num_of_period')
    def get_num_of_period(self):
        if not self.num_of_period.isdigit():
            self.num_of_period = '0'
        else:
            self.num_of_period = str(int(self.num_of_period))

    @api.multi
    @api.onchange('start_date', 'end_date')
    @api.depends('start_date', 'end_date')
    def _compute_duration_start2end(self):
        start2end = '0 Day'
        if self.start_date and self.end_date:
            if self.start_date <= self.end_date:
                start_date = datetime.datetime.strptime(self.start_date,
                                                        "%Y-%m-%d")
                end_date = datetime.datetime.strptime(self.end_date,
                                                      "%Y-%m-%d")
                start = start_date.date()
                end = end_date.date()
                if end < start:
                    self.duration_start2end = start2end
                    return
                enddate = end + datetime.timedelta(days=1)
                rd = rdelta(enddate, start)
                start2end = str(rd.years)
                start2end += _(' Year ')
                start2end += str(rd.months)
                start2end += _(' Month ')
                start2end += str(rd.days)
                start2end += _(' Day ')
            else:
                start2end = _("** Wrong Date **")
        self.duration_start2end = start2end
