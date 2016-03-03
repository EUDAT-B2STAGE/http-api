(function() {
  'use strict';

angular.module('web')
    .controller('UploadController', UploadController);


function UploadController($scope, $log, $mdDialog)
{
    var self = this;
    $log.debug("Uploader");

    self.validate = function() {
      $mdDialog.hide('OK');
    };

    self.cancel = function() {
      $mdDialog.hide('FAIL');
    };

    self.uploaded = function() {
      $log.info("File uploaded");
    };

};

})();