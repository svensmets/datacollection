/**
 * Created by svens on 30-10-2015.
 */
$(document).ready(function () {
    $("#profile-information-row").css('display', 'none');
    $("#tweets-by-name-row").css('display', 'none');
    $("#tweets-by-searchterm-row").css('display', 'none');

    $("#btn-search-profile-information").click(function () {
        $("#profile-information-row").fadeIn();
        $("#tweets-by-name-row").fadeOut();
        $("#tweets-by-searchterm-row").fadeOut();
    });
    $("#btn-search-tweets-names").click(function () {
        $("#profile-information-row").fadeOut();
        $("#tweets-by-name-row").fadeIn();
        $("#tweets-by-searchterm-row").fadeOut();
    });
    $("#btn-search-tweets-searchterms").click(function () {
        $("#profile-information-row").fadeOut();
        $("#tweets-by-name-row").fadeOut();
        $("#tweets-by-searchterm-row").fadeIn();
    });

    //if streaming options are checked, number of days must be set to required
    $("#streaming-searchterms-checkbox").change(function () {
        if ($("#streaming-searchterms-checkbox").is(":checked")) {
            $("#nr-days-searchterms-streaming").prop("required", true);
        } else {
            $("#nr-days-searchterms-streaming").prop("required", false);
        }
    });
    $("#streaming-tweetsbyname-checkbox").change(function () {
        if ($("#streaming-tweetsbyname-checkbox").is(":checked")) {
            $("#nr-days-names-streaming").prop("required", true);
        } else {
            $("#nr-days-names-streaming").prop("required", false);
        }
    });
    //hide alerts on startup
    $("#alert-search-started").hide();
    $("#alert-name-not-valid").hide();
    $("#alert-search-problem").hide();
    /*
     * REFRESH TASKS
     * !! not longer used 01/02/2016
     * */
    // refresh tasks: necessary because task does not yet exist when user performs a search and the screen returns
    $("#refresh-tasks-button").click(function () {
        $.post("/get_tasks/", function (data) {
            //clear tasks shown
            $("#tasks-row").empty();
            //gather data from response
            var user = data['user'];
            var tasks = data['tasks'];
            //tasks are in string delimited wit ';'
            var allTasks = String(tasks).split(";");
            //show tasks to user
            $("#tasks-row").append("<h2>Tasks of " + user + "</h2>");
            for (var i = 0; i < allTasks.length; i++) {
                var task = allTasks[i];
                //remove comma's at the beginning of tasks
                if (task.charAt(0) === ',') {
                    task = task.substr(1)
                }
                //add only if task is not empty
                if (task.length > 0) {
                    $("#tasks-row").append('<div class="well">' + task + '<a class="btn btn-info pull-right" href="#" role="button" id="btn-download-data">Download data</a></div>');
                }
            }
        });
    });
    /*
     * SEARCH PROFILE INFORMATION
     * */
    //add names
    //Check whether the name the user entered is a valid screenname
    //Adds name to textarea if valid
    $("#add-name-button").click(function () {
        if ($("#add-name-input").val()) {
            var name = $("#add-name-input").val();
            /* check name, if exists as a twittername add it to the textarea*/
            $.get("/lookupname/", {name: name}, function (data) {
                var response = data['exists'];
                if (response === 'true') {
                    /*add name to textarea*/
                    var allnames = $("#all-names-textarea").val();
                    $("#all-names-textarea").val(allnames + name + ",");
                    /*clear textfield*/
                    $("#add-name-input").val("");
                } else {
                    $("#alert-name-not-valid").show().delay(3000).fadeOut();
                    /*clear textfield*/
                    $("#add-name-input").val("");
                }
            })
        }
    });
    //submit profile information search task
    $("#form-search-options").submit(function (event) {
        //stop form from submitting normally
        event.preventDefault();
        //gather all information
        var names = $("#all-names-textarea").val();
        if (names === "") {
            //if textarea is empty, error message is shown for 2 seconds
            $("#all-names-textarea").before('<p class="names-error-message" style="color:red;"><red>Name is required</p>');
            setTimeout(function () {
                $(".names-error-message").hide();
            }, 2000);
        } else {
            //textarea has names, gather values of search options
            var followersChecked = false;
            var friendChecked = false;
            var listMembershipsChecked = false;
            var listSubscriptionsChecked = false;
            var relationshipsChecked = false;
            var maxFollowers = $("#max-followers-input").val();
            if (!maxFollowers) {
                maxFollowers = 110000;
            }
            if ($("#followers-checkbox").is(":checked")) {
                followersChecked = true;
            }
            if ($("#friends-checkbox").is(":checked")) {
                friendChecked = true;
            }
            if ($("#list-memberships-checkbox").is(":checked")) {
                listMembershipsChecked = true;
            }
            if ($("#list-subscriptions-checkbox").is(":checked")) {
                listSubscriptionsChecked = true;
            }
            if ($("#relationships-checkbox").is(":checked")) {
                relationshipsChecked = true;
            }
            //data must be put in array and then stringified => otherwise error on post
            var data = {
                names: names, followers: followersChecked, friends: friendChecked,
                listmemberships: listMembershipsChecked, listsubscriptions: listSubscriptionsChecked,
                maxfollowers: maxFollowers, relationshipschecked: relationshipsChecked
            }
            //http://api.jquery.com/jquery.post/
            //post the from with ajax
            $.post("/profile-information-search/", JSON.stringify(data), function(){
                $("#alert-search-started").show().delay(3000).fadeOut();
            }).fail(function () {
                $("#alert-search-problem").show().delay(3000).fadeOut();
            });
        }
    });
    //clear names of textarea search profile information
    $("#btn-clear-profile-information-textarea").click(function () {
        $("#all-names-textarea").val("");
    });
    /*
     * SEARCH TWEETS BY NAME
     * */
    //Check whether the name the user entered is a valid screenname
    //Adds name to textarea if valid
    $("#add-tweetname-button").click(function () {
        if ($("#add-tweetname-input").val()) {
            var name = $("#add-tweetname-input").val();
            $.get("/lookupname/", {name: name}, function (data) {
                var response = data['exists'];
                if (response === 'true') {
                    /*add name to textarea*/
                    var allnames = $("#all-names-textarea-tweetsbyname").val();
                    $("#all-names-textarea-tweetsbyname").val(allnames + name + ",");
                    /*clear textfield*/
                    $("#add-tweetname-input").val("");
                } else {
                    $("#alert-name-not-valid").show().delay(3000).fadeOut();
                    /*clear textfield*/
                    $("#add-tweetname-input").val("");
                }
            })
        }
    });
    //clear names of textarea tweets by name
    $("#btn-clear-tweetsbyname-textarea").click(function () {
        $("#all-names-textarea-tweetsbyname").val("");
    });
    //start streaming search by name
    $("#form-tweets-by-name-search-options").submit(function (event) {
        //stop form from submitting normally
        event.preventDefault();
        //gather all information
        var names = $("#all-names-textarea-tweetsbyname").val();
        if (names === "") {
            //if textarea is empty, error message is shown for 2 seconds
            $("#all-names-textarea-tweetsbyname").before('<p class="names-error-message" style="color:red;"><red>Must not be empty</p>');
            setTimeout(function () {
                $(".names-error-message").hide();
            }, 2000);
        } else {
            //textarea has names, gather values of search options
            var getSearchAPITweets = false;
            var getStreamingTweets = false;
            var nrOfDays = 0;
            if ($("#searchapi-tweetsbyname-checkbox").is(":checked")) {
                getSearchAPITweets = true;
            }
            if ($("#streaming-tweetsbyname-checkbox").is(":checked")) {
                getStreamingTweets = true;
                nrOfDays = $("#nr-days-searchterms-streaming").val();
            }
            //data must be put in array and then stringified => otherwise error on post
            var data = {
                names: names,
                getSearchApiTweets: getSearchAPITweets,
                getStreamingTweets: getStreamingTweets,
                nrOfDays: nrOfDays
            }
            //http://api.jquery.com/jquery.post/
            //post the from with ajax
            $.post("/tweets_by_name_search/", JSON.stringify(data), function(){
                $("#alert-search-started").show().delay(3000).fadeOut();
            }).fail(function () {
                $("#alert-search-problem").show().delay(3000).fadeOut();
            });
        }
    });
    /*
     * SEARCH TWEETS BY SEARCHTERM
     * */
    $("#add-searchterm-button").click(function () {
        if ($("#add-searchterm-input").val()) {
            var searchTerm = $("#add-searchterm-input").val();
            var allSearchTerms = $("#all-names-textarea-searchterms").val();
            $("#all-names-textarea-searchterms").val(allSearchTerms + searchTerm + ",");
            $("#add-searchterm-input").val("");
        }
    });
    //clear names of textarea tweets by name
    $("#btn-clear-searchterms-textarea").click(function () {
        $("#all-names-textarea-searchterms").val("");
    });
    //start search
    $("#form-tweets-by-searchterm-options").submit(function (event) {
        //stop form from submitting normally
        event.preventDefault();
        //gather all information from the input fields
        var searchTerms = $("#all-names-textarea-searchterms").val();
        if (searchTerms === "") {
            //if textarea is empty, error message is shown for 2 seconds
            $("#all-names-textarea-searchterms").before('<p class="names-error-message" style="color:red;"><red>Must not be empty</p>');
            setTimeout(function () {
                $(".names-error-message").hide();
            }, 2000);
        } else {
            //textarea has names, gather values of search options
            var getSearchAPITweets = false;
            var getStreamingTweets = false;
            var nrOfDays = 0;
            if ($("#searchapi-searchterms-checkbox").is(":checked")) {
                getSearchAPITweets = true;
            }
            if ($("#streaming-searchterms-checkbox").is(":checked")) {
                getStreamingTweets = true;
                nrOfDays = $("#nr-days-searchterms-streaming").val();
            }
            //data must be put in array and then stringified => otherwise error on post
            var data = {
                searchTerms: searchTerms,
                getSearchApiTweets: getSearchAPITweets,
                getStreamingTweets: getStreamingTweets,
                nrOfDays: nrOfDays
            };
            //post the from with ajax
            $.post("/tweets_by_searchterm_search/", JSON.stringify(data), function(){
                $("#alert-search-started").show().delay(3000).fadeOut();
            }).fail(function () {
                $("#alert-search-problem").show().delay(3000).fadeOut();
            });
        }
    });

    /**
     * When a user clicks on the button "download data" in the task section => download the data associated
     * with the taks
     */
    $("#btn-download-data").click(function(){
        //the id of the surrounding task is the id of the task
        var taskId = $("#btn-download-data").parent().id;
        //start the query and return the data, with compression
        var data = {
            id: taskId
        }
        //http://api.jquery.com/jquery.post/
        //post the from with ajax
        $.post("/get_task_data/", JSON.stringify(data)).fail(function () {
            alert("error");
        });
    });

    /*
     * Functions for security token
     * */
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

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

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