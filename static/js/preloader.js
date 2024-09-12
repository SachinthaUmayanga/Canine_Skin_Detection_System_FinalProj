document.addEventListener('DOMContentLoaded', function () {
    // Find the upload form and button
    const uploadForm = document.querySelector('form');
    const preloader = document.getElementById('preloader');

    // Add an event listener to the form submit event
    if (uploadForm) {
        uploadForm.addEventListener('submit', function (e) {
            // Prevent the form from submitting immediately
            e.preventDefault();

            // Show the preloader
            preloader.classList.remove('d-none');

            // Simulate form submission after a slight delay for demonstration purposes
            setTimeout(() => {
                // Submit the form
                uploadForm.submit();
            }, 500); // Adjust this delay as needed
        });
    }
});
