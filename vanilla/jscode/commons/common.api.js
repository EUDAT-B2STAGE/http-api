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
    self.checkToken = function () {
        return $auth.getToken();
    }

    self.apiCall = function (endpoint, method, data, id, errorCheck) {


      ////////////////////////
        //DEFAULTS
        errorCheck = self.getOrDefault(errorCheck, false);
        endpoint = self.getOrDefault(endpoint, self.endpoints.check);
        if (typeof id !== 'undefined' && method != 'POST') {
            endpoint += '/' + id;
        }
        method = self.getOrDefault(method, 'GET');
        var params = {};
        if (method == 'GET') {
            params = self.getOrDefault(data, {});
            data = {};
        } else if (method == 'POST') {
            data = self.getOrDefault(data, {});
        }
      ////////////////////////

        var token = self.checkToken(),
            timeout = 5500,
            req = {
                method: method,
                url: self.API_URL + endpoint,
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': token,
                },
                data: data,
                params: params,
                timeout: timeout,
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
        return self.apiCall(endpoint, 'GET', undefined, undefined, true)
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