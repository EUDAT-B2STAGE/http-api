(function() {
  'use strict';

angular.module('web')
    .service('search', SearchService);

function SearchService($log, api) {

    var self = this;

    self.endpoints = {
        search: 'filter',
        users : 'accounts',
    }

    self.handleResponse = function (promise) {
        return promise.then(function (response) {
            console.log("RESP", response);
            return response;
        });
    }

    // All possible calls
    self.getData = function() {
        return self.handleResponse(
            api.apiCall(api.endpoints.search)
            );
    }

    // Single call
    self.getSingleData = function(id) {
        return self.handleResponse(
            api.apiCall(api.endpoints.search, id)
            );
    }

    // Using json data in POST
    self.getFromQuery = function(json) {
        return self.handleResponse(
            api.apiCall(
                api.endpoints.search,
                'query', 'POST', {'query':json})
            );
    }

}

})();
