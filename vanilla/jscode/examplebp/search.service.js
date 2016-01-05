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

    var SEARCH_ENDPOINT = 'datavalues';
    var SUBMIT_ENDPOINT = 'datakeys';
    var DOCUMENTS_ENDPOINT = 'docs';
    var USERS_ENDPOINT = 'accounts';

    self.getOrDefault = function (value, mydefault) {
        return typeof value !== 'undefined' ? value : mydefault;
    }

    self.apiCall = function (endpoint, key, method, data) {

        //DEFAULTS
        endpoint = self.getOrDefault(endpoint, SEARCH_ENDPOINT);
        if (typeof key !== 'undefined') {
            endpoint += '/' + key;
        }
        method = self.getOrDefault(method, 'GET');
        if (method == 'GET') {
            data = {};
        }
        data = self.getOrDefault(data, {});

        var token = $auth.getToken();
        var req = {
            method: method,
            url: API_URL + endpoint,
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': token,
            },
            data: data,
        }
        console.log("DATA", data);

        return $http(req).then(
            function successCallback(response) {
                $log.debug("API call successful");
                return response.data;
          }, function errorCallback(response) {
                $log.error("API failed to call")
                return response.data;
        });
    }

    // All possible calls
    self.getData = function() {
        return self.apiCall(SEARCH_ENDPOINT);
    }

    self.getSingleData = function(id) {
        return self.apiCall(SEARCH_ENDPOINT, id);
    }

    self.getSteps = function(id) {
        return self.apiCall(SUBMIT_ENDPOINT);
    }

}

})();
