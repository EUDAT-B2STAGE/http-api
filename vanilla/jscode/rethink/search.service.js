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

    self.getSingleData = function(id, details) {

      var detailed = 'short';
      if (details) {
        detailed = 'full';
      }

      //$log.debug("Single data", id);
      return api.apiCall(
        self.endpoints.search,
        'GET', {details: detailed}, id)
       .then(function(out)
       {
          if (!out || out.elements < 1) {
              return false;
          }
          var element = {id: id, thumb: null, images: {},};
          forEach(out.data, function(value, key){
              var stepName = self.latestSteps[key+1];
              element[stepName] = value;
          });
          return self.getDocs(id).then(function(out_docs)
          {
            //console.log("DOCS", out_docs);
            if (out_docs.elements > 0) {
              // RECOVER ALL IMAGES
              var images = out_docs.data[0].images;
              element.images = images;
              // HANDLE ONLY FIRST ONE AS THUMBNAIL IN MAIN SEARCH
              element.thumb = images[0].filename
                .replace(/\.[^/.]+$/, "")+'/TileGroup0/0-0-0.jpg';
            }
            $log.debug("Single element", element);
            return element;
          }); // GET DOCUMENTS

          });
    }

    self.doQuery = function(endpoint, filters) {
        return api.apiCall(endpoint, 'GET', filters);
    }
// Base API calls
//////////////////

// OLD
    // self.getSteps = function(id) {
    //     return api.apiCall(self.endpoints.submit, 'GET', undefined, id)
// NEW
    self.getSteps = function(all)
    {
        return api.apiCall(self.endpoints.submit)
          .then(function(out_steps) {
            // Prepare steps name
            var steps = [];
            if (out_steps && out_steps.hasOwnProperty('data'))
            {
                if (all) {
                    return out_steps.data;
                }
                forEach(out_steps.data, function(single, i){
                  steps[single.step.num] = single.step.name;
                });
            }
            self.latestSteps = steps;
            return steps;
        });
    }

    self.getDistinctValuesFromStep = function(step) {
      return self.doQuery(self.endpoints.search,
            {
                perpage: 0, //all
                filter: 'autocompletion',
                step: step,
                position: 1,
            }
        );
    }

    self.filterData = function(filter) {
        return self.doQuery(
            self.endpoints.search,
            {
                filter: 'nested_filter',
                position: 1,
                key: filter,
            }
        );
    }

    self.getDocs = function(id) {
        return api.apiCall(
            self.endpoints.documents,
            undefined, undefined, id);
    }
    self.getDistinctTranscripts = function() {
      return self.doQuery(self.endpoints.documents,
            {
                perpage: 0, //all
                filter: 'notes',
            }
        );
    }
    self.filterDocuments = function(filter) {
        return self.doQuery(
            self.endpoints.documents,
            {
                filter: 'notes',
                key: filter,
            }
        );

    }

}

})();
