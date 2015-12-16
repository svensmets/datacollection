/**
 * Created by svens on 30-10-2015.
 */
$(document).ready(function(){
    //visibility of fields on form
    //default no search options visible on template
    $("#profile-information-namefield").css('visibility', 'hidden');
    $("#profile-information-options").css('visibility', 'hidden');
    //if clicked on the appropriate button, the search options become visible
    $("#btn-search-profile-information").click(function(){
        $("#profile-information-namefield").css('visibility', 'visible');
        $("#profile-information-options").css('visibility', 'visible');
    });
    $("#btn-second-search-option").click(function(){
        $("#profile-information-namefield").css('visibility', 'hidden');
        $("#profile-information-options").css('visibility', 'hidden');
    });

    // refresh tasks: necessary because task does not yet exist when user performs a search and the screen returns
    $("#refresh-tasks-button").click(function(){
        $.post("/get_tasks/", function(data){
            //clear tasks shown
            $("#tasks-row").empty();
            //gather data from response
            var user = data['user'];
            var tasks = data['tasks'];
            //tasks are in string delimited wit ';'
            var allTasks = String(tasks).split(";");
            //show tasks to user
            $("#tasks-row").append("<h2>Tasks of " + user + "</h2>");
            for(var i = 0; i < allTasks.length; i++){
                var task = allTasks[i];
                //remove comma's at the beginning of tasks
                if(task.charAt(0) === ','){
                    task = task.substr(1)
                }
                //add only if taks is not empty
                if(task.length > 0){
                    $("#tasks-row").append('<div class="well">' + task + '</div>');
                }
            }
        }).fail(function(){
            alert("error")
        });
    });

    //add names
    //Check whether the name the user entered is a valid screenname
    //Adds name to textarea if valid
    $("#add-name-button").click(function(){
        if($("#add-name-input").val()){
            var text = $("#add-name-input").val();
            $.get("/lookupname/", {name:text}, function(data){
                var response = data['exists'];
                if(response === 'true'){
                    /*add name to textarea*/
                    $("#all-names-textarea").append(text + ",");
                    /*clear textfield*/
                    $("#add-name-input").val("");
                    /*remove possible error message*/
                    $("#error_usernotvalid").text("");
                }else{
                    $("#add-name-input").after("<span id='error_usernotvalid'>user not valid</span>");
                    /*clear textfield*/
                    $("#add-name-input").val("");
                }
            })
        }
    });
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    //submit profile information search task
    $("#form-search-options").submit(function(event){
        //stop form from submitting normally
        event.preventDefault();
        //gather all information
        var names = $("#all-names-textarea").val();
        if(names === ""){
            //if textarea is empty, error message is shown for 2 seconds
            $("#all-names-textarea").before('<p class="names-error-message" style="color:red;"><red>Name is required</p>');
            setTimeout(function(){
                $(".names-error-message").hide();
            }, 2000);
        }else{
            //textarea has names, gather values of search options
            var followersChecked = false;
            var friendChecked = false;
            var listMembershipsChecked = false;
            var listSubscriptionsChecked = false;
            var maxFollowers = $("#max-followers-input").val() ;
            if(!maxFollowers){
                maxFollowers = 110000;
            }
            if($("#followers-checkbox").is(":checked")){
                followersChecked = true;
            }
            if($("#friends-checkbox").is(":checked")){
                friendChecked = true;
            }
            if($("#list-memberships-checkbox").is(":checked")){
                listMembershipsChecked = true;
            }
            if($("#list-subscriptions-checkbox").is(":checked")){
                listSubscriptionsChecked = true;
            }
            //data must be put in array and then stringified => otherwise error on post
            var data = {names: names, followers: followersChecked, friends: friendChecked,
                listmemberships: listMembershipsChecked, listsubscriptions: listSubscriptionsChecked,
                maxfollowers: maxFollowers}
            //http://api.jquery.com/jquery.post/
            //post the from with ajax
            $.post("/profile-information-search/", JSON.stringify(data)).fail(function(){
                alert("error");
            });
        }
    });
    //https://docs.djangoproject.com/en/1.6/ref/contrib/csrf/#ajax
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

});