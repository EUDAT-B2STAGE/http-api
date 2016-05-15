(function() {
  'use strict';

angular.module('web')
    .controller('ToastController', ToastController);

function ToastController($scope, $log, $mdToast, $document)
{
    $log.debug("Toast is ready");
    //https://material.angularjs.org/latest/demo/toast

    var last = {
        bottom: false,
        top: true,
        left: false,
        right: true
    };
    $scope.toastPosition = angular.extend({},last);
    $scope.getToastPosition = function() {
        sanitizePosition();
        return Object.keys($scope.toastPosition)
            .filter(function(pos) { return $scope.toastPosition[pos]; })
            .join(' ');
    };
    function sanitizePosition() {
        var current = $scope.toastPosition;
        if ( current.bottom && last.top ) current.top = false;
        if ( current.top && last.bottom ) current.bottom = false;
        if ( current.right && last.left ) current.left = false;
        if ( current.left && last.right ) current.right = false;
        last = angular.extend({},current);
    }
    $scope.showSimpleToast = function(messages, delay) {

        var message = "";
// CHECK IF IT'S JUST A STRING INSTEAD OF ARRAY

        if (messages) {
            forEach(messages, function (value, key) {
                //console.log("MESSAGE", key, value);
                var line = '[' + key+ ']';
                if (value) {
                    line += ' ' + value;
                }
                message += line + '\r\n';
            })
        }
        // Skip empty message
        if (message == "") {
            return false;
        }
        // Choose the delay
        if (typeof(delay) === 'undefined') {
            delay = 3000;
        }
        // Show the dialog
        $mdToast.show(
            $mdToast.simple()
                .textContent(message)
                .position($scope.getToastPosition())
                .hideDelay(delay)
        );

        return true;
    };
}

})();
