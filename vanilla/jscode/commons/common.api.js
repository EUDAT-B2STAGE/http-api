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

    self.endpoints = {
        check: 'verify',
        logged: 'verifylogged',
        admin: 'verifyadmin',
    }


    self.getOrDefault = function (value, mydefault) {
        return typeof value !== 'undefined' ? value : mydefault;
    }

    self.apiCall = function (endpoint, key, method, data, errorCheck) {

        //DEFAULTS
        errorCheck = self.getOrDefault(errorCheck, false);
        endpoint = self.getOrDefault(endpoint, self.endpoints.check);
        if (typeof key !== 'undefined' && method != 'POST') {
            endpoint += '/' + key;
        }
        method = self.getOrDefault(method, 'GET');
        if (method == 'GET') {
            data = {};
        } else {
            data = self.getOrDefault(data, {});
            //$log.debug("Sending data", data);
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
            timeout: 5500,
        }

        return $http(req).then(
            function successCallback(response) {
                //$log.debug("API call successful");
                return response.data;
          }, function errorCallback(response) {
                $log.warn("API failed to call")
                if (errorCheck) {
                    return response;
                } else {
                    // Default: data or null
                    if (typeof response.count === 'undefined') {
                        return null;
                    }
                    return response.data;
                }
        });
    }

    self.verify = function(logged) 
    {
        var endpoint = self.endpoints.check;
        if (logged) {
            endpoint = self.endpoints.logged;
        }
        return self.apiCall(endpoint, undefined, 'GET', {}, true)
            .then(function (response) {
                $log.debug("API verify:", response);
                if (response.status > 250) {
                    // API available
                    return false;
                } else if (response.status < 0) {
                    // API offline
                    return null;
                }
                return true;
            });
    }
}

})();