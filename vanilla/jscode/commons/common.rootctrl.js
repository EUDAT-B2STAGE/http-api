(function() {
  'use strict';

angular.module('web').controller('AppRootController', AppRootController);

function AppRootController($scope, $log, $state, $timeout, $auth)
{

    // Init controller
    var self = this;
    $log.debug("Root controller");

    // Init the models
    self.menu = [];
    self.load = true;
    // Passing a global variable
    self.templateDir = templateDir;
    self.customTemplateDir = customTemplateDir;

    // Let this login load after a little while
    $timeout(function() {
        var token = $auth.getToken();
        $log.debug("Actual token is:", token);
        if (token !== null) {
            $state.go('logged');
        } else {
        }
        // Show the page content
        self.load = false;
    }, timeToWait);

    // Control states to create the menu
    var myObj = $state.get();
    //console.log(myObj);

	forEach(myObj, function (x, i) {

        //$log.debug("Menu element", i , x);

		var key = 'logged.'
        var prefix = x.name.slice(0, key.length);
        var suffix = x.name.slice(key.length);
        // Skip if:
            // a - the view is a sub child
            // b - there is a parameter into the url (so direct link won't work)
        if (suffix.indexOf('.') < 0 && x.url.indexOf(':') < 0) {
            //console.log(x, i, suffix, suffix.indexOf('.'));
    		if (prefix == key) {
    			self.menu.push(x.name.substr(7).capitalizeFirstLetter());
    		}
        }
	});

	$log.info("Menu", self.menu);

}

})();