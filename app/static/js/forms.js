function handleSubmitForm(formID, endpoint) {
    
    $('#' + formID).on('submit', function(event) {
        
        event.preventDefault();

        // Show loading button
        $(":input[type='submit']").prop('disabled', true);
        $('.btn-text').hide();
        $('.spinner-border').show();

        var formData = $(this).serialize();
        formData += "&form-id=" + $(this).attr('id');

        $.post(endpoint, formData, function(data) {
            
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
                
                // Display error messages for each input field
                if (response.errors) {
                    for (const key in response.errors) {
                        const inputField = $('#' + key);
                        const errorMessage = $(
                            '<div class="error-message">' 
                                + '<i class="fa-solid fa-circle-exclamation"></i> ' 
                                + response.errors[key] 
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

    // Event listener for the toggle button
    $('#togglePassword').click(function() {
        
        // Toggle the type attribute of the password field
        const passwordFieldType = $('#password').attr('type') === 'password' ? 'text' : 'password';
        $('#password').attr('type', passwordFieldType);

        // Toggle the icon class
        const icon = $(this).find('i');
        if (passwordFieldType === 'password') {
            icon.removeClass('fa-eye-slash').addClass('fa-eye');
        } else {
            icon.removeClass('fa-eye').addClass('fa-eye-slash');
        }
    });
    
    // Form handlers using AJAX
    handleSubmitForm('register-form', '/register');
    handleSubmitForm('login-form', '/login');
    handleSubmitForm('verify-email-form', '/verify-email');
    handleSubmitForm('initiate-password-reset-form', '/reset-password');
    handleSubmitForm('reset-password-form', '/reset-password');
});
