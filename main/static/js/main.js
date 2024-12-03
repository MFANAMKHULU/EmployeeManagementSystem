// Function to get the CSRF token from the cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        // Split the cookies string into individual cookies
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if the current cookie is the one we're looking for
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Get the CSRF token from the cookies
const csrftoken = getCookie('csrftoken');

// Add an event listener to the form for the submit event
document.getElementById('employeeForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Retrieve and trim values from the form fields
    const employeeNumber = document.getElementById('employeeNumber').value.trim();
    let reportsTo = document.getElementById('reportsTo').value.trim(); 

    // If the reportsTo field is empty, replace it with "None"
    if (reportsTo === '') {
        reportsTo = 'None';
    }

    // Check if the reportsTo value is the same as the employee number
    if (reportsTo && reportsTo === employeeNumber) {
        // Display an error message and stop the form submission
        document.getElementById('response-message').innerHTML = '<p style="color:red;">An employee cannot report to themselves.</p>';
        return;
    }

    // Send a POST request to check if the employee number already exists
    fetch('/check_employee_number/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ employeeNumber: employeeNumber })
    })
    .then(response => response.json())
    .then(data => {
        if (data.exists) {
            // Display an error message if the employee number already exists
            document.getElementById('response-message').innerHTML = '<p style="color:red;">Employee number already exists.</p>';
        } else {
            // Prepare the employee data for submission
            const employeeData = {
                employeeNumber: employeeNumber,
                firstName: document.getElementById('firstName').value,
                lastName: document.getElementById('lastName').value,
                email: document.getElementById('email').value,
                birthDate: document.getElementById('birthDate').value,
                salary: document.getElementById('salary').value,
                role: document.getElementById('role').value,
                reportsTo: reportsTo 
            };

            // Send a POST request to register the new employee
            fetch('/employee/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken 
                },
                body: JSON.stringify(employeeData)
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Failed to register employee.');
                }
            })
            .then(data => {
                // Display a success message and reset the form
                document.getElementById('response-message').innerHTML = '<p style="color:green;">Employee registered successfully!</p>';
                document.getElementById('employeeForm').reset();
            })
            .catch(error => {
                // Display an error message if something goes wrong
                document.getElementById('response-message').innerHTML = '<p style="color:red;">' + error.message + '</p>';
            });
        }
    })
    .catch(error => {
        // Display an error message if the check request fails
        document.getElementById('response-message').innerHTML = '<p style="color:red;">' + error.message + '</p>';
    });
});