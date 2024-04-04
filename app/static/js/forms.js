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

    // Auth forms
    handleSubmitForm('register-form', '/register');
    handleSubmitForm('login-form', '/login');
    handleSubmitForm('verify-email-form', '/verify-email');
    handleSubmitForm('initiate-password-reset-form', '/initiate-password-reset');
    handleSubmitForm('reset-password-form', '/reset-password');

    // Profile forms
    handleSubmitForm('user-profile-form', '/profile/user');
    handleSubmitForm('therapist-profile-form', '/profile/therapist');
    handleSubmitForm('client-profile-form', '/profile/client');
});


function handleSubmitForm(formID, endpoint) {
    
    $('#' + formID).on('submit', function(event) {
        
        event.preventDefault();

        var submitBtn = $(this).find(":input[type='submit']");
        var btnText = $(this).find('.btn-text');
        var btnSpinner = $(this).find('.spinner-border');
        var errorMessages = $(this).find('.error-message');
        var errorInputs = $(this).find('.input-error');

        $.ajax({
            url: endpoint,
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
                        if (key === 'profile_picture') {
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
