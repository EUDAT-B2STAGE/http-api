(function() {
  'use strict';

angular.module('web')
    .service('search', SearchService);

// CHANGE POST TO GET

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
        return api.apiCall(self.endpoints.search, 'GET', undefined, id)
          .then(function(out)
          {
            if (!out || out.count < 1) {
                return false;
            }
            var element = {'image': null};
            forEach(out.data, function(value, key){
                var stepName = self.latestSteps[key+1];
                element[stepName] = value;
            });
            self.getDocs(id).then(function(out_docs)
            {
              if (out_docs.count > 0) {
                element.image =
                  out_docs.data[0].images[0].filename.replace(/\.[^/.]+$/, "")
                    + '/TileGroup0/0-0-0.jpg';
              }
            }); // GET DOCUMENTS
            console.log("ELEMENT", element);
            return element;

          });
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

// TO FIX
    self.getDocs = function(id) {
        return api.apiCall(
            self.endpoints.documents,
            undefined, undefined, id);
    }

}

})();
