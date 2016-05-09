
function DialogExample ()
{
  var dialogOptions = {
      template: "Hello dialog",
      //controller: DialogController,
      parent: angular.element(document.body),
      //locals: { id: null, },
      //targetEvent: ev,
      clickOutsideToClose:true,
      //onComplete: function() { $log.debug("complete"); },
    }

  var afterDialog = function(response) {
        $log.info("Dialog response", response);
  }

  // Open
  $mdDialog.show(dialogOptions).then(afterDialog);
}
