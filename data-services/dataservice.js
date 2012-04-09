$(function() {
    // Deck initialization
    $.deck('.slide');
    
    $('#style-themes').change(function() {
        $('#style-theme-link').attr('href', $(this).val());
    });
    
    $('#transition-themes').change(function() {
        $('#transition-theme-link').attr('href', $(this).val());
    });


    var server = "http://learnreg1.sri.com";
    function runQuery( url ) {

        var settings = {
            dataType: 'text',
            callback: 'callback',
            success: function (data, textStatus, jqXhr) {
                $('#extract-query-examples .loading').hide(500);
                 $('#extract-query-examples .result').html("<code>"+JSON.stringify(JSON.parse(data), null, 2)+"</code>").show(500);
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

    $(document).bind('deck.change', function(event, from, to) {
        if (from === 26 || to === 26) {
             $('#extract-query-examples .result').hide(500).html("");
        }

    });

});