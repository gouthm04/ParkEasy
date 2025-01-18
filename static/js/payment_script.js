document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('payment-form');
    const loader = document.getElementById('loader');
    const successMessage = document.getElementById('success-message');
    const paymentHeader = document.getElementById('payment-header');
    const paymentContainer = document.querySelector('.payment-container'); // Get the container

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission

        // Get form data
        const formData = new FormData(form);

        // Hide form and header, show loader
        form.style.display = 'none';
        paymentHeader.style.display = 'none';
        loader.style.visibility = 'visible';

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
                console.log(response); // Log response for debugging
                if (!response.ok) {
                    return response.text().then(text => { throw new Error(text || 'Payment failed. Please try again.'); });
                }
                return response.json();
            })
            .then((data) => {
                console.log(data); // Log successful data
                loader.style.visibility = 'hidden';
                successMessage.style.display = 'block';
                document.querySelector('.details').innerHTML = `
            <p><strong>Amount Paid:</strong> $${data.amount}</p>
            <p><strong>Date & Time:</strong> ${data.date_time}</p>
            <p><strong>Reference Number:</strong> ${data.reference_number}</p>
        `;
            })
            .catch((error) => {
                console.error(error); // Log error for debugging
                alert(error.message);
                loader.style.visibility = 'hidden';
                form.style.display = 'block';
                paymentHeader.style.display = 'block';
                paymentContainer.style.backgroundColor = ''; // Reset background
            });

    });
});
