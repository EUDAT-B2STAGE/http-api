(function() {
  'use strict';

angular.module('web')
    .controller('AdminController', AdminController)
    .controller('WelcomeController', WelcomeController)
    .controller('DialogController', DialogController)
    ;

function AdminController($scope, $log, admin, $stateParams)
{
  // Init controller
  $log.debug("ADMIN page controller", $stateParams);
  var self = this;

  // Init data for each tab
  $scope.sections = {};

  //TABS
  self.selectedTab = 0;

  $scope.sectionReload = function () {
    admin.getData().then(function (out)
    {
      if (out !== null && out.hasOwnProperty('elements')) {
        $scope.sections = out.data;
      } else {
        $log.warn("No data?", out);
      }
    });
  }

  self.onTabSelected = function (key) {
      $log.debug("Selected", self.selectedTab, key);

      // INIT TAB FOR MANAGING SECTIONS
      if (key == 'sections') {
        $scope.sections = {};
        $scope.sectionReload();
      }
  }

  if ($stateParams.tab && $stateParams.tab != self.selectedTab) {
    $log.debug("URL tab is ",$stateParams);
    self.selectedTab = $stateParams.tab;
  }

  // Template Directories
  self.templateDir = templateDir;
  self.blueprintTemplateDir = blueprintTemplateDir;
}

function WelcomeController($scope, $rootScope, $timeout, $log, admin, $stateParams, $mdMedia, $mdDialog)
{
  $rootScope.loaders['admin_sections'] = false;
  $log.debug("Welcome admin controller", $stateParams);
  var self = this;
  self.init = 'rdb';

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
  self.customFullscreen = $mdMedia('xs') || $mdMedia('sm');

  self.showAdvanced = function(ev, model) {
    var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && self.customFullscreen;
    var id = null;
    if (model) {
        id = model.id;
    }

// Clear or insert data in the model
    for (var j = 0; j < self.sectionModels.length; j++) {
        var value = "";
        if (model) {
            value = model.data[self.sectionModels[j].name];
        }
        self.sectionModels[j].text = value;
    };
// Options
    var dialogOptions =
    {
      controller: DialogController,
      templateUrl: blueprintTemplateDir + 'add_section.html',
      parent: angular.element(document.body),
      locals: {
        sectionModels: self.sectionModels,
        modelId: id,
      },
      targetEvent: ev,
      //clickOutsideToClose:true,
      onComplete: function(){
        // Focus on first textarea
        $timeout(function(){ angular.element("textarea")[0].focus(); });
      },
      fullscreen: useFullScreen
    }

// WHEN COMPLETED
    var afterDialog = function(response) {

      var update_id = response[0], remove = response[1];
      $log.debug("After dialog", update_id, remove);
      // Check if id
      var element = {};
      forEach(self.sectionModels, function(x, i) {
        element[x.name] = x.text;
      });

      var apicall = null;
      var data_type = 'welcome_section';
      if (update_id) {
        if (remove) {
            apicall = admin.delete(data_type, update_id);
        } else {
            apicall = admin.update(data_type, update_id, element);
        }
      } else {
        apicall = admin.insert(data_type, element);
      }

// MAKE LOADER APPEAR

      apicall.then(function (out) {
        console.log("Admin api call", out);
        if (out.elements >= 0) {
          $scope.sectionReload();
        }
        // Activate the view
        $timeout(function() {
           $rootScope.loaders['admin_sections'] = false;
        }, timeToWait);
      });
    }

// Open
    $mdDialog.show(dialogOptions)
        .then(afterDialog);

// WATCH FOR FULL SCREEN
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

function DialogController($scope, $rootScope, $mdDialog, sectionModels, modelId)
{

  $scope.sectionModels = sectionModels;
  $scope.id = modelId;
  $scope.title = "Add a new element";
  if (modelId) {
      $scope.title = "Edit/Update element";
  }

  $scope.hide = function() {
    $mdDialog.hide();
  };
  $scope.cancel = function() {
    $mdDialog.cancel();
  };
  $scope.validate = function(model) {
    var valid = true;
    forEach(model, function(x, i) {
      if (x.required && !x.text) {
        valid = false;
      }
    });
    if (valid) {
      $rootScope.loaders['admin_sections'] = true;
      $mdDialog.hide([modelId, null]);
    }
  };
  $scope.remove = function() {
    $rootScope.loaders['admin_sections'] = true;
    $mdDialog.hide([modelId, true]);
  };
}

})();