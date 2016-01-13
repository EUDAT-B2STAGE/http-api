(function() {
'use strict';

angular.module('web')
 .constant('rethinkRoutes',

// EXTRA ROUTES
    {

    //////////////////////
        'logged.submit': {
            url: "/submit",
            // resolve: {
            //     skipAuhtenticationCheck: false,
            //     redirectIfNotAuthenticated: true,
            // },
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
