(function() {
  'use strict';

angular.module('web')
    .controller('AppRootController', AppRootController);

function AppRootController($scope, $rootScope, $log, $state, $timeout,api)
{
    // Init controller
    var self = this;
    $log.debug("Root controller");

    // Init the models
    $rootScope.menu = [];
    self.load = true;

    // Passing a global variable
    self.templateDir = templateDir;
    self.customTemplateDir = customTemplateDir;
    self.blueprintTemplateDir = blueprintTemplateDir;

    // Let this login load after a little while
    $rootScope.loadTimer = $timeout(function() {

        // Do we need extra time to show the page?
        var moreTime = 1;
        if (!checkLoggedState($state.current) && api.checkToken() !== null) {
            if ($state.current.name == 'login') {
                // Avoid the user to see the reload of the page
                moreTime = 500;
                $log.debug("More time", moreTime);
            }
            $state.go('logged');
        }
        // Show the page content
        $timeout(function() {
            self.load = false;
        }, moreTime);
    }, timeToWait);

    // Control states to create the menu
    var myObj = $state.get();

    // Handling logged states
    var loggedKey = 'logged.';
    function checkLoggedState(stateName) {
        return (stateName.name.slice(0, loggedKey.length) == loggedKey);
    }

    // DO THE MENU
	forEach(myObj, function (x, i) {
        //$log.debug("Menu element", i , x);

        if (x.name.slice(loggedKey.length).indexOf('.') < 0
            && x.url.indexOf(':') < 0)
        {
        // Skip if:
            // a - the view is a sub child
            // b - there is a parameter into the url (so direct link won't work)

    		if (checkLoggedState(x)) {
                var name = x.name.substr(loggedKey.length);
                if (name != 'specialsearch') {
                    $rootScope.menu.push(name.capitalizeFirstLetter());
                }
    		}
        }
	});

    // In case of special search available
    // Redirect to that state
    $rootScope.activateSearch = function ()
    {
        $state.go('logged.specialsearch');
    }

	$log.info("Menu", $rootScope.menu);

}

})();