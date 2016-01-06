(function() {
  'use strict';

angular.module('web').controller('AppRootController', AppRootController);

function AppRootController($scope, $log, $state)
{
    $scope.menu = [];
    $log.debug("Root controller");

    // Control states to create the menu
    var myObj = $state.get();
    //console.log(myObj);

	forEach(myObj, function (x, i) {
		var key = 'logged.'
        var prefix = x.name.slice(0, key.length);
        var suffix = x.name.slice(key.length);
        // Skip if: 
            // a - the view is a sub child
            // b - there is a parameter into the url (so direct link won't work)
        if (suffix.indexOf('.') < 0 && x.url.indexOf(':') < 0) {
            //console.log(x, i, suffix, suffix.indexOf('.'));
    		if (prefix == key) {
    			$scope.menu.push(x.name.substr(7));
    		}
        }
	});

	$log.info("Menu", $scope.menu);

}

})();