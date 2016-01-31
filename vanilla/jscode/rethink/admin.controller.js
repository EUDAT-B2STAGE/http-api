(function() {
  'use strict';

angular.module('web')
    .controller('DialogController', DialogController)
    .controller('AdminController', AdminController)
    .controller('AdminWelcomeController', AdminWelcomeController);



function AdminController($scope, $rootScope, $log, admin, $stateParams, $mdMedia, $mdDialog)
{
  // Init controller
  $log.debug("ADMIN page controller", $stateParams);
  var self = this;
  admin.getData().then(function (out)
  {
       console.log("Admin api:", out);
  });

  //TABS
  self.selectedTab = 0;
  self.onTabSelected = function () {
      $log.debug("Selected", self.selectedTab);
  }
  if ($stateParams.tab && $stateParams.tab != self.selectedTab) {
    console.log("URL TAB is ",$stateParams);
    self.selectedTab = $stateParams.tab;

  }

  // Template Directories
  self.blueprintTemplateDir = blueprintTemplateDir;
}

function AdminWelcomeController($scope, $rootScope, $log, admin, $stateParams, $mdMedia, $mdDialog)
{
  $log.debug("Welcome admin controller", $stateParams);
  var self = this;

  self.sectionModels = [
    {
        name: 'Section',
        value: 'New section!',
        description: 'The name for your new welcome section',
        chars: 50,
    },
    {
        name: 'Description',
        value: 'We will talk about a lot of things',
        description: 'Short description of your section. It will appear in the home page.',
        chars: 500,
    },
    {
        name: 'Content',
        value: 'This explanation is very long',
        description: 'Explanation of the section. It will appear in a separate page.',
        chars: 99999,
    },
  ];

  self.models = [
      {
        'Section': 'First',
        'Description': 'This is editable!',
        'Content': 'This is long editable!!<br>Test',
      },
      {
        'Section': 'Second',
        'Description': 'Try',
        'Content': 'Ehm ... <b>Uhm</b>.',
      },
  ];
/*
  self.options = {};
  self.fields = [
    {
      key: 'text',
      type: 'editableInput',
      templateOptions: {
        label: 'Text'
      }
    }
  ];
  self.originalFields = angular.copy(self.fields);
*/

  // function definition
  self.saveForm = function () {
    console.log("MODEL", self.model);
  }

  $scope.status = 'Dialog to open';
  self.customFullscreen = $mdMedia('xs') || $mdMedia('sm');

  self.showAdvanced = function(ev) {
    var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && self.customFullscreen;
    $mdDialog.show({
      controller: DialogController,
      templateUrl: blueprintTemplateDir + 'add_section.html',
      parent: angular.element(document.body),
      locals: {
        sectionModels: self.sectionModels,
      },
      targetEvent: ev,
      clickOutsideToClose:true,
      fullscreen: useFullScreen
    })
    .then(function(answer) {
      $scope.status = 'You said the information was "' + answer + '".';

// DO SOMETHING WITH THIS VALUES
      console.log(self.sectionModels);
// DO SOMETHING WITH THIS VALUES

    }, function() {
      $scope.status = 'You cancelled the dialog.';
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

function DialogController($scope, $mdDialog, sectionModels)
{

  $scope.sectionModels = sectionModels;
  $scope.title = "Add a new element";

  $scope.hide = function() {
    $mdDialog.hide();
  };
  $scope.cancel = function() {
    $mdDialog.cancel();
  };
  $scope.answer = function(answer) {
    $mdDialog.hide(answer);
  };
}

})();