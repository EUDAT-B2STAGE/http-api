(function() {
  'use strict';

angular.module('web').service('DataService', DataService);
function DataService($log, api, jsonapi_parser) {

    var self = this;

    self.searchBoundingBox = function(min_date, max_date) {

        var format = 'DD-MM-YYYY';
        var suffix = "T00:00:00Z"
        min_date = moment(min_date).format(format);
        max_date = moment(max_date).format(format);

        var data = {}
        // data['start']="13-01-2015T00:00:00Z";
        // data['end']="14-01-2015T00:00:00Z";
        data['start'] = min_date+suffix;
        data['end'] = max_date+suffix;
        data['minlat']="35.3";
        data['minlon']="6.3";
        data['maxlat']="46.3";
        data['maxlon']="13.3";
        data['download']="false";

        return api.apiCall('statics/data', 'GET', data)
    }

}

})();
