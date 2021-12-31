odoo.define('fbno_posback_security.floor_back_button', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var ScreenWidget = screens.ScreenWidget;
var gui = require('point_of_sale.gui');
var core = require('web.core');
var QWeb = core.qweb;
var PopupWidget = require('point_of_sale.popups');
var rpc = require('web.rpc');
var _t  = require('web.core')._t;
var session = require('web.session');
var chrome = require('point_of_sale.chrome');

chrome.OrderSelectorWidget.include({
    floor_button_click_handler: function(){
        var self=this;
        if (self.pos.config.back_button == true){
            self.gui.show_popup('password',{
                                'title': _t('Password ?'),
            confirm: function (pw) {
                            if (pw !== self.pos.config.back_button_password) {
                                self.gui.show_popup('error', {
                                    'title': _t('Error'),
                                    'body': _t('Incorrect password. Please try again'),
                                });
                            } else
                                return this.pos.set_table(null);
                            },
            });
        } else
        {  this._super.apply(this);
        }
    },

});
});
