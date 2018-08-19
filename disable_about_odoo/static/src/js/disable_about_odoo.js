(function() {

    "use strict";

    openerp.web.UserMenu.include({
        start: function() {
            var Users = new openerp.web.Model('res.users');
            Users.call('has_group', ['disable_about_odoo.group_developer_mode']).done(function(is_group_developer_mode) {
                if (! is_group_developer_mode) self.$('.dropdown-menu li:has(> a[data-menu="about"])').remove();
            });
            this._super.apply(this, arguments);
        },
    });

    openerp.web.ViewManagerAction.include({
        start: function() {
            var Users = new openerp.web.Model('res.users');
            Users.call('has_group', ['disable_about_odoo.group_developer_mode']).done(function(is_group_developer_mode) {
                if (! is_group_developer_mode) self.$('.oe_debug_view').remove();
            });
            this._super.apply(this, arguments);
        },
    });

})();
