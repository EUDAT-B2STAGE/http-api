(function() {
  'use strict';

angular.module('web')
    .service('search', SearchService);

function SearchService($log, api) {

    var self = this;
    self.available = true;

    api.logged().then(function (check) {
        console.log("CHECK AUTH ON API", check);
        self.available = false;
    });

    self.endpoints = {
        search: 'datavalues',
        submit: 'datakeys',
        documents: 'datadocs',
        users : 'accounts',
    }

    // All possible calls
    self.getData = function() {
        return api.apiCall(self.endpoints.search);
    }

    self.getSingleData = function(id) {
        return api.apiCall(self.endpoints.search, id);
    }

    self.getSteps = function(id) {
        return api.apiCall(self.endpoints.submit, id);
    }

    self.getDocs = function(id) {
        return api.apiCall(self.endpoints.documents, id);
    }

    self.getFromQuery = function(json) {
        return api.apiCall(
            self.endpoints.search,
            'query', 'POST', {'query':json});
    }

}

})();
