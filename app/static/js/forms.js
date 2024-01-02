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


    // Registration handler using AJAX
    $('#register-form').on('submit', function(event) {

        showLoadingBtn(true);

        $.post(
            '/register', {
                'first_name': $('#first_name').val(),
                'last_name': $('#last_name').val(),
                'email': $('#email').val(),
                'password': $('#password').val()
            },
            function(data) {

                // Display error message if unsuccessful
                if (data.error) {
                    showLoadingBtn(false);
                    $('#error-alert').html(data.error).show();
                }

                // Reload page if successful
                else {
                    window.location = data;

                }
            }
        );
        event.preventDefault();
    });


    // Login handler using AJAX
    $('#login-form').on('submit', function(event) {

        showLoadingBtn(true);

        $.post(
            '/login', {
                'email': $('#email').val(),
                'password': $('#password').val()
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
        event.preventDefault();
    });


    // Resend email verification handler using AJAX
    $('#verify-email-form').on('submit', function(event) {

        showLoadingBtn(true);

        $.post(
            '/verify-email', {},
            function(data) {
                showLoadingBtn(false);
            }
        );
        event.preventDefault();
    });


    // Password reset request handler using AJAX
    $('#reset-request-form').on('submit', function(event) {

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
        event.preventDefault();
    });


    // Password reset handler using AJAX
    $('#reset-password-form').on('submit', function(event) {

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
                    window.location = data;
                }
            }
        );
        event.preventDefault();
    });

});
