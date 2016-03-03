(function() {
  'use strict';

angular.module('web')
    .controller('ExploreController', ExploreController)
    .controller('FixImagesController', FixImagesController)
    .controller('StepsController', StepsController)
    ;

////////////////////////////////
// controller
////////////////////////////////

function ExploreController($scope, $rootScope, $log, $state, search, admin)
{

  // INIT controller
  var self = this;
  $log.debug("Explore data: controller");

  // INIT scope variables
  $scope.data = {};
  $scope.results = false;

  //TABS
  self.selectedTab = null;
  self.onTabSelected = function (key)
  {
      $log.debug("Selected", key, self.selectedTab);

// THIS IS WHERE YOU ADD THE DATA LOAD LOGIC FOR TABS
      if (key == 'imagefix') {
        getMissingImagesData(admin, $scope);
      }
  }

}

////////////////////////////////
// Fix images
////////////////////////////////

function getMissingImagesData(admin, $scope) {
    return admin.getDocumentsWithNoImages()
      .then(function (out)
      {
        console.log("DATA", out);
        $scope.parties = out.data;
    });

};

function FixImagesController($scope, $log, $mdDialog)
{
    $log.debug("Fix Controller");
    var self = this;
    self.noImageList = function (name, data) {
      self.elements = data;
      self.currentParty = name;
    }


/////////////////////////////////////
    self.uploaderDialog = function()
    {
      var dialogOptions = {
        templateUrl: blueprintTemplateDir + 'uploader.html',
        //controller: UploadController,
        parent: angular.element(document.body),
        //locals: { id: null, },
        //targetEvent: ev,
        //clickOutsideToClose:true,
        //onComplete: function() { $log.debug("complete"); },
        }

      var afterDialog = function(response) {
        $log.info("Dialog response", response);
      }

      // Open
      $mdDialog.show(dialogOptions).then(afterDialog);
    }
/////////////////////////////////////

};

////////////////////////////////
// controller
////////////////////////////////

function StepsController($scope, $log, $state, search)
{
  // INIT controller
  $log.debug("Stepping in pieces");
  var self = this;
  self.step = 2;

  search.getDistinctValuesFromStep(self.step).then(function (out)
  {
        self.data = [];
        self.dataCount = self.data.length;
       if (out) {
           self.dataCount = out.elements;
           self.data = out.data;
       }
  })
}


})();