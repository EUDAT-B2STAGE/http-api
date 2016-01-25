(function() {
'use strict';

angular.module('web').config(hotkeysConfig);
//angular.module('web').run(formlyConfig);

function hotkeysConfig(hotkeysProvider) {
  //Disable ngRoute integration to prevent listening for $routeChangeSuccess events
  hotkeysProvider.useNgRoute = false;
}

});