odoo.define('fbno_pos_custom_button.custom_order_mode', function (require) {
"use strict";


var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var core = require('web.core');
var rpc = require('web.rpc');
var utils = require('web.utils');
var screens = require('point_of_sale.screens');
var field_utils = require('web.field_utils');
var BarcodeEvents = require('barcodes.BarcodeEvents').BarcodeEvents;
var mixins = require('web.mixins');
var Session = require('web.Session');
var Printer = require('point_of_sale.Printer');
var NetworkDevices = require('pos_network_printer.NetworkDevices');
var PrinterMixin = require('point_of_sale.Printer').PrinterMixin;
var QWeb = core.qweb;
var _t = core._t;

var ActionpadWidget = screens.ActionpadWidget;

screens.ActionpadWidget.include({
    renderElement: function() {
        var self = this;
        this._super();
        this.$('.pay').click(function(){
            var order = self.pos.get_order();
            var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                return line.has_valid_product_lot();
            });
            if(!has_valid_product_lot){
                self.gui.show_popup('confirm',{
                    'title': _t('Empty Serial/Lot Number'),
                    'body':  _t('One or more product(s) required serial/lot number.'),
                    confirm: function(){
                        self.gui.show_screen('payment');

                    },
                });
            }else{
                var $order_btn = $(this).parent().parent().find('.order-submit')
                $order_btn.click()
                self.gui.show_screen('payment');
            }
        });

    }

});
});
