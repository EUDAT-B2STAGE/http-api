(function() {
  'use strict';

angular.module('web')
    .controller('UploadController', UploadController);


function UploadController($scope, $log, $mdDialog)
{
    var self = this;
    $log.debug("Uploader");

// Buttons actions in the dialog
    self.validate = function() {
      $mdDialog.hide('OK');
    };

    self.cancel = function() {
      $mdDialog.hide('FAIL');
    };

//////////////////////////////
// IMAGES filter?
//////////////////////////////

// Functions for uploading
    self.uploaded = function(file) {
      $log.info("File uploaded", file);
// DO SOMETHING
    };

    self.adding = function(file) {
      //$log.debug("File adding", file);
      $scope.showSimpleToast( {"Uploading the file": file.name} );
    };

    self.fileError = function(file, message_json) {
      $log.warn("File error", file, message_json);
      $scope.showSimpleToast({
        "Test": 'test me',
        "Failed to upload": file.name,
        "Error message": message_json,
      }, 9000);
    };

/*
    self.otherError = function(file, message) {
      $log.warn("Upload error", file, message);
      $scope.showSimpleToast({
        "Failed to flow": file.name,
        "Error is": message,
      });
    };
*/

};

})();