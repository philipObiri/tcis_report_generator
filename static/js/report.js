$(document).ready(function () {
    $('#generate-report-btn').on('click', function (e) {
        e.preventDefault();

        const studentName = $('#student-name').text().trim();
        const classYear = $('#class-year').text().trim();
        const selectedTerm = $('#term-dropdown').val().trim();

        if (!studentName) {
            Swal.fire('Error!', 'Please select a student first from the saved scores list.', 'error');
            return;
        }

        if (!selectedTerm) {
            Swal.fire('Error!', 'Please select a term to generate the report.', 'error');
            return;
        }

        // Step 1: Confirm generation
        Swal.fire({
            title: 'Generate Report?',
            text: `Do you want to generate a report for ${studentName} in ${selectedTerm}?`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'Yes, Continue',
            cancelButtonText: 'Cancel'
        }).then(function (confirmResult) {
            if (confirmResult.isConfirmed) {
                // Step 2: Fetch existing comment
                $.ajax({
                    url: '/dashboard/get_comment/',
                    type: 'POST',
                    contentType: 'application/json',
                    headers: {
                        'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
                    },
                    data: JSON.stringify({
                        student_name: studentName,
                        class_year: classYear,
                        term: selectedTerm
                    }),
                    success: function (response) {
                        const existingComment = response.comment || '';

                        // Step 3: Ask for (or edit) comment
                        Swal.fire({
                            title: 'Enter Report Comment',
                            input: 'textarea',
                            inputLabel: 'Comment (optional)',
                            inputValue: existingComment,
                            inputPlaceholder: 'Enter comment for this academic report...',
                            showCancelButton: true,
                            confirmButtonText: 'Submit & Generate',
                            cancelButtonText: 'Cancel'
                        }).then(function (commentResult) {
                            if (commentResult.isConfirmed) {
                                const userComment = commentResult.value;

                                // Step 4: Send data to generate report
                                $.ajax({
                                    url: '/reports/generate_report/',
                                    type: 'POST',
                                    contentType: 'application/json',
                                    headers: {
                                        'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
                                    },
                                    data: JSON.stringify({
                                        student_name: studentName,
                                        class_year: classYear,
                                        term: selectedTerm,
                                        comment: userComment
                                    }),
                                    success: function (data) {
                                        if (data.success && data.report_html) {
                                            const newTab = window.open('', '_blank');
                                            newTab.document.write('<html><head><title>Academic Report</title></head><body>');
                                            newTab.document.write(data.report_html);
                                            newTab.document.write('</body></html>');
                                        } else {
                                            Swal.fire('Error!', data.error || 'An error occurred while generating the report.', 'error');
                                        }
                                    },
                                    error: function () {
                                        Swal.fire('Error!', 'An unexpected error occurred during report generation.', 'error');
                                    }
                                });
                            }
                        });
                    },
                    error: function () {
                        Swal.fire('Error!', 'Failed to fetch existing comment.', 'error');
                    }
                });
            }
        });
    });
});
