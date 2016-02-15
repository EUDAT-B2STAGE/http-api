(function() {
  'use strict';

angular.module('web')
    .controller('SubmissionController', SubmissionController)
    ;

function SubmissionController($scope, $log)
{

  // INIT controller
  var self = this;
  $log.debug("Submission controller");

  self.images = [];

  self.addImage = function () {
    self.images.push("new select" + self.images.length);
  }

}

})();