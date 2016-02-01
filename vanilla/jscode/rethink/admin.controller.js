(function() {
  'use strict';

angular.module('web')
    .controller('DialogController', DialogController)
    .controller('AdminController', AdminController)
    .controller('AdminWelcomeController', AdminWelcomeController);



function AdminController($scope, $log, admin, $stateParams)
{
  // Init controller
  $log.debug("ADMIN page controller", $stateParams);
  var self = this;

  // Init data for each tab
  $scope.sections = {};

  //TABS
  self.selectedTab = 0;
  self.onTabSelected = function (key) {
      $log.debug("Selected", self.selectedTab, key);

      // INIT TAB FOR MANAGING SECTIONS
      if (key == 'sections') {
        $scope.sections = {};
        admin.getData().then(function (out)
        {
            if (out !== null && out.hasOwnProperty('elements')) {
              $scope.sections = out.data;
            } else {
              $log.warn("No data?", out);
            }
        });
      }
  }

  if ($stateParams.tab && $stateParams.tab != self.selectedTab) {
    $log.debug("URL tab is ",$stateParams);
    self.selectedTab = $stateParams.tab;
  }

  // Template Directories
  self.blueprintTemplateDir = blueprintTemplateDir;
}

function AdminWelcomeController($scope, $rootScope, $timeout, $log, admin, $stateParams, $mdMedia, $mdDialog)
{
  $log.debug("Welcome admin controller", $stateParams);
  var self = this;

  self.sectionModels = [
    {
        name: 'Section',
        value: 'New section!',
        description: 'The name for your new welcome section',
        required: true,
        focus: true,
        chars: 50,
    },
    {
        name: 'Description',
        value: 'We will talk about a lot of things',
        description: 'Short description of your section. It will appear in the home page.',
        required: true,
        chars: 500,
    },
    {
        name: 'Content',
        value: 'This explanation is very long',
        description: 'Explanation of the section. It will appear in a separate page.',
    },
  ];

//////////////////////////////////////
// HANDLING THE CREATION OF A DIALOG
  $scope.status = 'Dialog to open';
  self.customFullscreen = $mdMedia('xs') || $mdMedia('sm');

  self.showAdvanced = function(ev, data) {
    var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && self.customFullscreen;

// Clear or insert data in the model
    for (var j = 0; j < self.sectionModels.length; j++) {
        self.sectionModels[j].text = ""
    };

// Open
    $mdDialog.show({
      controller: DialogController,
      templateUrl: blueprintTemplateDir + 'add_section.html',
      parent: angular.element(document.body),
      locals: {
        sectionModels: self.sectionModels,
      },
      targetEvent: ev,
      //clickOutsideToClose:true,
      onComplete: function(){
        // Focus on first textarea
        $timeout(function(){
          angular.element("textarea")[0].focus();
        });
      },
      fullscreen: useFullScreen
    })
// WHEN COMPLETED
    .then(function(answer) {
      $scope.status = "Creating the new element";
      var element = {};
      forEach(self.sectionModels, function(x, i) {
        element[x.name] = x.text;
      });
      //console.log("To save", element);
      admin.insert('welcome_section', element).then(function (out) {
        console.log("INSERT", out);
        if (out.elements >= 0) {
          $scope.status = 'Created';
        } else {
          $scope.status = 'Failed to insert';
      }
      });

    }, function() {
      $scope.status = 'New element creation aborted...';
    });
    $scope.$watch(function() {
      return $mdMedia('xs') || $mdMedia('sm');
    }, function(wantsFullScreen) {
      self.customFullscreen = (wantsFullScreen === true);
    });
  };

  // Activate dialog to insert new element if requested by url
  if ($stateParams.new) {
    self.showAdvanced();
  }

}

function DialogController($scope, $rootScope, $mdDialog, sectionModels)
{

  $scope.sectionModels = sectionModels;
  $scope.title = "Add a new element";

  $scope.hide = function() {
    $mdDialog.hide();
  };
  $scope.cancel = function() {
    $mdDialog.cancel();
  };
  $scope.answer = function(model) {
    var valid = true;
    forEach(model, function(x, i) {
      if (x.required && !x.text) {
        valid = false;
      }
    });
    if (valid) {
      $mdDialog.hide("Funziona");
    }
  };
}

})();