odoo.define('account.payment.rtl', function (require) {
	"use strict";

	var core = require('web.core');
	var form_common = require('web.form_common');
	var formats = require('web.formats');
	var Model = require('web.Model');
	var account_payment = require('account.payment');

	var QWeb = core.qweb;

	var _t = core._t;

	var reconciliation = require('account.reconciliation');


	var PLWExtend = form_common.AbstractField.extend({
	    render_value: function() {
	        var self = this;
	        var info = JSON.parse(this.get('value'));
	        var invoice_id = info.invoice_id;
	        if (info !== false) {
	            _.each(info.content, function(k,v){
	                k.index = v;
	                k.amount = formats.format_value(k.amount, {type: "float", digits: k.digits});
	                if (k.date){
	                    k.date = formats.format_value(k.date, {type: "date"});
	                }
	            });
	            this.$el.html(QWeb.render('ShowPaymentInfo', {
	                'lines': info.content, 
	                'outstanding': info.outstanding, 
	                'title': info.title
	            }));
	            this.$('.outstanding_credit_assign').click(function(){
	                var id = $(this).data('id') || false;
	                new Model("account.invoice")
	                    .call("assign_outstanding_credit", [invoice_id, id])
	                    .then(function (result) {
	                        self.view.reload();
	                    });
	            });
	            _.each(this.$('.js_payment_info'), function(k, v){
	                var options = {
	                    'content': QWeb.render('PaymentPopOver', {
	                            'name': info.content[v].name, 
	                            'journal_name': info.content[v].journal_name, 
	                            'date': info.content[v].date,
	                            'amount': info.content[v].amount,
	                            'currency': info.content[v].currency,
	                            'position': info.content[v].position,
	                            'payment_id': info.content[v].payment_id,
	                            'move_id': info.content[v].move_id,
	                            'ref': info.content[v].ref,
	                            }),
	                    'html': true,
	                    'placement': 'right',
	                    'title': _t('Payment Information'),
	                    'trigger': 'focus',
	                };
	                $(k).popover(options);
	                $(k).on('shown.bs.popover', function(event){
	                    $(this).parent().find('.js_unreconcile_payment').click(function(){
	                        var payment_id = parseInt($(this).attr('payment-id'))
	                        if (payment_id !== undefined && payment_id !== NaN){
	                            new Model("account.move.line")
	                                .call("remove_move_reconcile", [payment_id])
	                                .then(function (result) {
	                                    self.view.reload();
	                                });
	                        }
	                    });
	                    $(this).parent().find('.js_open_payment').click(function(){
	                        var move_id = parseInt($(this).attr('move-id'))
	                        if (move_id !== undefined && move_id !== NaN){
	                            //Open form view of account.move with id = move_id
	                            self.do_action({
	                                type: 'ir.actions.act_window',
	                                res_model: 'account.move',
	                                res_id: move_id,
	                                views: [[false, 'form']],
	                                target: 'current'
	                            });
	                        }
	                    });
	                });
	            });
	        }
	        else {
	            this.$el.html('');
	        }
	    }

	});


	var bankStatementReconciliation = reconciliation.bankStatementReconciliation.extend({
		bindPopoverTo: function(el) {
	        var self = this;
	        $(el).addClass("bootstrap_popover");
	        el.popover({
	            'placement': 'right',
	            'container': self.el,
	            'html': true,
	            'trigger': 'hover',
	            'animation': false,
	            'toggle': 'popover'
	        });
	    }
	});


	var manualReconciliation = reconciliation.manualReconciliation.extend({
		bindPopoverTo: function(el) {
	        var self = this;
	        $(el).addClass("bootstrap_popover");
	        el.popover({
	            'placement': 'right',
	            'container': self.el,
	            'html': true,
	            'trigger': 'hover',
	            'animation': false,
	            'toggle': 'popover'
	        });
	    }
	});

	var bankStatementReconciliationLine = reconciliation.bankStatementReconciliationLine.extend({
		bindPopoverTo: function(el) {
	        var self = this;
	        $(el).addClass("bootstrap_popover");
	        el.popover({
	            'placement': 'right',
	            'container': self.el,
	            'html': true,
	            'trigger': 'hover',
	            'animation': false,
	            'toggle': 'popover'
	        });
	    }
	});

	core.form_widget_registry.add('payment_rtl', PLWExtend);

	core.action_registry.add('bank_statement_reconciliation_view', bankStatementReconciliation);
	/* This widget takes its parameters from the action context. They are :
	     - statement_ids: list of bank statements to reconcile (if not passed, all unreconciled bank
	            statement lines will be displayed)
	     - notifications: list of {
	            type: one of bootstrap alert types (success, info, warning, danger)
	            message: the message to display,
	            details: a dict containing 'name', 'model' and 'ids' used to call a window action
	        }
	*/

	core.action_registry.add('manual_reconciliation_view', manualReconciliation);
	/* This widget takes its parameters from the action context. They are :
	     - mode : 'customers', 'suppliers', 'others' or 'all' (default 'all')
	     - show_mode_selector : boolean (default true)
	     - partner_ids: list of ids
	     - account_ids: list of ids

	   The mode sets which kind of reconciliations are displayed. Set show_mode_selector to false if the user
	   should not be able to change the mode. partner_ids and account_ids allow to specify items to reconcile,
	   otherwise all items for which there are entries to reconcile are displayed.
	*/

	return {
	    bankStatementReconciliation: bankStatementReconciliation,
	    manualReconciliation: manualReconciliation,
	    bankStatementReconciliationLine: bankStatementReconciliationLine,
	};
});
