document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('payment-form');
    const loader = document.getElementById('loader');
    const successMessage = document.getElementById('success-message');
    const paymentHeader = document.getElementById('payment-header');
    const bookingDetails = document.getElementById('booking-details'); // Get the booking details div
    const paymentContainer = document.querySelector('.payment-container'); // Get the container

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission
        console.log('Form submitted');  // Debugging log

        // Get form data
        const formData = new FormData(form);

        // Hide form, booking details, and header, show loader
        form.style.display = 'none';
        bookingDetails.style.display = 'none';
        paymentHeader.style.display = 'none';
        loader.style.display = 'block'; // Make loader visible

        // Remove the background using JavaScript
        paymentContainer.style.backgroundColor = 'transparent'; // Set background to transparent

        // Send data to Django backend
        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: formData,
        })
            .then((response) => {
                console.log('Response received');
                if (!response.ok) {
                    return response.text().then(text => { throw new Error(text || 'Payment failed. Please try again.'); });
                }
                return response.json();
            })
            .then((data) => {
                console.log('Data received', data); // Log successful data

                // Force the loader to stay visible for 2 seconds
                setTimeout(() => {
                    loader.style.display = 'none'; // Hide loader
                    successMessage.style.display = 'block';
                    document.querySelector('.details').innerHTML = `
                        <p><strong>Amount Paid:</strong> $${data.amount}</p>
                        <p><strong>Date & Time:</strong> ${data.date_time}</p>
                        <p><strong>Reference Number:</strong> ${data.reference_number}</p>
                    `;
                }, 2000); // Wait for 2 seconds before hiding loader
            })
            .catch((error) => {
                console.error(error); // Log error for debugging
                alert(error.message);
                loader.style.display = 'none'; // Hide loader
                form.style.display = 'block';
                bookingDetails.style.display = 'block'; // Show booking details again
                paymentHeader.style.display = 'block';
                paymentContainer.style.backgroundColor = ''; // Reset background
            });
    });
});
