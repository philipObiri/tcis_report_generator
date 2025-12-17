$(document).ready(function () {
    $('#generate-report-btn').on('click', function (e) {
        e.preventDefault();

        const studentName = $('#student-name').text().trim();
        const classYear = $('#class-year').text().trim();
        const selectedTerm = $('#term-dropdown').val().trim();
        const isHeadClassTeacher = $('#is-head-class-teacher').val() === 'True';

        if (!studentName || !selectedTerm) {
            Swal.fire('Error!', 'Please select a student and a term first.', 'error');
            return;
        }

        // Check if user is a Class Advisor (Head Class Teacher)
        if (!isHeadClassTeacher) {
            Swal.fire('Error!', 'Only Class Advisors (Head Class Teachers) are authorized to generate reports.', 'error');
            return;
        }

        // For Term 3, we need to ask for promotion
        if (selectedTerm === 'Term 3') {
            // Fetch promotion choices and show promotion modal
            $.ajax({
                url: '/dashboard/get_promotion_choices/',
                method: 'GET',
                success: function (choicesResponse) {
                    const choices = choicesResponse.choices || [];

                    // Fetch existing promotion if any
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
                            const savedPromotion = response.promotion || '';
                            showPromotionModal(studentName, classYear, selectedTerm, choices, savedPromotion);
                        },
                        error: function () {
                            showPromotionModal(studentName, classYear, selectedTerm, choices, '');
                        }
                    });
                },
                error: function () {
                    Swal.fire('Error!', 'Failed to load promotion choices.', 'error');
                }
            });
        } else {
            // For Term 1 and Term 2, directly generate report
            confirmAndGenerateReport(studentName, classYear, selectedTerm, '');
        }
    });

    function showPromotionModal(studentName, classYear, selectedTerm, promotionChoices, savedPromotion) {
        let htmlContent = `
            <div style="margin-top:15px; text-align:left;">
                <label for="promotion-select" style="font-weight:600;">Promoted to:</label>
                <select id="promotion-select" class="swal2-select" style="width:100%; margin-top: 5px;">
                    <option value="">-- Select Class Year --</option>
                    ${promotionChoices.map(choice =>
                        `<option value="${choice}" ${choice === savedPromotion ? 'selected' : ''}>${choice}</option>`
                    ).join('')}
                </select>
            </div>
        `;

        Swal.fire({
            title: 'Select Promotion',
            html: htmlContent,
            showCancelButton: true,
            confirmButtonText: 'Generate Report',
            cancelButtonText: 'Cancel',
            focusConfirm: false,
            width: '500px',
            preConfirm: () => {
                const popup = Swal.getPopup();
                const promotionSelect = popup.querySelector('#promotion-select');
                const promotion = promotionSelect ? promotionSelect.value.trim() : '';
                return { promotion };
            }
        }).then(result => {
            if (!result.isConfirmed) return;
            const { promotion } = result.value;
            confirmAndGenerateReport(studentName, classYear, selectedTerm, promotion);
        });
    }

    function confirmAndGenerateReport(studentName, classYear, selectedTerm, promotion) {
        Swal.fire({
            title: 'Generate Report?',
            text: `Do you want to generate a report for ${studentName} in ${selectedTerm}?`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'Yes, Generate',
            cancelButtonText: 'Cancel'
        }).then(function (confirmResult) {
            if (!confirmResult.isConfirmed) return;

            Swal.fire({
                title: 'Generating Report...',
                text: 'Please wait while we generate your report.',
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => Swal.showLoading()
            });

            // Generate report - comments will be fetched from scores saved in formset
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
                    promotion: promotion
                }),
                success: function (data) {
                    Swal.close();
                    if (data.success && data.report_html) {
                        Swal.fire({
                            title: 'Success!',
                            text: 'Report generated successfully!',
                            icon: 'success',
                            timer: 2000,
                            showConfirmButton: false
                        });

                        const newTab = window.open('', '_blank');
                        if (newTab) {
                            newTab.document.write('<!DOCTYPE html><html><head><title>Academic Report</title></head><body>');
                            newTab.document.write(data.report_html);
                            newTab.document.write('</body></html>');
                            newTab.document.close();
                        } else {
                            Swal.fire('Warning!', 'Popup blocked. Please allow popups for this site.', 'warning');
                        }
                    } else {
                        Swal.fire('Error!', data.error || 'Failed to generate report.', 'error');
                    }
                },
                error: function () {
                    Swal.close();
                    Swal.fire('Error!', 'Unexpected error during report generation. Please try again.', 'error');
                }
            });
        });
    }
});
