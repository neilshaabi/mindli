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

// Function to display error messages
function displayFormErrors(errors) {
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

function ajaxFormResponseHandler(response) {
    
    // Clear previous errors
    $('.error-message').remove();
    $('.input-error').removeClass('input-error');

    if (response.success) {
        if (response.url) {
            window.location = response.url;
        }
    } else {
        if (response.errors) {
            displayFormErrors(response.errors);
        }
    }
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
    


    // Registration handler using AJAX
    $('#register-form').on('submit', function(event) {
        
        event.preventDefault();
        showLoadingBtn(true);

        $.post('/register', {
            'role': $('input[name="role"]:checked').attr('id'),
            'first_name': $('#first_name').val(),
            'last_name': $('#last_name').val(),
            'email': $('#email').val(),
            'password': $('#password').val()
        },
        function(data) {
            showLoadingBtn(false);
            ajaxFormResponseHandler(data);
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
                showLoadingBtn(false);
                ajaxFormResponseHandler(data);
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
                ajaxFormResponseHandler(data);
            }
        );
    });


    // Password reset request handler using AJAX
    $('#initiate-password-reset-form').on('submit', function(event) {

        event.preventDefault();
        showLoadingBtn(true);

        $.post(
            '/reset-password', {
                'form-type': 'initiate_password_reset',
                'email': $('#email').val()
            },
            function(data) {
                showLoadingBtn(false);
                ajaxFormResponseHandler(data);
            }
        );
    });


    // Password reset handler using AJAX
    $('#reset-password-form').on('submit', function(event) {

        event.preventDefault();
        showLoadingBtn(true)

        $.post(
            '/reset-password', {
                'form-type': 'reset_password',
                'email': $('#email').val(),
                'password': $('#password').val(),
                'password_confirmation': $('#password_confirmation').val()
            },
            function(data) {
                showLoadingBtn(false);
                ajaxFormResponseHandler(data);
            }
        );
    });
});
