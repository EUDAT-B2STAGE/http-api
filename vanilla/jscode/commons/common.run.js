// I DISABLED THIS CODE BY REMOVING PARENTHESIS AT THE END OF THE FILE
(function() {
  'use strict';

angular.module('web')
    .run(runBlock);

function runBlock($log, $rootScope, $cacheFactory, $templateCache) {
	$log.debug('The RUN block');

    // SPECIFIC FOR UI ROUTER
    // Execute every time a state change begins
    $rootScope.$on('$stateChangeSuccess',
        function (event, toState, toParams, fromState, fromParams) {
            // If the state we are headed to has cached template views
            if (typeof (toState) !== 'undefined'
                && typeof (toState.views) !== 'undefined') {
                // Loop through each view in the cached state
                for (var key in toState.views) {
                    // Delete templeate from cache
                    $log.debug("Delete cached template: " + toState.views[key].templateUrl);
                    $cacheFactory.get('templates')
                        .remove(toState.views[key].templateUrl);
                }
            }
        });

}
})
//();