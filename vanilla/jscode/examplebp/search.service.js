(function() {
  'use strict';

angular.module('web')
    .service('search', SearchService);

function SearchService($window, $http, $auth, $log) {

    var self = this;

    var API_PORT = 8081;
    var API_URL =
        window.location.protocol + "//" + 
        window.location.host + ':' + API_PORT + 
        '/api/'
        ;

    var SEARCH_ENDPOINT = 'newstepscontent';
    //var SEARCH_ENDPOINT = 'datakeys';
    var SUBMIT_ENDPOINT = 'newsteps';
    //var SUBMIT_ENDPOINT = 'datavalues';
    var DOCUMENTS_ENDPOINT = 'docs';
    var USERS_ENDPOINT = 'accounts';

    self.getData = function(content) {
        var token = $auth.getToken();
        var req = {
            method: 'GET',
            url: API_URL + SEARCH_ENDPOINT,
            headers: {
                'Authentication-Token': token,
            }
        }

        return $http(req).then(
            function successCallback(response) {
                $log.debug("API search call successful");
                return response.data;
          }, function errorCallback(response) {
                $log.error("Failed to call")
                return response.data;
        });
    }

}

})();
