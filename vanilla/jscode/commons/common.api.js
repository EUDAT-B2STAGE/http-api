(function() {
  'use strict';

angular.module('web')
    .service('api', RestApiService);

function RestApiService($window, $http, $auth, $log) {

    var self = this;

    // This is for development.
    // In production nginx should provide access to 'api' url
    self.API_PORT = 8081;

    self.API_URL =
        window.location.protocol + "//" +
        window.location.host + ':' + self.API_PORT +
        '/api/'
        ;


    self.getOrDefault = function (value, mydefault) {
        return typeof value !== 'undefined' ? value : mydefault;
    }

    self.apiCall = function (endpoint, key, method, data) {

        //DEFAULTS
        endpoint = self.getOrDefault(endpoint, self.endpoints.search);
        if (typeof key !== 'undefined' && method != 'POST') {
            endpoint += '/' + key;
        }
        method = self.getOrDefault(method, 'GET');
        if (method == 'GET') {
            data = {};
        } else {
            data = self.getOrDefault(data, {});
            $log.debug("Sending data", data);
        }

        var token = $auth.getToken();
        var req = {
            method: method,
            url: self.API_URL + endpoint,
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': token,
            },
            data: data,
        }

        return $http(req).then(
            function successCallback(response) {
                $log.debug("API call successful");
                return response.data;
          }, function errorCallback(response) {
                $log.error("API failed to call")
                return response.data;
        });
    }
}

})();