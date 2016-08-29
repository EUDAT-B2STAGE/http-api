(function() {
  'use strict';

angular.module('web')
    .controller('MainController', MainController);

function MainController($scope, $rootScope, $log,
    $timeout, $auth ,$state, api
    //, hotkeys, keyshortcuts
    )
{
    // Init controller
    var self = this;
    $log.debug("This is the main controller");

// GLOBAL LOGGED
// USE A WATCH ON SOMETHING
    //$rootScope.logged = false;
/*
    // In case i am already logged, skip
    if ($auth.isAuthenticated())
    {
        $rootScope.logged = true;
    }
*/

    // Passing a global variable
    self.templateDir = templateDir;
    // self.customTemplateDir = customTemplateDir;
    self.blueprintTemplateDir = blueprintTemplateDir;

    var color = 'cyan darken-3';
    self.originalColor = angular.copy(color);
    self.toolbarColor = angular.copy(color);
    self.shade = "md-whiteframe-8dp";
    //self.shade = 'z-depth-2';

/*
    // Utilities
    $rootScope.goTo = function (element) {
        $state.go(element.state.name, element.params);
    };
*/

    // Init the models
    $rootScope.loaders = {};

    self.splash = true;
    $timeout(function () {
        self.splash = false;
    }, 2000);

// SET TO LOAD APIs?
    self.load = false;

/*
    // Init keys
    hotkeys.bindTo($scope)
        .add({
            combo: "/",
            description: "Use quick search form",
            callback: function() {
                keyshortcuts.search(event, self);
            }
        });
*/

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

        if ($rootScope.logged) {
            console.log("Should check LOGIN!");
        }

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

/*
    ////////////////////////////
    // Control states to create the menu
    $rootScope.menu = [];
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
*/

}

})();