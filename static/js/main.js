// Document ready function to handle toast notifications
$(document).ready(function(){
    // Show all toasts on page load
    $('.toast').toast('show');
});

document.addEventListener("DOMContentLoaded", function() {
    var navbar = document.getElementById('navbar');
    var sticky = navbar.offsetTop;

    window.onscroll = function() {
        if (window.pageYOffset > sticky + 50) { // Starts being fixed after scrolling down 50px
            navbar.classList.add("fixed-top", "scrolled");
            document.body.classList.add("fixed-navbar");
        } else {
            navbar.classList.remove("fixed-top", "scrolled");
            document.body.classList.remove("fixed-navbar");
        }
    };
});

