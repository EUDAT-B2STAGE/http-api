
angular.module('myapp', [
    // 'ngMaterial'
]).controller('MyController',
  function($scope, $http) {

    var token = '';
    var request = {
        method: 'GET', url: 'http://localhost:8080/auth/profile',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
    };

    $http(request).then(
        function success(response) {
            $scope.dataset = response.data.Response.data;
        },
        function error(response) {
            $scope.messages = response.data.Response.errors;
        },
    );

    $scope.reload = function() {
        window.location.reload();
    }
  }
);
