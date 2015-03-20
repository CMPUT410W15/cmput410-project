$(function() {

    $('#{{p.uid}}-1').on('submit', function(event) {
        event.preventDefault();
        console.log('form submitted for {{p.uid}}-1')
        create_comment();
    });

    function create_comment() {
        console.log('create comment is working')
        $.ajax({
            url:"/post/comment/{{p.uid}}/",
            type:"POST",
            data: {the_comment: $('#content{{p.uid}}').val() },

            success: function(json) {
                $('#content{{p.uid}}').val('');
                console.log(json)
                console.log(json.content)
                $('#{{p.uid}}-2').append("<li id='{{comments.uid}}'>"+json.content+"</li>");
                console.log('yay!!');
            },

            error: function(xhr, errmsg, err) {
                $('#error{{p.uid}}').html("<div> <p class='text-danger'> Can't post an empty comment. </p>" +"</div>");
                console.log(xhr.status + ": " + xhr.responseText);
                console.log(errmsg);

                setTimeout(function() {
                    $("#error{{p.uid}}").html("<div> </div>");
                }, 3000);
            }

        });
    }

     /*
    The functions below are required else there will be a 403 error on each
    attempt for a comment.
    */
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

    /*
    The functions below will create a header with csrftoken
    */

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
});
