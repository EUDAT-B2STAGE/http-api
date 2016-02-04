(function() {
  'use strict';

angular.module('web')
    .controller('AppRootController', AppRootController)
    .controller('WelcomeMenuController', WelcomeMenuController)
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

function WelcomeMenuController($scope, $log, api, $auth)
{
    $log.debug("Welcome menu");
    var self = this;
    self.buttons = [];

    api.verify(true).then(function(response){
      if (response && $auth.isAuthenticated()) {
        //console.log("Logged");
        self.buttons.push({
            name: 'app',
            link: 'logged',
            icon: 'something',
        });
      } else {
        self.buttons.push({
            name: 'login',
            link: 'login',
            icon: 'profile',
        });
      }
    });
}

function AppRootController($scope, $rootScope, $log, $state, $timeout, api, hotkeys, keyshortcuts)
{
    // Init controller
    var self = this;
    $log.debug("Root controller");
    $rootScope.loaders = [];

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
            // // If welcome page, don't do anything
            // if (!self.intro) {
            //     console.log("Going to logged");
            //     // Try to force logging
            //     $state.go('logged');
            // }
        }

        // Let this login load after a little while
        $log.debug("Load page timeout:", timeToWait);
        $rootScope.loadTimer = $timeout(function() {
            // Show the page content
            self.load = false;
        }, timeToWait);
    }

    self.routesHistory = [];
    $rootScope.$on('$stateChangeSuccess',
      function (event, toState, toParams, fromState, fromParams) {

        // I should save every state change to compile my history.
        var lastRoute = {state: toState, params: toParams};
        //console.log("Current is", toState);

        // To execute only if we are loading the page
        if (self.routesHistory.length < 1) {
            self.initTimer(toState);
        }

        // Push to temporary history
        self.routesHistory.push(lastRoute);
        $log.debug("History stack", self.routesHistory);

        // Push to cookie?
// TO FIX

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