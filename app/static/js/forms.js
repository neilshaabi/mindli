$(document).ready(function() {

    // Setup CSRF token for AJAX requests
    var csrf_token = "{{ csrf_token() }}";
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    // Register submission handlers for all forms using AJAX
    registerFormHandlers();
});


function registerFormHandlers() {
    
    $('form').on('submit', function(event) {
        
        event.preventDefault();

        var form = $(this);
        var submitBtn = $(form).find(":input[type='submit']");
        var btnText = $(form).find('.btn-text');
        var btnSpinner = $(form).find('.spinner-border');
        var errorMessages = $(form).find('.error-message');
        var errorInputs = $(form).find('.input-error');

        $.ajax({
            url: $(form).attr('action'),
            type: 'POST',
            data: new FormData(this),
            processData: false,
            contentType: false,
            beforeSend: function() {
                // Show loading button only for this form
                $(submitBtn).prop('disabled', true);
                $(btnText).hide();
                $(btnSpinner).show();

                // Clear previous errors for this form
                $(errorMessages).remove();
                $(errorInputs).removeClass('input-error');

                // Remove flashed messages
                $('.flashed-message').remove();
            },
            success: function(response) {
                if (response.success) { // Redirect user
                    window.location = response.url;
                } else if (response.errors) { // Display form errors
                    for (const key in response.errors) {
                        var inputField = $('#' + key);
                        const firstError = response.errors[key][0];
                        const errorMessage = $(
                            '<div class="error-message">' 
                                + '<i class="fa-solid fa-circle-exclamation"></i> ' 
                                + firstError
                            + '</div>'
                        );
                        if (['profile_picture', 'consent'].includes(key)) {
                            inputField = inputField.parent();
                        }
                        inputField.after(errorMessage);
                        inputField.addClass('input-error');
                    }
                } else {
                    window.location = '/error';
                }
            },
            error: function() {
                window.location = '/error';
            },
            complete: function() { // Hide loading button only for this form
                $(submitBtn).prop('disabled', false);
                $(btnText).show();
                $(btnSpinner).hide();
            }
        });
    });
}
