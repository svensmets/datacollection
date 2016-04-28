/**
 * Created by svens on 3-3-2016.
 */
/** Functionality for newsscraper app **/
(function(){
    var app = angular.module('newsscraper',['djng.forms','ngMaterial', 'ngMessages', 'material.svgAssetsCache'])
        .config(function($httpProvider){
            $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

    app.controller('ArchiveSearchCtrl',['$scope', '$http', 'sendToast', function($scope, $http, sendToast){
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
                .then(function succesCallback(data){
                    sendToast.showSuccess();
                    // reset form
                    $scope.archFormData = {
                        newspapers:[
                            {id:0, name:'De Standaard', enabled: false},
                            {id:1, name:'De Morgen', enabled: false},
                            {id:2, name:'HLN', enabled: false}
                        ]
                    };
                }), function errorCallback(data){
                    sendToast.showError();
            };
        };
    }]);

    app.controller('TaskController', ['$scope', '$http', 'taskService', function($scope, $http, taskService){
        taskService.async().then(function(d){
            $scope.tasks = d;
        });
        $scope.getTaskData = function(taskId){
                $http({
                    url: "/newsscraper/get_task_data/",
                    method: 'POST',
                    responseType: 'arraybuffer',
                    cache: false,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                    data: $.param({id:taskId})
                }).success(function(data){
                    // solution to save file: http://stackoverflow.com/questions/30158115/how-to-download-a-zip-file-using-angular
                    var file = new Blob([data], {type:'application/octet-stream'});
                    saveAs(file, "data.zip");
                });
            };
    }]);

    app.directive('jqdatepicker', function () {
        // http://stackoverflow.com/questions/18144142/jquery-ui-datepicker-with-angularjs (28/04/2016)
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

    app.service('sendToast', function($mdToast){
        //https://material.angularjs.org/latest/demo/toast
        this.showSuccess = function(){
            $mdToast.show(
                $mdToast.simple()
                    .textContent('Search started')
                    .hideDelay(3000)
            );
        };
        this.showError = function(){
            $mdToast.show(
                $mdToast.simple()
                    .textContent('Problem with search')
                    .hideDelay(3000)
            );
        };
    });

    app.factory('taskService', function($http){
        // http://stackoverflow.com/questions/12505760/processing-http-response-in-service (28/04/22016)
        var taskService = {
            async: function(){
                var promise = $http.get('/newsscraper/tasks').then(function(data){
                    return data.data;
                });
                return promise
            }
        };
        return taskService;
    });

})();
