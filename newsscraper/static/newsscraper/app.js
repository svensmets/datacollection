/**
 * Created by svens on 3-3-2016.
 */
/** Functionality for newsscraper app **/
(function(){
    var app = angular.module('newsscraper',['djng.forms','ngMaterial'])
        .config(function($httpProvider){
            $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

    app.controller('ArchiveSearchCtrl',['$scope', '$http', function($scope, $http){
        // http://stackoverflow.com/questions/25000896/angularjs-checkbox-not-working (17/03/2016)
        $scope.archFormData = {
            newspapers:[
                {id:0, name:'De Standaard', enabled: false},
                {id:1, name:'De Morgen', enabled: false},
                {id:2, name:'HLN', enabled: false}
            ]
        };
        $scope.submitArchiveForm = function(){
            $http({
                method: 'POST',
                url: '/newsscraper/start_archive_search',
                data: JSON.stringify($scope.archFormData),
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            })
                .success(function(data){
                    if(!data.success){
                        //TODO: errorcode
                    }else{
                        $scope.message = data.message;
                    }
                });
        }
    }]);

    app.controller('TaskController', ['$scope', '$http', function($scope, $http){
        $http.get('/newsscraper/tasks').success(function(data){
            $scope.tasks = data;
        });
    }]);

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
