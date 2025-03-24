document.addEventListener('DOMContentLoaded', function () {
    const generateReportBtn = document.getElementById('generate-report-btn');

    generateReportBtn.addEventListener('click', function (e) {
        e.preventDefault();

        // Grab the selected term and student details
        const studentName = document.getElementById('student-name').innerText.trim();
        const classYear = document.getElementById('class-year').innerText.trim();
        const selectedTerm = document.getElementById('term-dropdown').value.trim();

        // Validate if a student is selected
        if (!studentName) {
            Swal.fire({
                title: 'Error!',
                text: 'Please select a student first from the saved scores list.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
            return;  // Stop further execution
        }

        // Validate if a term is selected
        if (!selectedTerm) {
            Swal.fire({
                title: 'Error!',
                text: 'Please select a term to generate the report.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
            return;  // Stop further execution
        }

        // Confirm before generating the report
        Swal.fire({
            title: 'Generate Mock Report?',
            text: `Do you want to generate a mock report for ${studentName} in ${selectedTerm}?`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'Yes, Generate',
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                // Prepare the data to send with the request
                const reportData = {
                    student_name: studentName,
                    class_year: classYear,
                    term: selectedTerm
                };

                // Make the AJAX request to generate the report
                fetch('/reports/generate_mock_report/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // CSRF token
                    },
                    body: JSON.stringify(reportData),
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.report_html) {
                            // Open the generated report in a new tab
                            const reportWindow = window.open('', '_blank');
                            reportWindow.document.write('<html><head><title>Mock Report</title></head><body>');
                            reportWindow.document.write(data.report_html);  // Insert the HTML content here
                            reportWindow.document.write('</body></html>');
                        } else {
                            // Handle error if report generation fails
                            Swal.fire({
                                title: 'Error!',
                                text: data.error || 'An error occurred while generating the report.',
                                icon: 'error',
                                confirmButtonText: 'OK'
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire({
                            title: 'Error!',
                            text: 'An unexpected error occurred.',
                            icon: 'error',
                            confirmButtonText: 'OK'
                        });
                    });
            }
        });
    });
});
