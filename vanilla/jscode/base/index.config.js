(function() {
  'use strict';

angular.module('web')
    .config(config);

function config($routeProvider, $locationProvider, $logProvider)
{
    $locationProvider.html5Mode(true);
    $logProvider.debugEnabled(true); //.hashPrefix('!');
    console.log("TEST 1");
    $routeProvider
        .when('/test', {
            templateUrl: '/static/app/templates/home.html',
            controller: 'MainController'
        })
        .otherwise({ redirectTo: '/test' });
    console.log("TEST 2");
}

/* UI ROUTER?
    function config(
        $logProvider, $locationProvider, $interpolateProvider,
        $stateProvider, $urlRouterProvider)
    {
    	// Enable log
    	$logProvider.debugEnabled(true); //.hashPrefix('!');
        // HTML5 mode: remove hash bang to let url be parsable
        $locationProvider.html5Mode(true);
        // Change angular variables from {{}} to [[]]
        $interpolateProvider.startSymbol('[[').endSymbol(']]');

        $stateProvider
            .state('home', {
                url: "/",
                views: {
                    "main": {
                        template: 'Home page<br><a ui-sref="data">link</a>.',
                        controller: 'MainController',
                    }
                },
            })

            ////////////////////////////
            .state("login", {
                url: "/login",
                 views: {
                    "main": {
                        //template: '<br><h1>test</h1> [[angular]]',
                        templateUrl: '/static/app/templates/login.html',
                        controller: 'LoginController',
                    }
                }
            })
            .state("logout", {
                url: "/logout",
                 views: {
                    "main": {
                        templateUrl: '/static/app/templates/logout.html',
                        controller: 'LoginController',
                    }
                }
            })
            .state("logged", {
                url: "/app",
                 views: {
                    "main": {
                        template: '<b>Logged</b>!!!',
                        controller: 'MainController',
                    }
                }
            })
            ////////////////////////////

            .state("data", {
                url: "/data",
                views: {
                    "main": {
                        template: 'Welcome to data page <div ui-view="id"></div>',
                        controller: 'DataController',

                    }
                }
                })
           .state("data.id", {
                url: "/:id",
                views: {
                    "id": {
                        template: '<h1>id = [[id]]</h1>',
                        controller: 'DataIDController',

                    }
                },
            });


        $urlRouterProvider.otherwise('/notfound');
    }
*/

})();