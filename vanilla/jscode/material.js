
var app = angular.module('materializeApp', ['ui.materialize'])
    .controller('BodyController', ["$scope", function ($scope) {

        $scope.test = "Hello Worlds";
        console.log("It works")

    }]);