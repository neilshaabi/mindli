function handleSubmitForm(formID, endpoint) {
    
    $('#' + formID).on('submit', function(event) {
        
        event.preventDefault();

        // Show loading button
        $(":input[type='submit']").prop('disabled', true);
        $('.btn-text').hide();
        $('.spinner-border').show();

        // Retrieve form data with ID
        var formData = $(this).serialize();
        formData += "&form-id=" + $(this).attr('id');

        $.post(endpoint, formData, function(response) {
            
            // Hide loading button
            $(":input[type='submit']").prop('disabled', false);
            $('.btn-text').show();
            $('.spinner-border').hide();
            
            // Clear previous errors
            $('.error-message').remove();
            $('.input-error').removeClass('input-error');

            if (response.success) {
                
                // Redirect if url returned
                if (response.url) {
                    window.location = response.url;
                }
            } else {
                
                // Display first error message for each input field
                if (response.errors) {
                    for (const key in response.errors) {
                        const firstError = response.errors[key][0];
                        const inputField = $('#' + key);
                        const errorMessage = $(
                            '<div class="error-message">' 
                                + '<i class="fa-solid fa-circle-exclamation"></i> ' 
                                + firstError
                            + '</div>'
                        );
                        inputField.after(errorMessage);
                        inputField.addClass('input-error');
                    }
                }
            }
        });
    });
}


$(document).ready(function() {
    
    // Form handlers using AJAX
    handleSubmitForm('register-form', '/register');
    handleSubmitForm('login-form', '/login');
    handleSubmitForm('verify-email-form', '/verify-email');
    handleSubmitForm('initiate-password-reset-form', '/reset-password');
    handleSubmitForm('reset-password-form', '/reset-password');
});
