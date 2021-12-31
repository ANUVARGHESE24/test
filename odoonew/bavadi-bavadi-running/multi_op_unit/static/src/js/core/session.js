odoo.define('multi_op_unit.Session', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var concurrency = require('web.concurrency');
    var core = require('web.core');
    var local_storage = require('web.local_storage');
    var mixins = require('web.mixins');
    var utils = require('web.utils');

    var _t = core._t;
    var qweb = core.qweb;

    var session = require('web.Session')
    var session_context = require('web.session')


    var Session = session.include({
        setOpUnits: function (main_op_unit_id, op_unit_ids) {
            var hash = $.bbq.getState()
            hash.opids = op_unit_ids.sort(function(a, b) {
                //console.log("a n b are: ", a ,b)
                if (a === main_op_unit_id) {
                    //console.log("a is main")
                    return -1;
                } else if (b === main_op_unit_id) {
                    //console.log("b is main")
                    return 1;
                } else {
                    //console.log("else is main", a-b)
                    return a - b;
                }
            }).join(',');
            //console.log("hash.opids is: ", hash.opids, String(main_op_unit_id))
            utils.set_cookie('opids', hash.opids || String(main_op_unit_id));
            $.bbq.pushState({'opids': hash.opids}, 0);

            location.reload();

        },
    });

    return Session;

});


