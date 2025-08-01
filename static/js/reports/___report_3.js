$(document).ready(function () {
    $('#generate-report-btn').on('click', function (e) {
        e.preventDefault();

        const studentName = $('#student-name').text().trim();
        const classYear = $('#class-year').text().trim();
        const selectedTerm = $('#term-dropdown').val().trim();

        if (!studentName || !selectedTerm) {
            Swal.fire('Error!', 'Please select a student and a term first.', 'error');
            return;
        }

        Swal.fire({
            title: 'Generate Report?',
            text: `Do you want to generate a report for ${studentName} in ${selectedTerm}?`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'Yes, Continue',
            cancelButtonText: 'Cancel'
        }).then(function (confirmResult) {
            if (!confirmResult.isConfirmed) return;

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
                    const academicComment = response.academic_comment || '';
                    const behavioralComment = response.behavioral_comment || '';
                    const savedPromotion = response.promotion || '';

                    let htmlContent = `
                        <div style="margin-bottom: 15px; text-align: left;">
                            <label for="academic-comment" style="font-weight:600;">Academic Comment</label>
                            <textarea id="academic-comment" class="swal2-textarea" style="width:100%; min-height: 80px;">${academicComment}</textarea>
                        </div>
                        <div style="margin-bottom: 15px; text-align: left;">
                            <label for="behavioral-comment" style="font-weight:600;">Behavioral Comment</label>
                            <textarea id="behavioral-comment" class="swal2-textarea" style="width:100%; min-height: 80px;">${behavioralComment}</textarea>
                        </div>
                    `;

                    // Only show promotion dropdown for Term 3
                    if (selectedTerm === 'Term 3') {
                        htmlContent += `
                            <div style="margin-top:15px; text-align:left;">
                                <label for="promotion-select" style="font-weight:600;">Promoted to:</label>
                                <select id="promotion-select" class="swal2-select" style="width:100%; margin-top: 5px;">
                                    <option value="">-- Select Class Year --</option>
                                    <option value="Year 7 (Lower Secondary)">Year 7 (Lower Secondary)</option>
                                    <option value="Year 8 (Lower Secondary)">Year 8 (Lower Secondary)</option>
                                    <option value="Year 9 (Lower Secondary)">Year 9 (Lower Secondary)</option>
                                    <option value="Year 10 (Upper Secondary)">Year 10 (Upper Secondary)</option>
                                    <option value="Year 11 (Upper Secondary)">Year 11 (Upper Secondary)</option>
                                    <option value="Year 12 (Sixth Form)">Year 12 (Sixth Form)</option>
                                    <option value="Year 13 (Sixth Form)">Year 13 (Sixth Form)</option>
                                </select>
                            </div>
                        `;
                    }

                    Swal.fire({
                        title: 'Add Comments',
                        html: htmlContent,
                        showCancelButton: true,
                        confirmButtonText: 'Submit & Generate',
                        cancelButtonText: 'Cancel',
                        focusConfirm: false,
                        width: '600px', // Make the modal wider
                        didOpen: () => {
                            // Set the saved promotion value if it's Term 3
                            if (selectedTerm === 'Term 3' && savedPromotion) {
                                const promotionSelect = document.getElementById('promotion-select');
                                if (promotionSelect) {
                                    promotionSelect.value = savedPromotion;
                                }
                            }
                        },

                        preConfirm: () => {
                            const academic_comment = document.getElementById('academic-comment').value.trim();
                            const behavioral_comment = document.getElementById('behavioral-comment').value.trim();
                            
                            // Initialize promotion as empty string
                            let promotion = '';
                            
                            // Only get promotion value if it's Term 3 and the select exists
                            if (selectedTerm === 'Term 3') {
                                const promotionSelect = document.getElementById('promotion-select');
                                if (promotionSelect) {
                                    promotion = promotionSelect.value.trim();
                                }
                            }

                            // Validation: At least one comment is required
                            if (!academic_comment && !behavioral_comment) {
                                Swal.showValidationMessage('At least one comment is required');
                                return false;
                            }

                            return { academic_comment, behavioral_comment, promotion };
                        }

                    }).then(result => {
                        if (!result.isConfirmed) return;
                        
                        const { academic_comment, behavioral_comment, promotion } = result.value;
                        
                        // Show loading state
                        Swal.fire({
                            title: 'Generating Report...',
                            text: 'Please wait while we generate your report.',
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                            showConfirmButton: false,
                            didOpen: () => {
                                Swal.showLoading();
                            }
                        });

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
                                academic_comment: academic_comment,
                                behavioral_comment: behavioral_comment,
                                promotion: promotion
                            }),

                            success: function (data) {
                                Swal.close(); // Close loading dialog
                                
                                if (data.success && data.report_html) {
                                    // Success message
                                    Swal.fire({
                                        title: 'Success!',
                                        text: 'Report generated successfully!',
                                        icon: 'success',
                                        timer: 2000,
                                        showConfirmButton: false
                                    });

                                    // Open report in new tab
                                    const newTab = window.open('', '_blank');
                                    if (newTab) {
                                        newTab.document.write('<!DOCTYPE html><html><head><title>Academic Report</title></head><body>');
                                        newTab.document.write(data.report_html);
                                        newTab.document.write('</body></html>');
                                        newTab.document.close();
                                    } else {
                                        Swal.fire('Warning!', 'Report generated but popup was blocked. Please allow popups for this site.', 'warning');
                                    }
                                } else {
                                    Swal.fire('Error!', data.error || 'Failed to generate report.', 'error');
                                }
                            },
                            error: function (xhr, status, error) {
                                Swal.close(); // Close loading dialog
                                console.error('AJAX Error:', error);
                                Swal.fire('Error!', 'Unexpected error during report generation. Please try again.', 'error');
                            }
                        });
                    });
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching comments:', error);
                    Swal.fire('Error!', 'Failed to fetch existing comments. Please try again.', 'error');
                }
            });
        });
    });
});