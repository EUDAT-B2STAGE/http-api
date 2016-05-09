(function() {
  'use strict';

angular.module('web')
    .controller('TestController', TestController)
    .controller('SubController', SubController);

function TestController($scope, $log)
{
  $log.info("Ready to search");
  var self = this;
  self.hello = 'Hello World!';
}

function SubController($scope, $log)
{
  $log.info("Ready to search");
  var self = this;
  self.sub = 'sub!';
}

})()