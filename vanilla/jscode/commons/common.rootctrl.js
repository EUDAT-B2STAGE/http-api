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

    // Passing a global variable
    self.templateDir = templateDir;
    self.customTemplateDir = customTemplateDir;
    self.blueprintTemplateDir = blueprintTemplateDir;

    // Init the models
    $rootScope.menu = [];
    self.load = true;

    // Init keys
    hotkeys.bindTo($scope)
        .add({
            combo: "/",
            description: "Use quick search form",
            callback: function() {
                keyshortcuts.search(event, self);
            }
        });

    // Handling logged states
    var loggedKey = 'logged.';
    function checkLoggedState(stateName) {
        return (stateName.name.slice(0, loggedKey.length) == loggedKey);
    }

    self.initTimer = function (current) {

        // Do not wait on intro page
        self.intro = (current.name == 'welcome');
        if (self.intro) { timeToWait = 0; }

        // Check if not logged state and not authorized
        if (!checkLoggedState(current) && api.checkToken() !== null)
        {
            // If login page, we need extra time
            if (current.name == 'login') {
                // Avoid the user to see the reload of the page
                timeToWait += 500;
            }
            // If welcome page, don't do anything
            if (!self.intro) {
                console.log("Going to logged");
                // Try to force logging
                $state.go('logged');
            }
        }

        // Let this login load after a little while
        $log.debug("Load page timeout:", timeToWait);
        $rootScope.loadTimer = $timeout(function() {
            // Show the page content
            self.load = false;
        }, timeToWait);
    }

    $rootScope.$on('$stateChangeSuccess',
      function (event, toState, toParams, fromState, fromParams) {
        console.log("Current is", toState);
        self.initTimer(toState);
      }
    )

    // Control states to create the menu
    var myObj = $state.get();

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