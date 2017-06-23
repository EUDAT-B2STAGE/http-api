(function() {
  'use strict';

angular.module('web').service('DataService', DataService);
function DataService($log, api, jsonapi_parser) {

    var self = this;

    self.searchBoundingBox = function() {
        
        var data = {}
        data['start']="13-01-2015T00:00:00Z";
        data['end']="14-01-2015T00:00:00Z";
        data['minlat']="35.3";
        data['minlon']="6.3";
        data['maxlat']="46.3";
        data['maxlon']="13.3";
        data['download']="false";

	// test me:
	// data['output']="json";

        return api.apiCall('statics/data', 'GET', data)
    }

}

})();
