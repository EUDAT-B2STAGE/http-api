(function() {
  'use strict';

angular.module('web')
    .service('search', SearchService);

function SearchService($log, api) {

    var self = this;

    self.latestSteps = [];
    self.endpoints = {
        search: 'datavalues',
        submit: 'datakeys',
        documents: 'datadocs',
        users : 'accounts',
    }

//////////////////
// Base API calls with Rethinkdb
    self.getData = function() {
        return api.apiCall(self.endpoints.search);
    }

    self.getSingleData = function(id) {
        return api.apiCall(self.endpoints.search, 'GET', undefined, id);
    }

    self.getFromQuery = function(endpoint, json) {
        return api.apiCall(endpoint, 'POST', {'query':json});
    }

    self.filterData = function(filter) {
        return self.getFromQuery(
            self.endpoints.search,
            {'nested_filter':
                {'position': 1, 'filter': filter}});
    }

    self.filterDocuments = function(filter) {
        return self.getFromQuery(
            self.endpoints.documents,
            {'notes': {'filter': filter}});

    }

// Base API calls
//////////////////

    self.getSteps = function(id) {
        return api.apiCall(self.endpoints.submit, 'GET', undefined, id)
          .then(function(out_steps) {
            // Prepare steps name
            var steps = [];
            if (out_steps && out_steps.hasOwnProperty('data'))
            {
                forEach(out_steps.data, function(single, i){
                  steps[single.step.num] = single.step.name;
                });
            }
            self.latestSteps = steps;
            return steps;
        });
    }

    self.getDistinctValuesFromStep = function(step) {
      return self.getFromQuery(self.endpoints.search,
            {
                'limit': 0, //all
                'autocomplete': {'step': step, 'position': 1}
            }
        );
    }

    self.getDistinctTranscripts = function() {
      return self.getFromQuery(self.endpoints.documents,
            {
                'limit': 0, //all
                'notes': {'nofilter': true},
            }
        );
    }

    self.getDocs = function(id) {
        return api.apiCall(
            self.endpoints.documents,
            undefined, undefined, id);
    }

}

})();
