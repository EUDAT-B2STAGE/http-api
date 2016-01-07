(function() {
  'use strict';

angular.module('web').config(config);

// Ui Resolve + Satellizer to authenticate
// source http://j.mp/1VnxlQS
function _skipIfAuthenticated($q, $state, $auth) {
    var defer = $q.defer();
    //console.log("STATE", $state);
/*
    if($auth.isAuthenticated()) {
        defer.reject();
    } else {
        defer.resolve();
    }
*/
        defer.resolve();
    return defer.promise;
}
 
function _redirectIfNotAuthenticated($q, $state, $auth, $timeout) {
    var defer = $q.defer();
    if($auth.isAuthenticated()) {
        defer.resolve();
    } else {
        //console.log("TEST");
        $timeout(function () {
            //console.log("TEST2");
            $state.go('login');
        }); //, 100);
        defer.reject();
    }
    return defer.promise;
}

/*********************************
* ROUTING
*********************************/
function config($stateProvider, $urlRouterProvider, $authProvider, $logProvider, $locationProvider) //, $interpolateProvider)
{

// BASE CONFS
    var framework = 'materialize';
    var templateDirBase = '/static/app/templates/';
    var templateDir = templateDirBase + framework + '/';
    var customTemplateDir = templateDirBase + 'custom/' + framework + '/';
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
/* 
    // In case you want to redirect to external link
    $urlRouterProvider.otherwise(function () {
        window.location.href = '/';
        //$location.path('/helloworld');
        //$location.replace();
    });
*/
/*
    .state("hello", {
        url: "/helloworld",
        resolve: {
            skipIfAuthenticated: _skipIfAuthenticated
        },
        views: {
            "main": {
                controller: function($window) {
                    //Reload python pages
                    console.log("Reload!");
                    $window.location.reload();
                }
            }
        }
    })
*/

}

})();