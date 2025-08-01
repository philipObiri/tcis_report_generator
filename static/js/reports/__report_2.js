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
                            <textarea id="academic-comment" class="swal2-textarea" style="width:100%;">${academicComment}</textarea>
                        </div>
                        <div style="margin-bottom: 15px; text-align: left;">
                            <label for="behavioral-comment" style="font-weight:600;">Behavioral Comment</label>
                            <textarea id="behavioral-comment" class="swal2-textarea" style="width:100%;">${behavioralComment}</textarea>
                        </div>
                    `;

                    if (selectedTerm === 'Term 3') {
                        htmlContent += `
                            <div style="margin-top:10px; text-align:left;">
                                <label for="promotion-select" style="font-weight:600;">Promoted to:</label>
                                <select id="promotion-select" class="swal2-select" style="width:100%;">
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
                        focusConfirm: false,
                        didOpen: () => {
                            if (selectedTerm === 'Term 3') {
                                $('#promotion-select').val(savedPromotion);
                            }
                        },

                        preConfirm: () => {
                            const academic_comment = $('#academic-comment').val().trim();
                            const behavioral_comment = $('#behavioral-comment').val().trim();

                            // let promotion = '';

                            const promotion = $('#promotion-select').val().trim();

                            // Only fetch promotion if Term 3
                            // if ($('#term-dropdown').val() === 'Term 3') {
                            //     promotion = $('#promotion-select').val().trim();
                            // }

                            return { academic_comment, behavioral_comment, promotion };
                        }

                    }).then(result => {
                        if (!result.isConfirmed) return;
                        const { academic_comment, behavioral_comment, promotion } = result.value;
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
                                if (data.success && data.report_html) {
                                    const newTab = window.open('', '_blank');
                                    newTab.document.write('<html><head><title>Academic Report</title></head><body>');
                                    newTab.document.write(data.report_html);
                                    newTab.document.write('</body></html>');
                                } else {
                                    Swal.fire('Error!', data.error || 'Failed to generate report.', 'error');
                                }
                            },
                            error: function () {
                                Swal.fire('Error!', 'Unexpected error during report generation.', 'error');
                            }
                        });
                    });
                },
                error: function () {
                    Swal.fire('Error!', 'Failed to fetch existing comments.', 'error');
                }
            });
        });
    });
});
