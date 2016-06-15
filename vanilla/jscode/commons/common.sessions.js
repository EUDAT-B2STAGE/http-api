(function() {
  'use strict';

angular.module('web')
    .controller('SessionsController', SessionsController);

function SessionsController($scope, $log, api)
{

	var self = this;

	api.getActiveSessions().then(
		function(response) {
			self.tokens = response
		}
	);
}

})();
