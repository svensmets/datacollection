/**
 * Created by svens on 3-3-2016.
 */
/** Functionality for newsscraper app **/
(function(){
    var app = angular.module('newsscraper',['djng.forms','ngMaterial'])
        .config(function($httpProvider){
            $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    });

    app.controller('ArchiveSearchCtrl', function($scope, $http){
        $scope.minDate = new Date('01/01/2005');
        $scope.maxDate = new Date();
    });

    app.directive('jqdatepicker', function () {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function (scope, element, attrs, ngModelCtrl) {
                element.datepicker({
                    dateFormat: 'DD, d  MM, yy',
                    onSelect: function (date) {
                        scope.date = date;
                    }
                });
            }
        };
    });
})();
