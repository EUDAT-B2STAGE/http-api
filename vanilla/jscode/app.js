(function() {
  'use strict';

/* Define another module?
console.log('PRE');
angular.module('blueprint', ['ui.router']);
console.log('POST');
*/

  angular
    .module('web', [
        //'ngAnimate',
        'ngSanitize',
        'ui.router', //'ngRoute',
// BOOTSTRAP
        //'mgcrea.ngStrap',
// OFFICIAL MATERIAL
        'ngMaterial',
// MATERIAL DESIGN
        'ui.materialize',

//////////////////////////////////////
        'satellizer',
// THE LOADING BAR
        //'angular-loading-bar',
        //'cfp.loadingBar',
// IMAGES LAZ LOAD
        'angularLazyImg',
// MAKE DATA TREE explorer
        'treeControl',
// KEYBOARD SHORTCUTS        
        'cfp.hotkeys',

// OTHERS?
        //'blueprint',
    ]);

})();
