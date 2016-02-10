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
    $scope.showSimpleToast = function(messages) {

        var message = "";
        if (messages) {
            forEach(messages, function (value, key) {
                message += key + ': ' + value;
            })
        }

        if (message == "") {
            return false;
        }

        $mdToast.show(
            $mdToast.simple()
                .textContent(message)
                .position($scope.getToastPosition())
                .hideDelay(3000)
        );
        return true;
    };
}

})();
