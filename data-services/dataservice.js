$(function() {
    // Deck initialization
    $.deck('.slide');
    
    $('#style-themes').change(function() {
        $('#style-theme-link').attr('href', $(this).val());
    });
    
    $('#transition-themes').change(function() {
        $('#transition-theme-link').attr('href', $(this).val());
    });

    $('.theme-menu').hide();


    var server = "http://learnreg1.sri.com";
    function runQuery( url ) {

        var settings = {
            dataType: 'text',
            callback: 'callback',
            success: function (data, textStatus, jqXhr) {
                $('#extract-query-examples .loading').hide(500);
                data = JSON.parse(data);
                data = JSON.stringify(data);
                 $('#extract-query-examples .result').html("").append("<code><strong>SERVICE RESPONSE</strong><pre/></code>").find("pre").text(data, null, 2);
                 $('#extract-query-examples .result').show(500);

            },
            error: function(jqXHR, textStatus, errorThrown) {
                $('#extract-query-examples .loading').hide(500);
                $('#extract-query-examples .result').html("<h4>"+textStatus+"</h4>").show();
                $('#extract-query-examples .result').append(errorThrown);
            }
        }
        $.ajax(server+url, settings);
    }

    $('#extract-query-examples button').click(function(){
        $('#extract-query-examples .loading').show(500);
        $('#extract-query-examples .result').hide(500);
        runQuery($('#extract-query-examples textarea').val());
    });

    $('#extract-query-examples span.example').click(function() {
        var url_partial = $("<div/>").html($(this).html()).text();
        $('#extract-query-examples textarea').val(url_partial);
    }) 

    $(document).bind('deck.change', function(event, from, to) {
        if (from === 31 || to === 31) {
             $('#extract-query-examples .result').hide(500).html("");
        }

    });

    $('#map-functions-described a.show-code').click(function() {

        var $dialog = $('<div></div>')
        .html(JSON.stringify(exports.alignment_data, null, '&nbsp;').replace(/\n/g, "<br/>"))
        .dialog({
            autoOpen: true,
            title: 'Sample Resource Data Documents',
            height: 500,
            width: 800
        });
    
    });


});