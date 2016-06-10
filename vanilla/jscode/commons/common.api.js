(function() {
  'use strict';

angular.module('web')
    .service('api', RestApiService);

function RestApiService($http, $q, $auth, $log, $mdToast) {

    var self = this;
    // Api URI
    self.API_URL = apiUrl + '/';
    self.AUTH_URL = authApiUrl + '/';
    self.FRONTEND_URL = serverUrl + '/';

    self.endpoints = {
        check: 'status',
        logged: 'profile',
        login: 'login',
        // logout: 'logout',
        logout: 'loggedout',
        admin: 'verifyadmin',
        register: 'doregistration',
    };


    self.getOrDefault = function (value, mydefault) {
        return typeof value !== 'undefined' ? value : mydefault;
    };
    self.checkToken = function () {
        return $auth.getToken();
    };

    self.apiCall = function (endpoint, method, data, id, returnRawResponse, skipPromiseResolve)
    {

      ////////////////////////
        //DEFAULTS
        returnRawResponse = self.getOrDefault(returnRawResponse, false);
        endpoint = self.getOrDefault(endpoint, self.endpoints.check);
        if (typeof id !== 'undefined' && method != 'POST') {
            endpoint += '/' + id;
        }
        method = self.getOrDefault(method, 'GET');
        skipPromiseResolve = self.getOrDefault(skipPromiseResolve, false);

        var params = {};
        if (method == 'GET') {
            params = self.getOrDefault(data, {});
            data = {};
        } else if (method == 'POST') {
            data = self.getOrDefault(data, {});
        }

        var currentUrl = self.API_URL + endpoint;
//////////////////////////////
// WARNING PORCATA
        if (endpoint == 'login' || endpoint == self.endpoints.logged) {
            currentUrl = self.AUTH_URL + endpoint;
        } else if (endpoint == self.endpoints.register
            || endpoint == self.endpoints.logout) {
            currentUrl = self.FRONTEND_URL + endpoint;
        }
//////////////////////////////

        var token = self.checkToken(),
            timeout = 5500,
            req = {
                method: method,
                url: currentUrl,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token,
                },
                data: data,
                params: params,
                timeout: timeout,
            }

        if (skipPromiseResolve) return $http(req);

        return $http(req).then(
            function successCallback(response) {
                //$log.debug("API call successful");

                if (returnRawResponse) return response;

                return response.data.Response;
          }, function errorCallback(response) {
                $log.warn("API failed to call")

                if (returnRawResponse) return $q.reject(response);

                if (!response.data || !response.data.hasOwnProperty('Response')) {
                    return null;
                } else if (typeof response.data.Response === 'undefined') {
                    return null;
                }

                return $q.reject(response.data.Response);
        });
    }

    self.verify = function(logged)
    {
        var endpoint = self.endpoints.check;
        if (logged) {
            endpoint = self.endpoints.logged;
        }
        return self.apiCall(endpoint, 'GET', undefined, undefined, true)
            .then(function successCallback(response) {
                $log.debug("API verify:", response);
                if (response.status < 0) {
                    // API offline
                    return null;
                }
                return response.data.Response.data;
                //return true;
            }, function errorCallback(response) {
                return false
            });
    }
}

})();
