openerp.language_switcher = function (session) {
    var _t = session.web._t;
    
    /* Extend the Sidebar to add Language Selection links in the 'More' menu */
    session.web.Sidebar = session.web.Sidebar.extend({
    
        init: function(parent) {
            var self = this;
            this._super(parent);
            this.sections.push({ 'name' : 'languages', 'label' : _t('Language'), })
            this.items['languages'] = [];
        },
        
        start: function() {
            var self = this;
            this._super(this);
            var lang_obj = new session.web.Model("res.lang");
            
            var languages_read = lang_obj.call('search_read', [[['active', '=', 'true']], {}]).done(function(res) {
                _.each(res, function(r){
                    self.add_items('languages', [
                        {   label: _t(r.name),
                            callback: self.on_click_lang,
                            classname: r.code },
                    ]);
                })
            });
        },
        
        on_click_lang: function(item) {
            var uid = session.session.uid
            var view = this.getParent()
            var Lang = new session.web.DataSet(self, 'res.lang', view.dataset.get_context());
            var old_this =this;
            
            new session.web.Model("res.users").call('write', [[uid], {'lang': item.classname}, Lang.get_context()]).done(function(r){
                old_this.do_action({'type': 'ir.actions.client', 'tag': 'reload_context',})
            })
        },
    });
}
