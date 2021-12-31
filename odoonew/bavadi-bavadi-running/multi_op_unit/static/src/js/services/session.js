odoo.define('multi_op_unit.session', function (require) {
"use strict";

        var Session = require('web.Session');
        var modules = odoo._modules;
        var session = require('web.session')
        console.log("THE real session is: ", session)
        var utils = require('web.utils');



        var state = $.bbq.getState();
        console.log("state: ", state)
        // If not set on the url, retrieve opids from the local storage
        // or from the default op_unit on the user
        var current_op_id = session.user_op_units.current_op_unit[0]
        console.log("user_context at beginning: ", session.user_context)


        if (!state.opids) {
            console.log("utils.get_cookie('opids'): ", utils.get_cookie('opids'))
            state.opids = utils.get_cookie('opids') !== null ? utils.get_cookie('opids') : String(current_op_id);
            console.log("state.opids: ", state.opids)
        }
        var stateOpIDS = _.map(state.opids.split(','), function (opid) { return parseInt(opid) });
        console.log("stateOpIDS: ", stateOpIDS)
        var userOpIDS = _.map(session.user_op_units.allowed_op_units, function(op_unit) {return op_unit[0]});
        console.log("userOpIDS: ", userOpIDS)
        // Check that the user has access to all the op_units
        if (!_.isEmpty(_.difference(stateOpIDS, userOpIDS))) {
            state.opids = String(current_op_id);
            stateOpIDS = [current_op_id]
        }
        // Update the user context with this configuration
        session.user_context['allowed_op_unit_ids'] = stateOpIDS;
        $.bbq.pushState(state);

        console.log("session in real-session.js: ", session.user_context)

        return session;

});
