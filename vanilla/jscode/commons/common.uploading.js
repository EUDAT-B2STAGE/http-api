(function() {
  'use strict';

angular.module('web')
    .controller('UploadController', UploadController);


function UploadController($scope, $log, $mdDialog) //, record)
{
    var self = this;
    $log.debug("Uploader", $scope.currentRecord);

    //////////////////////////////
    // Flow library configuration
    //////////////////////////////
    self.config = {
        // Passing data to the flow HTTP API call
        query: function (flowFile, flowChunk) {
          return {
            record: $scope.currentRecord,
            //source: 'flow_query'
          };
        }
    }

    //////////////////////////////
    // Other functions
    //////////////////////////////

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

    self.uploaded = function(file) {
      file.status = 'uploaded';
      $log.info("File uploaded", file);

/*
// REFRESH SHOULD BE DONE AFTER DIALOG CLOSING
// (another js file)
// BUT ONLY IF SOMETHING HAS BEEN UPLOADED
*/
    };

    self.adding = function(file, ev, flow) {
      file.status = 'progress';
      file.record = $scope.currentRecord;
      $log.debug("File adding", file, ev, flow);
      $scope.showSimpleToast( {"Uploading the file": file.name} );
    };

    self.fileError = function(file, message) {
      file.status = 'fail';
      var json_message = angular.fromJson(message);
      //console.log(message, json_message);
      file.errorMessage = json_message.data['error'];
      $log.warn("File error", file, file.errorMessage);
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