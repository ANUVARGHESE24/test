odoo.define('op_units.SwitchOpUnitMenu', function(require) {
"use strict";

// alert("Hello")

var config = require('web.config');
var core = require('web.core');
var session = require('web.session');
console.log("Session is: ", session)

var SystrayMenu = require('web.SystrayMenu');
console.log("Systray is: ", SystrayMenu)

var Widget = require('web.Widget');

var _t = core._t;

var SwitchOpUnitMenu = Widget.extend({
    template: 'SwitchOpUnitMenu',
    events: {
        'click .dropdown-item[data-menu] div.log_into': '_onSwitchOpUnitClick',
        'keydown .dropdown-item[data-menu] div.log_into': '_onSwitchOpUnitClick',
        'click .dropdown-item[data-menu] div.toggle_op_unit': '_onToggleOpUnitClick',
        'keydown .dropdown-item[data-menu] div.toggle_op_unit': '_onToggleOpUnitClick',
    },

    init: function () {
        this._super.apply(this, arguments);
        this.isMobile = config.device.isMobile;
        this._onSwitchOpUnitClick = _.debounce(this._onSwitchOpUnitClick, 1500, true);   
        session.user_context['opid'] = session.user_context.allowed_op_unit_ids[0]
    },


    willStart: function () {
        var self = this;
        console.log("session.user_op_units is : ", session.user_op_units)
        console.log("session.user_context: ", session.user_context)

        this.allowed_op_unit_ids = String(session.user_context.allowed_op_unit_ids).split(',').map(function (id) {return parseInt(id);});
        console.log("this.allowed_op_unit_ids is: ", this.allowed_op_unit_ids)

        this.user_op_units = session.user_op_units.allowed_op_units;
        console.log("this.user_op_units  is: ", this.user_op_units )

//        this.current_op_unit = session.user_op_units.current_op_unit;
        this.current_op_unit = this.allowed_op_unit_ids[0];
        console.log("this.current_op_unit is: ", this.current_op_unit)
        session.user_context['opid'] = this.current_op_unit

//        this.current_op_unit_name = this.current_op_unit[1];
        this.current_op_unit_name = _.find(session.user_op_units.allowed_op_units, function (op_unit) {return op_unit[0] === self.current_op_unit;})[1];
        console.log("CURRENT OP_UNIT NAME: ", this.current_op_unit_name)

        return this._super.apply(this, arguments);
    },


    _onSwitchOpUnitClick: function (ev) {
        console.log("ENTERED HERE.........")
        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var dropdownMenu = dropdownItem.parent();
        var op_unitID = dropdownItem.data('op-id');
        console.log("op_unitID IS: ", op_unitID)

        var allowed_op_unit_ids = this.allowed_op_unit_ids;
        if (dropdownItem.find('.fa-square-o').length) {
            // 1 enabled op_unit: Stay in single op_unit mode
            if (this.allowed_op_unit_ids.length === 1) {
                if (this.isMobile) {
                    dropdownMenu = dropdownMenu.parent();
                }
                dropdownMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                allowed_op_unit_ids = [op_unitID];
            } else { // Multi op_unit mode
                allowed_op_unit_ids.push(op_unitID);
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
            }
        }
        $(ev.currentTarget).attr('aria-pressed', 'true');
        session.setOpUnits(op_unitID, allowed_op_unit_ids);
    },


    _onToggleOpUnitClick: function (ev) {
         console.log("ENTERED _onToggleOpUnitClick ...........")
        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var op_unitID = dropdownItem.data('op-id');
        console.log("op_unitID-2 IS: ", op_unitID)

        var allowed_op_unit_ids = this.allowed_op_unit_ids;
//        var current_op_unit_id = allowed_op_unit_ids[0];
        var current_op_unit_id = this.current_op_unit[0];
        if (dropdownItem.find('.fa-square-o').length) {
            console.log("Adding into CHECKED ITEMS.....")
            allowed_op_unit_ids.push(op_unitID);
            dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
            $(ev.currentTarget).attr('aria-checked', 'true');
        } else {
            console.log("Adding into UN-CHECKED ITEMS.....")
            console.log("allowed_op_unit_ids- before: ", allowed_op_unit_ids)
            allowed_op_unit_ids.splice(allowed_op_unit_ids.indexOf(op_unitID), 1);
            console.log("allowed_op_unit_ids: ", allowed_op_unit_ids)
            console.log("allowed_op_unit_ids-session view: ", session.user_op_units.allowed_op_units)
            dropdownItem.find('.fa-check-square').addClass('fa-square-o').removeClass('fa-check-square');
            $(ev.currentTarget).attr('aria-checked', '!is_allowed');
        }
        session.setOpUnits(current_op_unit_id, allowed_op_unit_ids);
    },

});
if (session.display_switch_op_unit_menu) {
    SystrayMenu.Items.push(SwitchOpUnitMenu);
}

return SwitchOpUnitMenu;

});
