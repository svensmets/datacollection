/**
 * Created by svens on 3-3-2016.
 */
/** Functionality for newsscraper app*/
(function(){
    var app = angular.module('newsscraper',[

    ]).config(function($httpProvider){
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    });
    /*
    app.controller('', function(){

    });
    */
})();
