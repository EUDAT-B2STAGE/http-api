(function() {
'use strict';

angular.module('web')
// from http://stackoverflow.com/a/20024530/2114395
 .directive('script',
  function() {
    return {
      restrict: 'E',
      scope: false,
      link: function(scope, elem, attr) {
        if (attr.type === 'text/javascript-lazy') {
          var code = elem.text() || elem.attr.src;
          var f = new Function(code);
          f();
        }
      }
    };
});

})();
