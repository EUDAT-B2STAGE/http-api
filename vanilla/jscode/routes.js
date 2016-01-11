(function() {
  'use strict';

angular.module('web').config(config);

/*********************************
* ROUTING
*********************************/
function config($stateProvider, $urlRouterProvider, $authProvider, $logProvider, $locationProvider, $injector)
{

    var extraRoutes = $injector.get(blueprint + 'Routes');
    console.log("Dynamic inject", blueprint, extraRoutes);

    forEach(extraRoutes, function(element, index){
        console.log(index, element);
    });

	// Enable log
	$logProvider.debugEnabled(true); //.hashPrefix('!');
    // HTML5 mode: remove hash bang to let url be parsable
    $locationProvider.html5Mode(true);
    // Change angular variables from {{}} to [[]]
    //$interpolateProvider.startSymbol('[[').endSymbol(']]');

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
                //template: '<br><h1>test</h1> [[angular]]',
                templateUrl: templateDir + 'login.html',
                controller: 'LoginController',
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

//$urlRouterProvider.otherwise('/login');

// Ui router kinda bug fixing
// CHECK THIS IN THE NEAR FUTURE
//https://github.com/angular-ui/ui-router/issues/1022#issuecomment-50628789
    $urlRouterProvider.otherwise(function ($injector) {
        var $state = $injector.get('$state');
        return $state.go('login');
    });

}

})();