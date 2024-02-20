// Function to display error messages
function displayFormErrors(errors) {
    
    // Clear previous errors
    $('.error-message').remove();
    $('.input-error').removeClass('input-error');

    // Display new errors below corresponding input fields
    for (const key in errors) {
        const inputField = $('#' + key);
        const errorMessage = $(
            '<div class="error-message">' 
                + '<i class="fa-solid fa-circle-exclamation"></i> ' 
                + errors[key] 
            + '</div>'
        );
        inputField.after(errorMessage);
        inputField.addClass('input-error');
    }   
}

$(document).ready(function() {

    // Toggles loading button
    function showLoadingBtn(isLoading) {
        if (isLoading == true) {
            $(":input[type='submit']").prop('disabled', true);
            $('.btn-text').hide();
            $('.spinner-border').show();
        } else {
            $(":input[type='submit']").prop('disabled', false);
            $('.btn-text').show();
            $('.spinner-border').hide();
        }
    }

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


    // Registration handler using AJAX
    $('#register-form').on('submit', function(event) {
        
        event.preventDefault();
        showLoadingBtn(true);

        $.post('/register', {
            'first_name': $('#first_name').val(),
            'last_name': $('#last_name').val(),
            'email': $('#email').val(),
            'password': $('#password').val()
        },
        function(data) {
            if (data.errors) {
                showLoadingBtn(false);
                displayFormErrors(data.errors);
            } else {
                window.location = data.url;
            }
        });
    });


    // Login handler using AJAX
    $('#login-form').on('submit', function(event) {
        
        event.preventDefault();
        showLoadingBtn(true);

        $.post(
            '/login', {
                'email': $('#email').val(),
                'password': $('#password').val()
            },
            function(data) {
                if (data.errors) {
                    showLoadingBtn(false);
                    displayFormErrors(data.errors);
                } else {
                    window.location = data.url;
                }
            }
        );
    });


    // Resend email verification handler using AJAX
    $('#verify-email-form').on('submit', function(event) {

        event.preventDefault();
        showLoadingBtn(true);

        $.post(
            '/verify-email', {},
            function(data) {
                showLoadingBtn(false);
            }
        );
    });


    // Password reset request handler using AJAX
    $('#reset-request-form').on('submit', function(event) {

        event.preventDefault();
        showLoadingBtn(true);

        $.post(
            '/reset-password', {
                'form-type': 'request',
                'email': $('#email').val()
            },
            function(data) {

                // Display error message if unsuccessful
                if (data.error) {
                    showLoadingBtn(false);
                    $('#error-alert').html(data.error).show();
                }

                // Redirect to home page if successful
                else {
                    window.location = data;
                }
            }
        );
    });


    // Password reset handler using AJAX
    $('#reset-password-form').on('submit', function(event) {

        event.preventDefault();
        showLoadingBtn(true)

        $.post(
            '/reset-password', {
                'form-type': 'reset',
                'email': $('#email').val(),
                'password': $('#password').val(),
                'password_confirmation': $('#password_confirmation').val()
            },
            function(data) {

                // Display error message if unsuccessful
                if (data.error) {
                    showLoadingBtn(false)
                    $('#error-alert').html(data.error).show();
                }

                // Redirect to home page if successful
                else {
                    console.log(data)
                    window.location = data;
                }
            }
        );
    });
});
