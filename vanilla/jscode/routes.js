(function() {
  'use strict';

angular.module('web').config(config);

/////////////////////////////////
// ROUTES AND AUTHENTICATION

// Ui Resolve + Satellizer to authenticate
// original source http://j.mp/1VnxlQS heavily modified

// Check authentication via Token
function _redirectIfNotAuthenticated($state, $auth, $timeout, $log, api)
{
    var checkLogged = true;
    return api.verify(checkLogged).then(function(response){
      // Token is available and API confirm that is good
      if (response && $auth.isAuthenticated()) {
        return true;
      }
      var state = 'login';
      // API not reachable
      if (response === null) {
        state = 'offline';
      }
      // Not logged or API down
      $timeout(function () {
          // redirect
          $log.error("Failed resolve");
          $state.go(state);
          return false;
      });
    });
}

// Skip authentication
// Check for API available
function _skipAuthenticationCheckApiOnline($state, $timeout, $auth, api)
{
    var checkLogged = false;
    return api.verify(checkLogged)
      .then(function(response){

        // API available
        if (response) {
          return response;
        }
        // Not available
        $timeout(function () {
            $state.go('offline');
            return response;
        });
    });
}


/*********************************
* ROUTING
*********************************/
function config($stateProvider, $urlRouterProvider, $authProvider, $logProvider, $locationProvider, $httpProvider, $injector)
{

// ROUTER CONFIGURATION

    // Enable log
    $logProvider.debugEnabled(true); //.hashPrefix('!');
    // HTML5 mode: remove hash bang to let url be parsable
    $locationProvider.html5Mode(true);

    // // Change angular variables from {{}} to [[]]
    // $interpolateProvider.startSymbol('[[').endSymbol(']]');

    // Performance:
    // make all http requests that return in around the same time
    // resolve in one digest
    // http://www.toptal.com/angular-js/top-18-most-common-angularjs-developer-mistakes #9b
    $httpProvider.useApplyAsync(true);

    // Faster http requests?
    //http://stackoverflow.com/a/29126922/2114395
    $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';

////////////////////////////
// WHERE THE MAGIC HAPPENS

    // Dinamically inject the routes from the choosen blueprint
    var extraRoutes = $injector.get(blueprint + 'Routes');
    var extraRoutesSize = Object.keys(extraRoutes).length;
    console.log("[DEBUG] DynamicInject:", blueprint, extraRoutes);

    // Build the routes from the blueprint configuration
    if (extraRoutesSize > 0) {
        forEach(extraRoutes, function(x, stateName){

            // Build VIEWS for this single state
            var myViews = {};
            forEach(x.views, function(view, viewName){
                var dir = templateDir;
                if (view.dir == 'custom') {
                    dir = customTemplateDir;
                }
                myViews[viewName] = {templateUrl: dir + view.templateUrl};
            });

            // Add provider state to the ui router ROUTES
            $stateProvider.state(stateName, {
                url: x.url,
                //resolve: myResolve,
                views: myViews,
            });
        });
    }
////////////////////////////

// ROUTES
$stateProvider

    .state("offline", {
        url: "/offline",
        views: {
            "main": {templateUrl: templateDir + 'offline.html'}
        }
    })

    .state("login", {
        url: "/login",
        resolve: {
            skip: _skipAuthenticationCheckApiOnline,
        },
        views: {
            "main": {templateUrl: templateDir + 'login.html'}
        }
    })

    .state("logged", {
        url: "/app",
        // This parent checks for authentication and api online
        resolve: {
            redirect: _redirectIfNotAuthenticated
        },
        // Implement main route for landing page after login
        views: {
            "menu": {
                templateUrl: templateDir + 'menu.html',
                //controller: 'AppRootController',
            },
            "main": {
        // and add a child view called 'loggedview' for logged pages
                templateUrl: templateDir + 'logged.html',
                //controller: 'AppRootController',
            }
        },
    })

    .state("logged.logout", {
        url: "/logout",
        views: {
            "loggedview": {templateUrl: templateDir+'logout.html'}
        }
    })

    // Routes definition ends here
    ;


// Ui router kinda bug fixing
// CHECK THIS IN THE NEAR FUTURE
//https://github.com/angular-ui/ui-router/issues/1022#issuecomment-50628789
    // $urlRouterProvider.otherwise('/login');
    $urlRouterProvider.otherwise(function ($injector) {
        console.log("OTHERWISE");
        var $state = $injector.get('$state');
        return $state.go('login');
    });

}   // END CONFIG

})();