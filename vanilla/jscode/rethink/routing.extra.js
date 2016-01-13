(function() {
'use strict';

angular.module('web')
 .constant('rethinkRoutes',

// EXTRA ROUTES
    {

    //////////////////////
        'logged.submit': {
            url: "/submit",
            resolve: {
                skipAuhtenticationCheck: false,
                redirectIfNotAuthenticated: true,
            },
            views: {
                "loggedview": {
                    dir: 'base',
                    templateUrl: 'home.html',
                }
            },
        },

    //////////////////////
        'logged.search': {
            url: "/search",
            resolve: {
                skipAuhtenticationCheck: false,
                redirectIfNotAuthenticated: true,
            },
            views: {
                "loggedview": {
                    dir: 'custom',
                    templateUrl: 'search.html',
                }
            },
        },

    //////////////////////
        'logged.details': {
            url: "/details/:id",
            resolve: {
                skipAuhtenticationCheck: false,
                redirectIfNotAuthenticated: true,
            },
            views: {
                "loggedview": {
                    dir: 'custom',
                    templateUrl: 'details.html',
                }
            }
        },

    //////////////////////

    }

 ); // END CONSTANT

})();
