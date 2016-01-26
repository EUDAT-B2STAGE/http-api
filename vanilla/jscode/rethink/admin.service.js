(function() {
  'use strict';

angular.module('web')
    .service('admin', AdminService);

function AdminService($log, api) {

    var self = this;
    self.endpoints = {
        admin: 'datadmins',
    }

    //////////////////
    // Base API call with Rethinkdb
    self.getData = function() {
        return api.apiCall(self.endpoints.admin);
    }

    self.insert = function(name, data) {
        return self.doQuery(self.endpoints.admin,
            {
                type: {name: name},
                data: data,
            }
        );

    }

}

})();
