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

  self.images = [
    "image1",
    "image2",
    "image3",
    "image4",
  ];
  $scope.selectedStep = 'fixed';
  self.steps = {
    "fixed" : {
        "some": "text",
        "other": 1,
        "images": [],
    }
  };

  self.imageCard = false;

  self.addImage = function (index) {
    self.imageCard = true;
  }

  self.selectImage = function (image) {
    self.imageCard = false;
    self.steps[$scope.selectedStep].images.push(image);
  }

}

})();