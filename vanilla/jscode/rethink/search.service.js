(function() {
  'use strict';

angular.module('web')
    .service('search', SearchService);

function SearchService($log, api) {

    var self = this;

    self.endpoints = {
        search: 'datavalues',
        submit: 'datakeys',
        documents: 'datadocs',
        users : 'accounts',
    }

// Base API calls with Rethinkdb
    self.getData = function() {
        return api.apiCall(self.endpoints.search);
    }

    self.getSingleData = function(id) {
        return api.apiCall(self.endpoints.search, id);
    }

    self.getFromQuery = function(json) {
        return api.apiCall(
            self.endpoints.search,
            'query', 'POST', {'query':json});
    }
// Base API calls

    self.getSteps = function(id) {
        return api.apiCall(self.endpoints.submit, id)
          .then(function(out_steps) {
            console.log("STEPS!");
            // Prepare steps name
            var steps = [];
            forEach(out_steps.data, function(single, i){
              steps[single.step.num] = single.step.name;
            });
            return steps;
        });
    }

    self.getDistinctValuesFromStep = function (step) {
      return self.getFromQuery(
            {
                'limit': 0, //all
                'autocomplete': {'step': step, 'position': 1}
            }
        );
    }

    self.getDocs = function(id) {
        return api.apiCall(self.endpoints.documents, id);
    }

}

})();
