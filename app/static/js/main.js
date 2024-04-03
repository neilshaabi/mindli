$(document).ready(function() {

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
});

// Updates profile picture
function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function(){
        var output = $('#profile-picture-preview');
        output.attr('src', reader.result);
        output.removeClass('default-pic');
    };
    reader.readAsDataURL(event.target.files[0]);
}
