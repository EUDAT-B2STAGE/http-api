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


    // All possible calls
    self.getData = function() {
        return api.apiCall(api.endpoints.search);
    }

    // Single call
    self.getSingleData = function(id) {
        return api.apiCall(api.endpoints.search, id);
    }

    // Using json data in POST
    self.getFromQuery = function(json) {
        return api.apiCall(api.endpoints.search, 'query', 'POST',
            {'query':json});
    }

}

})();
