(function() {
  'use strict';

angular.module('web')
    .service('search', SearchService);

function SearchService($log, api) {

    var self = this;

    // All possible calls
    self.getData = function() {
        return api.apiCall(api.endpoints.search);
    }

    self.getSingleData = function(id) {
        return api.apiCall(api.endpoints.search, id);
    }

    self.getSteps = function(id) {
        return api.apiCall(api.endpoints.submit, id);
    }

    self.getDocs = function(id) {
        return api.apiCall(api.endpoints.documents, id);
    }

}

})();
