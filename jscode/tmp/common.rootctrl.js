(function() {
  'use strict';

angular.module('web')
    .controller('AppRootController', AppRootController)
    .controller('WelcomeMenuController', WelcomeMenuController)
    .controller('HistorySidebarController', HistorySidebarController)
    .controller('ToolbarController', ToolbarController);

function HistorySidebarController($scope, $rootScope, $log, $mdSidenav, $mdComponentRegistry, hotkeys, keyshortcuts, $timeout)
{
    // Init controller and variables
    $log.debug("Sidebar history controller");
    var self = this;
    self.name = "mysnav";
    self.history = [];

    self.loader = 'hside';

    // SIDEBAR STRANGE BEHAVIOUR
    //http://luxiyalu.com/angular-material-no-instance-found-for-handle-left/
    // so it requires mdComponentRegistry

    self.open = function () {
        $rootScope.loaders[self.loader] = true;
        // Open the bar
        $mdComponentRegistry.when(self.name).then(function(sidenav){
            sidenav.open();
            // Load data with little timeout
            $timeout(function () {
                self.history = getHistoryOfAllTimes();
                $rootScope.loaders[self.loader] = false;
            }, timeToWait);
        });
    };

    // Init keys
    hotkeys.bindTo($scope)
        .add({
            combo: "h",
            description: "Open a sidebar with the list of the actions you did inside the app",
            callback: function() {
                keyshortcuts.openHistorySidebar(event, self);
            }
        });

    //$mdSidenav(self.name).open().then();
    $scope.close = function () {
        $mdComponentRegistry.when(self.name).then(function(sidenav){
          sidenav.close();
        });
    };

}

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

    // Utilities
    $rootScope.goTo = function (element) {
        $state.go(element.state.name, element.params);
    };

    // Passing a global variable
    self.templateDir = templateDir;
    self.customTemplateDir = customTemplateDir;
    self.blueprintTemplateDir = blueprintTemplateDir;

    // Decide if Welcome page is a specific static file
    self.welcomeTemplate = welcomeTemplate;

    // Init the models
    $rootScope.menu = [];
    $rootScope.loaders = {};
    self.load = true;
    // Init data for welcoming page
    $scope.sections = {};

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

    ////////////////////////////
    // HISTORY GLOBAL OBJECT
    $rootScope.goToLastRoute = function () {
        var last = lastRoute();
        $log.debug("Going back to", last.state.name);
        $state.go(last.state.name, last.params);
    }

    $rootScope.$on('$stateChangeSuccess',
      function (event, toState, toParams, fromState, fromParams) {

        // I should save every state change to compile my history.
        var lastRoute = {state: toState, params: toParams};
        //console.log("Current is", toState);

        // To execute only if we are loading the page
        if (temporaryRoutingHistory.length < 1) {
            // Show a circle loader when refreshing the page
            self.initTimer(toState);
        }

        // Push to temporary history
        // (all the action you did after the last time you reloaded the page)
        temporaryRoutingHistory.push(lastRoute);

        //////////////////////
        // Push to cookie
        // 1. get the old elements
        var totalRoutingHistory = getHistoryOfAllTimes();

        var skipAdding = false;
        if (totalRoutingHistory.length > 1) {
            // 2. Skip saving this state if it's identical to the previous one
            var check = totalRoutingHistory[totalRoutingHistory.length-1];
            //console.log("Compare", check, lastRoute);
            skipAdding = (check.state.name == lastRoute.state.name &&
                angular.equals(check.params, lastRoute.params))
        }

        if (!skipAdding) {
            // 3. otherwise push the new element
            totalRoutingHistory.push(lastRoute);
            // 4. now save all data
            setHistoryOfAllTimes(totalRoutingHistory);
        }
            // Note: getHistoryOfAllTimes and setHistoryOfAllTimes
            // are defined in common.globals

        //DEBUG
        //$log.debug("History stacks", temporaryRoutingHistory, totalRoutingHistory);
      }
    )

    ////////////////////////////
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