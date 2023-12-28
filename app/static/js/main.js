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

    // Set home page height to window height - navbar
    $('#home-page').css('max-height', window.innerHeight - '56px');

    // Toggle between viewing student and associate membership info
    $('.membership-toggles').on('click', function(event) {

        // Do nothing if selected toggle is already active
        if ($(event.target).hasClass('active-toggle')) {
            return;
        }

        // Hide both sections initially
        $('.membership-info').hide();

        // Hide error message
        $('#error-alert').hide();

        // // Show section whose id contains the matching membership type
        var id = (event.target.id).split('-')[0];
        $('.membership-info[id^='' + id + '']').show();

        // // Update styling of selected toggle
        $('.toggle').removeClass('active-toggle');
        $(event.target).addClass('active-toggle');
    });

    // Toggle between viewing exec and frep photos
    $('.team-toggle').on('click', function(event) {

        // Hide both sections initially
        $('.team-swiper').hide();

        // Show swiper whose id contains the matching exec type
        var id = (event.target.id).split('-')[0];
        $('.team-swiper[id^='' + id + '']').show();

        // Update styling of selected toggle
        $('.team-toggle').removeClass('active-toggle');
        $(event.target).addClass('active-toggle');
    });

    // News page swiper
    const newsSwiper = new Swiper('.news-swiper', {

        direction: 'horizontal',
        grabCursor: 'true',
        spaceBetween: 25,
        slidesPerView: 2,
        loop: true,

        pagination: {
            el: '.swiper-pagination',
            dynamicBullets: true,
            clickable: true,
        },

        breakpoints: {
            0: {
                slidesPerView: 1
            },
            700: {
                slidesPerView: 2
            }
        }
    });

    // Team page swiper
    const teamSwiper = new Swiper('.team-swiper', {

        direction: 'horizontal',
        grabCursor: 'true',
        spaceBetween: 25,
        slidesPerView: 3,
        loop: true,

        autoplay: {
            delay: 2500,
            disableOnInteraction: false,
        },

        pagination: {
            el: '.swiper-pagination',
            dynamicBullets: true,
            clickable: true,
        },

        breakpoints: {
            0: {
                slidesPerView: 1
            },
            700: {
                slidesPerView: 2
            },
            1150: {
                slidesPerView: 3
            }
        }
    });

    // Photo page swiper
    const photosSwiper = new Swiper('.photos-swiper', {

        direction: 'horizontal',
        grabCursor: 'true',
        spaceBetween: 25,
        slidesPerView: '1',
        loop: true,

        autoplay: {
            delay: 2500,
            disableOnInteraction: false,
        },

        pagination: {
            el: '.swiper-pagination',
            dynamicBullets: true,
            clickable: true,
        },
    });

    // Member list search bar
    $('#search').on('input', function() {

        var input = $('#search').val().toLowerCase();
        var rows = $('tbody > tr');

        // Show all rows initially
        $(rows).show();

        // Do not hide any rows if search term is empty
        if (input == '') {
            return;
        }

        // Iterate through all rows
        for (var i = 0; i < rows.length; i++) {

            var thisRow = rows[i];
            var cells = thisRow.getElementsByTagName('td');

            var fullName = (cells[1].innerText + ' ' + cells[2].innerText).toLowerCase();
            var studentID = cells[3].innerText;

            // Hide row if it does not contain the search term
            if (!fullName.includes(input) && !studentID.includes(input)) {
                $(thisRow).hide();
            }
        }

    });

});