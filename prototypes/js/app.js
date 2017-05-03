
angular.module('myapp', [
    // 'ngMaterial'
]).controller('MyController',
  function($scope, $http) {

    var token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZTM4NDhlODMtZmMyMi00MTA3LWI4MDctMzQwM2MyNmZhMWFiIiwiaHB3ZCI6bnVsbCwiaWF0IjoxNDkzNzg0NDE5LCJuYmYiOjE0OTM3ODQ0MTksImV4cCI6MTQ5NjM3NjQxOSwianRpIjoiMmI2MTYxMWItNmQ1Ni00Y2IzLWE4NjItZTJhOTE1N2U5ZmFkIn0.yfSnAOehr8G90qqCQNrDcLmQGZuMReD87gwCl6u60C8';
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
