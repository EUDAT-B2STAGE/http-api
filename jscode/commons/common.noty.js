(function() {
  'use strict';

angular.module('web').service('noty', NotyService);

function NotyService() {

	var self = this;

	self.CRITICAL = 1;
	self.ERROR = 2;
	self.WARNING = 3;
	self.INFO = 4;

	// [label1: msg1, label2: msg2]
	self.showAll = function(messages, type) {
		if (messages)
		for (var i=0; i<messages.length; i++) {
		    var message = messages[i];
		    var label = Object.keys(message).pop();
		    var text = message[label];

		    var m = label+": "+text;

		    if (type == self.CRITICAL) self.showCritical(m);
		    else if (type == self.ERROR) self.showError(m);
		    else if (type == self.WARNING) self.showWarning(m);
		    else if (type == self.INFO) self.showInfo(m);
		    else $log.warn("Unknown message type. NotyService is unable to satisfy this request");
		}
	}

	self.showCritical = function(msg) {

	    var n = noty({
	        text        : msg,
	        type        : "error",
	        dismissQueue: true,
	        modal       : true,
	        maxVisible  : 1,
	        timeout     : 0,
	        force		: true,
	        killer      : true,
	        layout      : 'bottom',
	        theme       : 'defaultTheme'
	    });
	}

	self.showError = function(msg) {

	    var n = noty({
	        text        : msg,
	        type        : "error",
	        dismissQueue: true,
	        modal       : false,
	        maxVisible  : 5,
	        timeout     : 10000,
	        layout      : 'bottom',
	        theme       : 'relax'
	    });
	}

	self.showWarning = function(msg) {

	    var n = noty({
	        text        : msg,
	        type        : "warning",
	        dismissQueue: true,
	        modal       : false,
	        maxVisible  : 3,
	        timeout     : 5000,
	        layout      : 'bottomRight',
	        theme       : 'relax'
	    });
	}

	self.showInfo = function(msg) {

	    var n = noty({
	        text        : msg,
	        type        : "information",
	        dismissQueue: true,
	        modal       : false,
	        maxVisible  : 3,
	        timeout     : 5000,
	        layout      : 'bottomRight',
	        theme       : 'relax'
	    });
	}
	
}

})();
