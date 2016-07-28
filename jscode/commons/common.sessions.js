(function() {
  'use strict';

angular.module('web')
    .controller('SessionsController', SessionsController);

function SessionsController($scope, $log, $auth, api)
{

	var self = this;

	var token_in_use = $auth.getToken();

	api.getActiveSessions().then(
		function(response) {
			self.tokens = response

			for (var i = 0; i < self.tokens.length; i++) {
				self.tokens[i].inuse = (self.tokens[i].token == token_in_use);
			}

		}
	);
}

})();
