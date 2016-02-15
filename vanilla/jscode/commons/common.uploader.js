(function() {
  'use strict';

angular.module('web')
    .controller('UploadController', UploadController)

function UploadController($scope, $log, $mdDialog)
{
    // Init controller
    $log.debug("Uploader controller", $stateParams);
    var self = this;


    // Options
    var dialogOptions =
    {
      //controller: DialogController,
      templateUrl: blueprintTemplateDir + 'add_section.html',
      parent: angular.element(document.body),
      // How to pass data to the dialog
      locals: {
        id: null,
      },
      targetEvent: ev,
      //clickOutsideToClose:true,
      //onComplete: function(){ },
    }

    var afterDialog = function(response) {
        console.log("Dialog response", response);
    }

    // Open
    $mdDialog.show(dialogOptions)
        .then(afterDialog);
}

})();