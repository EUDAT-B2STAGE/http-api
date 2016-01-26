(function() {
'use strict';

angular.module('web')
 .constant('rethinkRoutes',

// EXTRA ROUTES
    {

    //////////////////////
        'logged.specialsearch': {
            url: "/search/:text",
            views: {
                "loggedview": {
                    dir: 'blueprint',
                    templateUrl: 'search.html',
                }
            },
            onEnter: function ($rootScope) {
                $rootScope.avoidTheToolbar = true;
            },
            onExit: function ($rootScope) {
                $rootScope.avoidTheToolbar = false;
            },
        },

    //////////////////////
        'logged.details': {
            url: "/details/:id",
            views: {
                "loggedview": {
                    dir: 'blueprint',
                    templateUrl: 'details.html',
                }
            }
        },

    //////////////////////
        'logged.explore': {
            url: "/explore",
            views: {
                "loggedview": {
                    dir: 'blueprint',
                    templateUrl: 'explore.html',
                }
            },
        },

    //////////////////////
        'logged.admin': {
            url: "/admin",
// TO FIX:
// ONLY ADMIN ROLE
            views: {
                "loggedview": {
                    dir: 'blueprint',
                    templateUrl: 'admin.html',
                }
            },
            onEnter: function ($rootScope) {
              $rootScope.toolbarColor = 'red darken-4';
            },
            onExit: function ($rootScope) {
              $rootScope.toolbarColor =
                angular.copy($rootScope.originalColor);
            },
        },

    //////////////////////

    }

 ); // END CONSTANT

})();
