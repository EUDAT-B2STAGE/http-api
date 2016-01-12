(function() {
  'use strict';

angular.module('web').config(config);

/*********************************
* ROUTING
*********************************/
function config($stateProvider, $urlRouterProvider, $authProvider, $logProvider, $locationProvider, $httpProvider, $injector)
{

// WHERE THE MAGIC HAPPENS

    // Dinamically inject the routes from the choosen blueprint
    var extraRoutes = $injector.get(blueprint + 'Routes');
    console.log("Dynamic inject", blueprint, extraRoutes);

    // Build the routes from the blueprint configuration
    forEach(extraRoutes, function(x, stateName){
        //console.log(stateName, x);

        // Build resolver of this single state
        var myResolve = {};
        if (x.resolve.skipAuhtenticationCheck) {
            myResolve['skipIfAuthenticated'] = _skipIfAuthenticated;
        } else if (x.resolve.redirectIfNotAuthenticated) {
            myResolve['redirectIfNotAuthenticated'] = _redirectIfNotAuthenticated;
        }

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
            resolve: myResolve,
            views: myViews,
        });
    });

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

// ROUTES
$stateProvider
    ////////////////////////////

    .state("login", {
        url: "/login",
        resolve: {
            skipIfAuthenticated: _skipIfAuthenticated
        },
        views: {
            "main": {
                templateUrl: templateDir + 'login.html',
                //controller: 'LoginController',
            }
        }
    })
    .state("logged", {
        url: "/app",
        resolve: {
            redirectIfNotAuthenticated: _redirectIfNotAuthenticated
            //logginer: function($auth) {
        },
        // Implement main route for landing page after login
        views: {
            "menu": {
                templateUrl: templateDir + 'menu.html',
                controller: 'AppRootController',
            },
            "main": {
        // and add a child view called 'loggedview' for logged pages
                templateUrl: templateDir + 'logged.html',
                //controller: 'AppRootController',
            }
        },
    })

    .state('logged.submit', {
        url: "/submit",
        views: {
            "loggedview": {
                templateUrl: templateDir + 'home.html',
                controller: 'MainController',
            }
        },
    })

    .state('logged.search', {
        url: "/search",
        views: {
            "loggedview": {
                templateUrl: customTemplateDir + 'search.html',
                controller: 'SearchController',
            }
        },
    })

    .state('logged.details', {
        url: "/details/:id",
        views: {
            "loggedview": {
                templateUrl: customTemplateDir + 'details.html',
                controller: 'DetailsController',
            }
        },
    })

    .state("logged.logout", {
        url: "/logout",
        views: {
            "loggedview": {
                templateUrl: templateDir + 'logout.html',
                controller: 'LogoutController',
            }
        }
    })

    // Routes definition end
    ;

$urlRouterProvider.otherwise('/login');

/*
// Ui router kinda bug fixing
// CHECK THIS IN THE NEAR FUTURE
//https://github.com/angular-ui/ui-router/issues/1022#issuecomment-50628789
    $urlRouterProvider.otherwise(function ($injector) {
        var $state = $injector.get('$state');
        return $state.go('login');
    });
*/

}   // END CONFIG

})();