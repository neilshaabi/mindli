$(document).ready(function() {

    // Enable Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
    
    // Toggle active state for navbar link when selected
    var pathname = window.location.pathname;
    var links = document.getElementsByClassName('nav-link');
    for (var i = 0; i < links.length; i++) {
        if (pathname == links[i].getAttribute('href')) {
            links[i].classList.add('active');
            break;
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
 
     // Set the delete modal's hidden field with the correct appointment type id
     $('#deleteAppointmentTypeModal').on('show.bs.modal', function (event) {
         var modalToggler = $(event.relatedTarget);
         var formId = modalToggler.attr('form');
         var appointment_type_id = formId.replace('appointment_type_', '');
         $(this).find('input[name="appointment_type_id"]').val(appointment_type_id);
     });
});


// Updates profile picture
function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function(){
        var output = $('#profile-picture-preview');
        output.attr('src', reader.result);
        output.removeClass('default-profile-picture');
    };
    reader.readAsDataURL(event.target.files[0]);
}


function enableFields(button) {
    
    // Get the form ID from the edit button
    var formId = $(button).attr('form');
    $(':input[form="' + formId + '"]').prop('disabled', false);
    
    // Toggle button visibility
    $(button).addClass('hidden');
    $('span[data-bs-target="#deleteAppointmentTypeModal"][form="' + formId + '"]').removeClass('hidden');
    $('button[type="submit"][form="' + formId + '"]').removeClass('hidden');
}

function registerFormHandlers() {

    // Store last clicked submit button to send with request
    $(':submit').click(function() {
        var form = $(this).closest('form');
        form.data({submit: {name: $(this).attr('name'), value: $(this).val()}});
    });
    
    $('form').on('submit', function(event) {
        
        event.preventDefault();

        var form = $(this);
        var formId = form.attr('id');
        var formData = new FormData(this);
        
        var submitBtn = form.find(":input[type='submit']");
        var btnText = submitBtn.find('.btn-text');
        var btnSpinner = submitBtn.find('.spinner-border');

        // Add name of clicked submit button
        var submitData = form.data('submit');
        if (submitData) {
            formData.append('submit', submitData.name);
        }

        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            beforeSend: function() { // Show loading state for submit button, remove flashed messages
                submitBtn.prop('disabled', true);
                btnText.hide();
                btnSpinner.show();
                $('.flashed-message').remove();
            },
            success: function(response) {
                if (response.success) {
                    if (response.url) { // Redirect user to url
                        window.location = response.url;
                    } else if (response.update_target) { // Replace element with new HTML
                        $('#' + response.update_target).html(response.updated_html)
                    }
                } else if (response.errors) { // Display form errors
                    var formPrefix = response.form_prefix ? response.form_prefix + "-" : "";
                    displayFormErrors(formId, formPrefix, response.errors);
                }
            },
            error: function() {
                // window.location = '/error'; // TODO
            },
            complete: function() { // Hide loading button only for this form
                submitBtn.prop('disabled', false);
                btnText.show();
                btnSpinner.hide();
            }
        });
    });
}

function displayFormErrors(formId, formPrefix, errors) {
    var existingErrorMessages = $('.error-message[data-form-id="' + formId + '"]');
    var existingErrorInputs = $('.input-error[data-form-id="' + formId + '"]');
    var newErrorMessages = {};

    // Remove previous error indicators for this form
    existingErrorInputs.removeClass('input-error');

    for (const key in errors) {
        var inputField = $('#' + formPrefix + key);
        const firstError = errors[key][0];
        newErrorMessages[formPrefix + key] = firstError;
        inputField.addClass('input-error').attr('data-form-id', formId);
    }

    // Remove outdated error messages and add new ones
    existingErrorMessages.each(function() {
        var thisMessage = $(this);
        var thisKey = thisMessage.data('form-id') + '-' + thisMessage.data('for');
        
        if (newErrorMessages[thisKey]) {
            if (thisMessage.text() !== newErrorMessages[thisKey]) {
                thisMessage.text(newErrorMessages[thisKey]);
            }
            delete newErrorMessages[thisKey];
        } else {
            thisMessage.remove();
        }
    });

    // Add new error messages
    for (const key in newErrorMessages) {
        var inputField = $('#' + key);
        const errorMessage = $(
            '<div class="error-message mt-2" data-form-id="' + formId + '" data-for="' + key + '">' +
                '<i class="fa-solid fa-circle-exclamation"></i> ' +
                newErrorMessages[key] +
            '</div>'
        );
        
        
        // Special handling for checkboxes and radio buttons
        if (inputField.attr('type') === 'checkbox' || inputField.attr('type') === 'radio') {
            inputField = inputField.closest('.form-check');
        }
        
        // Insert error message
        if (key == 'role') {
            inputField.append(errorMessage); // Append to register form's role field
        } else {
            inputField.after(errorMessage); // Insert after individual fields
        }
    }
}
