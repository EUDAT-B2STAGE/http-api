(function() {
  'use strict';

angular.module('web')
    .config(routeConfig);

/////////////////////////////////
// ROUTES AND AUTHENTICATION

// Ui Resolve + Satellizer to authenticate
// original source http://j.mp/1VnxlQS heavily modified

// Check authentication via Token
function _redirectIfNotAuthenticated($log, $rootScope,
    $state, $auth, $timeout, api)
{
    //console.log("CHECK LOGGED");
    var checkLogged = true;
    return api.verify(checkLogged).then(function(response)
    {
      // Token is available and API confirm that is good
      if (response && $auth.isAuthenticated()) {
        $log.debug("Checked: logged!")
        $rootScope.logged = true;
        return true;
      }
      var state = 'public.login';
      // API not reachable
      if (response === null) {
        state = 'offline';
      } else {
        // Token has expired...
        $auth.removeToken();
        $rootScope.logged = false;
        $log.info("Removed token, because it seems expired.");
      }

      $log.error("Failed resolve. Go to", state);
      // Not logged or API down
      $timeout(function () {
          // redirect
          $state.go(state);
          return false;
      });
    }, function(error) {
        $log.error("Failed with", error);
        $rootScope.logged = false;
        $timeout(function () {
            $state.go('public.login');
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
          //console.log("RESPONSE LOGIN:", response);
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
function routeConfig(
    $stateProvider,
    $logProvider, $locationProvider, $httpProvider, $injector,
    $urlRouterProvider, $authProvider
    )
{

// ROUTER CONFIGURATION

    // Enable log
    $logProvider.debugEnabled(true); //.hashPrefix('!');
    // HTML5 mode: remove hash bang to let url be parsable
    $locationProvider.html5Mode(true);

// Change angular variables from {{}} to [[]] ?
    // $interpolateProvider.startSymbol('[[').endSymbol(']]');

    // Performance:
    // make all http requests that return in around the same time
    // resolve in one digest
    // http://www.toptal.com/angular-js/top-18-most-common-angularjs-developer-mistakes #9b
    $httpProvider.useApplyAsync(true);

    // Faster http requests?
    //http://stackoverflow.com/a/29126922/2114395
    $httpProvider.defaults.headers.common["X-Requested-With"]
        = 'XMLHttpRequest';

////////////////////////////
// WHERE THE MAGIC HAPPENS

    // Dinamically inject the routes from the choosen blueprint

    var extraRoutes = null;
    var extraRoutesSize = 0;
    var blueprintRoutes = blueprint + 'Routes';
    try {
        extraRoutes = $injector.get(blueprintRoutes);
        extraRoutesSize = Object.keys(extraRoutes).length;
        console.log("Loaded extra routes:", blueprintRoutes);
    } catch(e) {
        console.log("Error! Failed to find a JS object to define extra routes." +
            "\nIt should be called '" + blueprintRoutes + "'");
    }

    // Build the routes from the blueprint configuration
    if (extraRoutesSize > 0) {
        forEach(extraRoutes, function(x, stateName){

            // Build VIEWS for this single state
            var myViews = {};
            forEach(x.views, function(view, viewName){
                var dir = templateDir;
                if (view.dir == 'custom') {
                    dir = customTemplateDir;
                } else if (view.dir == 'blueprint') {
                    dir = blueprintTemplateDir;
                }
                myViews[viewName] = {templateUrl: dir + view.templateUrl};
            });

            var finalRoute = {
                url: x.url,
                params: x.params,
                views: myViews,
                // ON ENTER AND EXIT
                onEnter: x.onEnter,
                onExit: x.onExit,
            };

            // Add provider state to the ui router ROUTES
            $stateProvider.state(stateName, finalRoute);
        });
    }
////////////////////////////

// ROUTES
$stateProvider

// Welcome page
    .state("welcome", {
        url: "/welcome",
        views: {
            // "menu": {
            //     templateUrl: templateDir + 'intro_menu.html',
            // },
            // "sidebar": {
            //     templateUrl: templateDir + 'history_sidenav.html',
            // },
            "main": {
                templateUrl: templateDir + 'welcome.html',
            }
        }
    })

// If i find out that APIs are not available...
    .state("offline", {
        url: "/offline",
        views: {
            "main": {templateUrl: templateDir + 'offline.html'}
        }
    })

// A public state
    .state("public", {
        url: "/public",
        resolve: {
            skip: _skipAuthenticationCheckApiOnline,
        },
        views: {
            // "menu": {
            //     templateUrl: templateDir + 'menu.html',
            // },
            // "sidebar": {
            //     templateUrl: templateDir + 'history_sidenav.html',
            // },
            "main": {
                template: "<div ui-view='unlogged'></div>",
            }
        }
    })


// To log the user in
    .state("public.login", {
        url: "/login",
        views: {
            "unlogged": {templateUrl: templateDir + 'login.html'}
        }
    })

// To log the user in
    .state("public.register", {
        url: "/register",
        views: {
            "unlogged": {templateUrl: templateDir + 'registration.html'}
        }
    })

// Base for the app views
    .state("logged", {
        url: "/app",
        // This parent checks for authentication and api online
        resolve: {
            redirect: _redirectIfNotAuthenticated
        },
        // Implement main route for landing page after login
        views: {
            // "menu": {
            //     templateUrl: templateDir + 'menu.html',
            //     //controller: 'AppRootController',
            // },
            // "sidebar": {
            //     templateUrl: templateDir + 'history_sidenav.html',
            // },
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

// TO FIX: move it to custom routing somehow
// Missing bar on some routes
    $urlRouterProvider.when("/app/search", "/app/search/");
    $urlRouterProvider.when("/app/admin", "/app/admin/");

// Ui router kinda bug fixing
// CHECK THIS IN THE NEAR FUTURE
//https://github.com/angular-ui/ui-router/issues/1022#issuecomment-50628789
    // $urlRouterProvider.otherwise('/login');
    $urlRouterProvider.otherwise(function ($injector) {
        console.log("OTHERWISE");
        var $state = $injector.get('$state');
        //return $state.go('login');
        return $state.go('welcome');
    });

}   // END ROUTES

})();