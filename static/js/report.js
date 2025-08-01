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

                    if (selectedTerm === 'Term 3') {
                        $.ajax({
                            url: '/dashboard/get_promotion_choices/',
                            method: 'GET',
                            success: function (choicesResponse) {
                                const choices = choicesResponse.choices || [];
                                renderCommentModal(studentName, classYear, academicComment, behavioralComment, savedPromotion, selectedTerm, choices);
                            },
                            error: function () {
                                Swal.fire('Error!', 'Failed to load promotion choices.', 'error');
                            }
                        });
                    } else {
                        renderCommentModal(studentName, classYear, academicComment, behavioralComment, '', selectedTerm, []);
                    }
                },
                error: function () {
                    Swal.fire('Error!', 'Failed to fetch existing comments.', 'error');
                }
            });
        });
    });

    function renderCommentModal(studentName, classYear, academicComment, behavioralComment, savedPromotion, selectedTerm, promotionChoices) {
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

        if (selectedTerm === 'Term 3') {
            htmlContent += `
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
        }

        Swal.fire({
            title: 'Add Comments',
            html: htmlContent,
            showCancelButton: true,
            confirmButtonText: 'Submit & Generate',
            cancelButtonText: 'Cancel',
            focusConfirm: false,
            width: '600px',
            preConfirm: () => {
                const popup = Swal.getPopup();
                const academic_comment = popup.querySelector('#academic-comment').value.trim();
                const behavioral_comment = popup.querySelector('#behavioral-comment').value.trim();
                let promotion = '';

                if (selectedTerm === 'Term 3') {
                    const promotionSelect = popup.querySelector('#promotion-select');
                    if (promotionSelect) {
                        promotion = promotionSelect.value.trim();
                    }
                }

                if (!academic_comment && !behavioral_comment) {
                    Swal.showValidationMessage('At least one comment is required');
                    return false;
                }

                return { academic_comment, behavioral_comment, promotion };
            }
        }).then(result => {
            if (!result.isConfirmed) return;

            const { academic_comment, behavioral_comment, promotion } = result.value;

            Swal.fire({
                title: 'Generating Report...',
                text: 'Please wait while we generate your report.',
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => Swal.showLoading()
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
                    academic_comment,
                    behavioral_comment,
                    promotion
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
