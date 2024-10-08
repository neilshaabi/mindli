$(document).ready(function() {

    // Enable Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

    // Hide/show tooltips depending on sidebar
    toggleSidebarTooltips();
    
    // Toggle active state for navbar link when selected
    var activePage = $('body').data('active-page');
    $('.nav-link').each(function() {
        var $this = $(this);
        if ($this.data('page') === activePage) {
            $this.addClass('active');
        }
    });

    // Expands/collapses sidebar when toggler clicked
    $('.sidebar .navbar-toggler').click(function() {
        
        collapseSidebar();
    
        // Toggle collapsed class for the sidebar
        $('.sidebar').toggleClass('collapsed');
        
        toggleSidebarTooltips();
        
        // Show sidebar text with delay to account for transition
        if (!$('.sidebar').hasClass('collapsed')) {
            expandSidebar();
        }
    });


    // Initial call to set the class based on window width on page load
    resizeSidebar();

    // Event listener for window resize to update class accordingly
    $(window).resize(function() {
        resizeSidebar();
    });



    // Display onboarding modal by default when page loads
    $(window).on('load', function() {
        $('#onboardingModal').modal('show');
    });
    

    // Update preview of profile picture when uploaded
    $('#profile_picture').change(function(event) {
        var reader = new FileReader();
        reader.onload = function(){
            var output = $('#profile-picture-preview');
            output.attr('src', reader.result);
        };
        reader.readAsDataURL(event.target.files[0]);
    });

    
    // Disable submit buttons in forms with input elements until changed
    $('form').each(function() {
        var form = $(this);

        // Do not disable submit buttons for filter forms
        if (form.attr('id') && form.attr('id').indexOf('filter') !== -1) {
            return;
        }

        // Do not disable buttons with no visible input elements
        if (form.find('input[type!=hidden], textarea, select').length > 0) {
            form.find(':submit').prop('disabled', true);

            // Attach an event listener to enable the submit button when any visible input, textarea, or select element changes
            form.on('change input', 'input[type!=hidden], textarea, select', function() {
                form.find(':submit').prop('disabled', false);
            });
        }
    });


    // Check URL for a 'section' parameter to determine the default section
    let params = new URLSearchParams(window.location.search);
    let defaultSection = params.get('section') || $('#section-selector').data('default-section');
    if (defaultSection) {
        
        defaultSectionID = '#' + defaultSection;
        
        // Hide all other sections
        $('.section').hide();
        $('#section-selector .list-group-item').removeClass('active');
        
        // Fall back to first section if default section does not exist
        if ($(defaultSectionID).length == 0) {
            defaultSectionID = $('#section-selector .list-group-item:first').data('target');
        }

        // Show default section and toggle active styling for menu item
        $(defaultSectionID).show();
        $('#section-selector .list-group-item[data-target="' + defaultSectionID + '"]').addClass('active');
    }

    
    // Toggle section when corresponding item in section selector is clicked
    $('#section-selector .list-group-item').click(function() {
    
        // Remove active class from all items and add to the clicked one
        $('#section-selector .list-group-item').removeClass('active');
        $(this).addClass('active');

        // Show only the section corresponding to the clicked item if one exists
        var target = $(this).data('target');
        if (target) {
            $('.section').hide();
            $(target).show();
        }

        var messagesContainer = $(target).find('.messages-container');
        messagesContainer.scrollTop(messagesContainer.prop('scrollHeight'));

        // Update the URL query string with the new section
        var newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?section=' + target.substring(1);
        window.history.pushState({ path: newUrl }, '', newUrl);
    });


    // Toggle between preview and form for treatment plan when button clicked
    $('#toggle-treatment-plan').click(function() {
        form = $('#treatment-plan-form');
        preview = $('#treatment-plan-preview');
        if (form.hasClass('hidden')) {
            preview.addClass('hidden');
            form.removeClass('hidden');
            $(this).html('<i class="fa-solid fa-magnifying-glass"></i><span>Preview</span>')
        } else {
            form.addClass('hidden');
            preview.removeClass('hidden');
            $(this).html('<i class="fa-solid fa-pen-to-square"></i><span>Edit</span>')
        }
    });

    
    // Set scroll position to bottom for messages
    $(window).on('load', function() {
        var messagesContainer = $('.messages-container');
        messagesContainer.scrollTop(messagesContainer.prop('scrollHeight'));
    });
    

    // Function to toggle disabled attribute on input fields and button visibility
    $('.enable-form-btn').click(function() {
        var formId = $(this).attr('form');
        $(':input[form="' + formId + '"]').prop('disabled', false);
        $('span[data-bs-target="#deleteAppointmentTypeModal"][form="' + formId + '"]').removeClass('hidden');
        $('button[form="' + formId + '"]').parent().removeClass('hidden');
        $(this).parent().addClass('hidden');
    });


    // Function to toggle input fields and enable submit button
    $('#action').change(function() {

        var selectedAction = $(this).val();
        var datetimeFields = $('.datetime-field');
                
        // Disable input button when no action selected
        var submitBtn = $('#submit-btn');
        if (selectedAction === '') {
            submitBtn.prop('disabled', true);
        } else {
            submitBtn.prop('disabled', false);
        }

        // Show date and time fields when action is rescheduled
        if (selectedAction === 'RESCHEDULED') {
            datetimeFields.removeClass('hidden');
        } else {
            datetimeFields.addClass('hidden');
        }
    });
    

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


// Collapse the sidebar automatically on small screens
function resizeSidebar() {
    var screenWidth = $(window).width();
    var sidebar = $('.sidebar');
    if (screenWidth < 1000) {
        collapseSidebar();
        sidebar.addClass('collapsed');
    } else if (!sidebar.hasClass('collapsed')) {
        sidebar.removeClass('collapsed');
        expandSidebar();
    }
    toggleSidebarTooltips();
}


function collapseSidebar() {
    $('.sidebar .navbar-brand').hide();
    $('.sidebar .nav-link span').hide();
}

function expandSidebar() {
    setTimeout(function() {
        $('.sidebar .navbar-brand').show();
        $('.sidebar .nav-link span').show();
        }, 
    150);
}


// Enable sidebar tooltips only when collapsed, otherwise disable
function toggleSidebarTooltips() {

    const sidebarTooltips = $('.sidebar [data-bs-toggle="tooltip"]');

    if ($('.sidebar').hasClass('collapsed')) {
        sidebarTooltips.each(function() {
            const tooltip = bootstrap.Tooltip.getInstance(this);
            tooltip.enable();
        });
    } else {
        sidebarTooltips.each(function() {
            const tooltip = bootstrap.Tooltip.getInstance(this);
            tooltip.disable();
        });
    }
}


// Handles form submissions via AJAX
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
            beforeSend: function() {
                // Show loading state for submit button, remove flashed messages
                submitBtn.prop('disabled', true);
                btnText.hide();
                btnSpinner.show();
                $('.flashed-message').remove();
            },
            success: function(response) {

                // Remove flashed messages
                $('#flashed-messages-container').empty();

                // Remove previous error messages for this form
                var existingErrorMessages = $('.error-message[data-form-id="' + formId + '"]');
                existingErrorMessages.each(function() {
                    $(this).remove()
                });

                // Remove previous error indicators for this form
                var existingErrorInputs = $('.input-error[data-form-id="' + formId + '"]');
                existingErrorInputs.removeClass('input-error');

                // Display flashed message using macro
                if (response.flashed_message_html) {
                    $('#flashed-messages-container').html(response.flashed_message_html);
                }

                // Redirect to url
                if (response.url) {
                    window.location = response.url;
                }
                
                // Successful response
                if (response.success) {
                    
                    if (response.update_targets) { // Replace multiple elements with new HTML
                        for (var target in response.update_targets) {
                            $('#' + target).html(response.update_targets[target]);
                        }
                    }
                } else if (response.errors) { // Display form errors
                    var formPrefix = response.form_prefix ? response.form_prefix + "-" : "";
                    displayFormErrors(formId, formPrefix, response.errors);
                } else if (response.redirect) { // Redirect
                    window.location = response.redirect;
                }
            },
            error: function() {
                window.location = '/error';å
            },
            complete: function() {
                // Hide loading button only for this form
                submitBtn.prop('disabled', false);
                btnText.show();
                btnSpinner.hide();
            }
        });
    });
}

function displayFormErrors(formId, formPrefix, errors) {
    
    var newErrorMessages = {};
    var existingErrorMessages = $('.error-message[data-form-id="' + formId + '"]');
    var existingErrorInputs = $('.input-error[data-form-id="' + formId + '"]');

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
                    '<span>' +
                newErrorMessages[key] +
                '</span>' +
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
