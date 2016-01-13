(function() {
  'use strict';

angular.module('web').config(config);

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
            //console.log(stateName, x);

/*
UNNECESSARY
            // Build resolver of this single state
            var myResolve = {};
            if (x.hasOwnProperty('resolve') && Object.keys(x.resolve).length > 0) 
            {
                // if you want to check auth
                if (x.resolve.redirectIfNotAuthenticated) {
                    myResolve['checkAuth'] = _redirectIfNotAuthenticated;
                } else {
                    myResolve['skip'] = _skipAuthenticationCheckApiOnline;
                }
            }
*/

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

// ROUTES
$stateProvider
    ////////////////////////////

    .state("offline", {
        url: "/offline",
        views: {
            "main": {
                templateUrl: templateDir + 'offline.html',
            }
        }
    })

    .state("login", {
        url: "/login",
        resolve: {
            skip: _skipAuthenticationCheckApiOnline,
        },
        views: {
            "main": {
                templateUrl: templateDir + 'login.html',
            }
        }
    })

    .state("logged", {
        url: "/app",
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
        // This parent checks for authentication and api online
        resolve: {
            redirect: _redirectIfNotAuthenticated
        },
    })

    .state("logged.logout", {
        url: "/logout",
        views: {
            "loggedview": {
                templateUrl: templateDir + 'logout.html',
            }
        }
    })

    // Routes definition end
    ;

// $urlRouterProvider.otherwise('/login');

// Ui router kinda bug fixing
// CHECK THIS IN THE NEAR FUTURE
//https://github.com/angular-ui/ui-router/issues/1022#issuecomment-50628789
    $urlRouterProvider.otherwise(function ($injector) {
        console.log("OTHERWISE");
        var $state = $injector.get('$state');
        return $state.go('login');
    });

}   // END CONFIG

})();