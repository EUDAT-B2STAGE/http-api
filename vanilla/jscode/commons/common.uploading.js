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
      file.status = 'uploaded';
      $log.info("File uploaded", file);
// DO SOMETHING
    };

    self.adding = function(file, ev, flow) {
      file.status = 'progress';
      $log.debug("File adding", file, ev, flow);
      $scope.showSimpleToast( {"Uploading the file": file.name} );
    };

    self.fileError = function(file, message) {
      file.status = 'fail';
      file.errorMessage = message;
      $log.warn("File error", file, message);
      $scope.showSimpleToast({
        "Failed to upload": file.name,
        //"Error message": message,
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