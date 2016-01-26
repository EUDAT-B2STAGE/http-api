(function() {
  'use strict';

angular.module('web')
    .controller('AppRootController', AppRootController)
    .controller('ToolbarController', ToolbarController);

function ToolbarController($scope, $log, $rootScope)
{
    var self = this;
    $log.debug("Toolbar controller");
    var color = 'cyan darken-3';
    $rootScope.originalColor = angular.copy(color);
    $rootScope.toolbarColor = angular.copy(color);
    self.shade = 'z-depth-2';
}

function AppRootController($scope, $rootScope, $log, $state, $timeout, api, hotkeys, keyshortcuts)
{
    // Init controller
    var self = this;
    $log.debug("Root controller");

    // Init keys
    hotkeys.bindTo($scope)
        .add({
            combo: "/",
            description: "Use quick search form",
            callback: function() {
                keyshortcuts.search(event, self);
            }
        });

    // Init the models
    $rootScope.menu = [];
    self.load = true;

    // Passing a global variable
    self.templateDir = templateDir;
    self.customTemplateDir = customTemplateDir;
    self.blueprintTemplateDir = blueprintTemplateDir;

    self.initTimer = function () {
        // Do not wait on intro page
        self.intro = ($state.current.name == 'welcome');
        if (self.intro) { timeToWait = 0; }

        // Check if not logged state and not authorized
        if (!checkLoggedState($state.current) && api.checkToken() !== null)
        {
            // If login page, we need extra time
            if ($state.current.name == 'login') {
                // Avoid the user to see the reload of the page
                timeToWait += 500;
                $log.debug("More time", moreTime);
            }
            // If welcome page, don't do anything
            if (!self.intro) {
                // Try to force logging
                $state.go('logged');
            }
        }

        $log.debug("Load page timeout:", timeToWait);

        // Let this login load after a little while
        $rootScope.loadTimer = $timeout(function() {
            // Show the page content
            self.load = false;
        }, timeToWait);
    }

    $timeout(self.initTimer);

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