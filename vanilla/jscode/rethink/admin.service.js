(function() {
  'use strict';

angular.module('web')
    .service('admin', AdminService);

function AdminService($log, api) {

    var self = this;
    self.endpoints = {
        admin: 'datadmins',
        imissing: 'dataimagemissing',
    }

    //////////////////
    // Admin fix on normal parts
    self.getDocumentsWithNoImages = function() {
        return api.apiCall(self.endpoints.imissing);
    }

    //////////////////
    // Base API call with Rethinkdb
    self.getData = function() {
        return api.apiCall(self.endpoints.admin);
    }

/* HOW DATA SHOULD LOOK LIKE:
    {
        "type": {
            "name": "Welcome page",
            "description": null
        },
        "data": {
            "whatever": "True"
        }
    }
*/

    self.insert = function(name, data) {
        return api.apiCall(self.endpoints.admin, 'POST',
            {
                type: {name: name},
                data: data,
            }
        );
    }

    self.update = function(name, id, data) {
        return api.apiCall(self.endpoints.admin, 'PUT',
            {
                type: {name: name},
                data: data,
            }, id);
    }

    self.delete = function(name, id) {
        return api.apiCall(self.endpoints.admin, 'DELETE', null, id);
    }

}

})();
