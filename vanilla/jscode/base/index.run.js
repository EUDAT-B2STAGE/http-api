(function() {
  'use strict';


	angular.module('web').run(runBlock);

	function runBlock($log) {
		$log.debug('The RUN block');
	}

})();
