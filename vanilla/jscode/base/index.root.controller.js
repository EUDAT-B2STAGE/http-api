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
		//console.log(x.name.slice(0, key.length));
		if (x.name.slice(0, key.length) == key) {
// TO FIX:
// if state has mandatory params, skip it from MENU
			$scope.menu.push(x.name.substr(7));
		}
	});

	$log.info("Menu", $scope.menu);

}

})();