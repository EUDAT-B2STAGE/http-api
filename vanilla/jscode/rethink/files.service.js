(function() {
  'use strict';

angular.module('web')
    .service('search', SearchService);

function SearchService($log, api)
{

    var self = this;

    self.endpoints = {
        files: 'upload',
        docs: 'datadocs',
        users : 'accounts',
    }

// USE THIS SERVICE FOR TRANSCRIPTIONS AND IMAGES LOADING?

/*
    // A new file is uploaded
    self.sendFile = function(id, file, type, user) {

        // Since python 'join path' uses underscore for spaces
        var myfile = file.replace(/[\s]/g, '_');

        var params = {
            code: myfile.replace(/\.[^\.]+$/, ''), // Remove extension
            filename: myfile,
            filetype: type,
            recordid: id,
            upload_user: user,
            upload_time: Date.now(), //timestamp
            // no transcriptions in the beginning
        };

        // Save a new document and get the id
        return API.set(resource, params).then(function(id) {
            logger.info("Uploaded new file inside db: " + id);
            return factory.get();
        });
    }

*/

};

})();