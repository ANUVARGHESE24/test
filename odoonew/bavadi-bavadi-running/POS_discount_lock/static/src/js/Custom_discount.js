odoo.define('pos_lock_mode.discount_lock_mode', function (require) {
    "use strict";

        var core = require('web.core');
        var screens = require('point_of_sale.screens');
        var models = require('point_of_sale.models');
        var field_utils = require('web.field_utils');
        var pos_screens = require('pos_discount.pos_discount');
        var _t = core._t;

        pos_screens.DiscountButton.include({
        button_click: function(){
        var self=this;
        if (self.pos.config.lock_discount == true){
            self.gui.show_popup('password',{
                                'title': _t('Password ?'),
            confirm: function (pw) {
                            if (pw !== self.pos.config.discount_password) {
                                self.gui.show_popup('error', {
                                    'title': _t('Error'),
                                    'body': _t('Incorrect password. Please try again'),
                                });
                            } else { self.gui.show_popup('number',{
                            'title': _t('Discount Percentage'),
                            'value': this.pos.config.discount_pc,
                            'confirm': function(val) {
                                val = Math.round(Math.max(0,Math.min(100,field_utils.parse.float(val))));
                                self.apply_discount(val);
                            },
                                });
                                }
                            },
            });
        }
        else
        {  this._super.apply(this);
        }
        },
})
});