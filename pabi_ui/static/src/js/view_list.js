openerp.pabi_ui = function(instance){

    instance.web.ListView.include({
        load_list: function(data) {
            var self = this;
            var tmp = this._super.apply(this, arguments)
            $('.oe_list_content').attr('class', 'oe_list_content table-bordered')
        }
        
    });

}
