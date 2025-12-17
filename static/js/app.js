$(document).ready(function () {
    // Fetch Levels
    $.ajax({
        url: '/get-levels/', // Endpoint to get levels
        dataType: 'json',
        success: function (data) {
            var levelSelect = $('#level-select');
            data.levels.forEach(function (level) {
                levelSelect.append('<option value="' + level.id + '">' + level.name + '</option>');
            });
        }
    });

    // Fetch Class Years, Terms, and Subjects based on selected Level
    $('#level-select').change(function () {
        var level_id = $(this).val();
        // Update hidden level field
        $('#hidden-level').val(level_id);

        if (level_id) {
            // Fetch Class Years for the selected Level
            $.ajax({
                url: '/get-classes-by-level/' + level_id + '/',
                dataType: 'json',
                success: function (data) {
                    var classYearSelect = $('#class-year-select');
                    classYearSelect.prop('disabled', false); // Enable class year dropdown
                    classYearSelect.empty().append('<option value="">Select Class Year</option>');
                    data.class_years.forEach(function (year) {
                        classYearSelect.append('<option value="' + year.id + '">' + year.name + '</option>');
                    });
                    // Reset Term and Subject dropdowns
                    $('#term-select').prop('disabled', true).empty().append('<option value="">Select Term</option>');
                    $('#subject-select').prop('disabled', true).empty().append('<option value="">Select Subject</option>');
                    // Reset hidden class-year, term, subject fields
                    $('#hidden-class-year').val('');
                    $('#hidden-term').val('');
                    $('#hidden-subject').val('');
                }
            });
        } else {
            // Reset all dropdowns and hidden fields when no level is selected
            $('#class-year-select').prop('disabled', true).empty().append('<option value="">Select Class Year</option>');
            $('#term-select').prop('disabled', true).empty().append('<option value="">Select Term</option>');
            $('#subject-select').prop('disabled', true).empty().append('<option value="">Select Subject</option>');
            // Reset hidden fields
            $('#hidden-level').val('');
            $('#hidden-class-year').val('');
            $('#hidden-term').val('');
            $('#hidden-subject').val('');
        }
    });

    // Fetch Terms and Subjects when Class Year is selected
    $('#class-year-select').change(function () {
        var class_year_id = $(this).val();
        var level_id = $('#level-select').val();
        // Update hidden class-year field
        $('#hidden-class-year').val(class_year_id);

        if (class_year_id) {
            // Fetch Terms for the selected Class Year
            $.ajax({
                url: '/get-terms-by-class-year/' + class_year_id + '/',
                dataType: 'json',
                success: function (data) {
                    var termSelect = $('#term-select');
                    termSelect.prop('disabled', false); // Enable term dropdown
                    termSelect.empty().append('<option value="">Select Term</option>');
                    data.terms.forEach(function (term) {
                        termSelect.append('<option value="' + term.id + '">' + term.name + '</option>');
                    });

                    // Fetch Subjects for the selected Class Year
                    $.ajax({
                        url: '/get-subjects-by-class-year/' + class_year_id + '/',
                        dataType: 'json',
                        success: function (data) {
                            var subjectSelect = $('#subject-select');
                            subjectSelect.prop('disabled', false); // Enable subject dropdown
                            subjectSelect.empty().append('<option value="">Select Subject</option>');
                            data.subjects.forEach(function (subject) {
                                subjectSelect.append('<option value="' + subject.id + '">' + subject.name + '</option>');
                            });
                        }
                    });
                }
            });
        } else {
            $('#term-select').prop('disabled', true).empty().append('<option value="">Select Term</option>');
            $('#subject-select').prop('disabled', true).empty().append('<option value="">Select Subject</option>');
            // Reset hidden term and subject fields
            $('#hidden-term').val('');
            $('#hidden-subject').val('');
        }
    });



    // Fetch Students when all filters are selected
    $('#term-select, #subject-select').change(function () {
        var level_id = $('#level-select').val()
        var class_year_id = $('#class-year-select').val()
        var term_id = $('#term-select').val()
        var subject_id = $('#subject-select').val()

        // Update hidden fields
        $('#hidden-term').val(term_id)
        $('#hidden-subject').val(subject_id)

        if (level_id && class_year_id && term_id && subject_id) {
            $.ajax({
                url: '/get-students-by-filters/' + level_id + '/' + class_year_id + '/' + term_id + '/' + subject_id + '/',
                dataType: 'json',
                success: function (data) {
                    var studentRows = ''
                    if (data.student_data.length > 0) {
                        data.student_data.forEach(function (item) {
                            // Log the item data to inspect
                            console.log('Student Data:', item);

                            // Extract continuous assessment and exam score
                            var continuousAssessment = (item.scores && item.scores[0] && item.scores[0].continuous_assessment !== undefined) ? parseFloat(item.scores[0].continuous_assessment) : 0.0;
                            var examScore = (item.scores && item.scores[0] && item.scores[0].exam_score !== undefined) ? parseFloat(item.scores[0].exam_score) : 0.0;

                            // Calculate 70% of exam score for display
                            var examScoreDisplay = examScore * 0.70;

                            console.log('Continuous Assessment:', continuousAssessment);  // Check the value
                            console.log('Exam Score (original):', examScore);  // Check the value
                            console.log('Exam Score (70% for display):', examScoreDisplay);  // Check the value

                            studentRows += '<tr>';
                            studentRows += '<td>' + item.student_name + '</td>';

                            // Display continuous assessment as a disabled input field (view-only)
                            studentRows += '<td><input type="number" value="' + continuousAssessment.toFixed(2) + '" class="form-control" min="0" step="any" disabled></td>';

                            // Display exam score: show 70% for display, but allow entering full score
                            studentRows += '<td>';
                            studentRows += '<div class="input-group">';
                            studentRows += '<input type="number" name="exam_score_' + item.student_id + '" value="' + examScore.toFixed(2) + '" class="form-control" min="0" max="100" step="any" title="Enter full exam score (system will calculate 70%)">';
                            studentRows += '<span class="input-group-text" title="Displayed as 70%">→ ' + examScoreDisplay.toFixed(2) + '</span>';
                            studentRows += '</div>';
                            studentRows += '</td>';

                            // Extract student-level comments (not tied to specific subject)
                            var academicComment = item.academic_comment || '';
                            var behavioralComment = item.behavioral_comment || '';
                            var hasComments = academicComment || behavioralComment;

                            // Debug: Log to see what we're getting
                            if (item.student_name === 'Tamar Williams' || item.student_name === 'Kirk Tamakloe') {
                                console.log('DEBUG Student:', item.student_name);
                                console.log('  academic_comment:', item.academic_comment);
                                console.log('  behavioral_comment:', item.behavioral_comment);
                                console.log('  hasComments:', hasComments);
                            }

                            // Check if user is head class teacher
                            var isHeadTeacher = $('#is-head-class-teacher').val() === 'True';

                            studentRows += '<td>';

                            // Add comment button for head teachers
                            if (isHeadTeacher) {
                                var commentBtnClass = hasComments ? 'btn-warning' : 'btn-info';
                                var commentBtnIcon = hasComments ? '✓' : '+';
                                studentRows += '<button type="button" class="btn ' + commentBtnClass + ' btn-sm me-1 add-comment-btn" ';
                                studentRows += 'data-student-id="' + item.student_id + '" ';
                                studentRows += 'data-student-name="' + item.student_name + '" ';
                                studentRows += 'data-academic-comment="' + academicComment.replace(/"/g, '&quot;') + '" ';
                                studentRows += 'data-behavioral-comment="' + behavioralComment.replace(/"/g, '&quot;') + '" ';
                                studentRows += 'title="' + (hasComments ? 'Edit comments' : 'Add comments') + '">';
                                studentRows += commentBtnIcon + ' Comments</button>';
                            }

                            studentRows += '<button type="button" class="btn btn-danger btn-sm remove-entry" data-student-id="' + item.student_id + '"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-x"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M18 6l-12 12"/><path d="M6 6l12 12" /></svg></button>';
                            studentRows += '</td>';
                            studentRows += '</tr>';
                        });

                        $('#student-rows').html(studentRows)
                        // Show the student scores section and update the title
                        $('#student-scores-section').removeClass('d-none')
                        $('#student-scores-title').text('Student Scores for ' + data.subject_name) // Update the subject name dynamically

                    } else {
                        $('#student-rows').html('<tr><td colspan="4">No students found for the selected filters.</td></tr>')
                        $('#student-scores-section').removeClass('d-none') // Show the section even if no students are found
                    }
                }
            })
        }
    })



    // Handle formset deletion
    $(document).on('click', '.remove-entry', function () {
        var student_id = $(this).data('student-id');
        $(this).closest('tr').remove(); // Remove the row from the table
    });

    // Handle AJAX form submission
    $('#exam-scores-form').submit(function (e) {
        e.preventDefault(); // Prevent regular form submission

        var formValid = true;
        var formData = $(this).serializeArray(); // Get all form data

        $('#students-table .form-control').each(function () {
            var input = $(this);
            var inputName = input.attr('name');

            // Ensure inputName exists and follows the expected format
            if (inputName && inputName.split('_').length > 2) {
                var studentId = inputName.split('_')[2]; // Extract the student ID from the name

                var examScore = $('[name="exam_score_' + studentId + '"]').val();

                // Validate only exam scores
                if (!examScore) {
                    formValid = false;
                    // Highlight the fields with missing data
                    $('[name="exam_score_' + studentId + '"]').addClass('is-invalid');
                    // Optionally, show an error message in each input's parent
                    if (!$('.invalid-feedback').length) {
                        $('<div class="invalid-feedback">This field is required</div>').insertAfter(input);
                    }
                } else {
                    $('[name="exam_score_' + studentId + '"]').removeClass('is-invalid');
                    $(input).siblings('.invalid-feedback').remove();
                }
            } else {
                console.error('Invalid input name:', inputName);  // Log error for inspection
            }
        });

        if (formValid) {
            // Add comments to form data
            $('.add-comment-btn').each(function() {
                var studentId = $(this).data('student-id');
                var academicComment = $(this).data('academic-comment') || '';
                var behavioralComment = $(this).data('behavioral-comment') || '';

                if (academicComment) {
                    formData.push({name: 'academic_comment_' + studentId, value: academicComment});
                }
                if (behavioralComment) {
                    formData.push({name: 'behavioral_comment_' + studentId, value: behavioralComment});
                }
            });

            $.ajax({
                url: '', // The URL to handle the POST request in the view
                type: 'POST',
                data: formData,
                success: function (response) {
                    if (response.status === 'success') {
                        Swal.fire({
                            title: 'Success!',
                            text: response.message,
                            icon: 'success',
                            confirmButtonText: 'OK'
                        }).then(() => {
                            // Reset form fields after successful submission
                            resetFormFields();
                        });
                    } else {
                        Swal.fire({
                            title: 'Error!',
                            text: response.message,
                            icon: 'error',
                            confirmButtonText: 'OK'
                        });
                    }
                },
                error: function () {
                    Swal.fire({
                        title: 'Error!',
                        text: 'An unexpected error occurred. Please try again.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                }
            });
        }
    });




    // Event listener for when the "View" button is clicked
    $('#scoresModal').on('click', '.btn-info', function (event) {
        event.preventDefault(); // Prevent the default link behavior

        // Get the student ID and term ID from the data attributes
        var studentId = $(this).data('student-id');
        var termId = $(this).data('term-id');

        // Check if studentId and termId are defined
        if (studentId && termId) {
            // Perform the AJAX request to fetch the report details
            $.ajax({
                url: `/reports/get_report_details/${studentId}/${termId}/`,  // Dynamic path with student_id and term_id
                method: 'GET',
                success: function (response) {
                    if (response) {
                        // Only populate the report section
                        $('#student-scores-section').addClass('d-none'); // Ensure the student scores section remains hidden

                        // Set the report details in the report section
                        $('#student-name').text(response.student_name);
                        $('#class-year').text(response.class_year);
                        $('#term').text(response.term);

                        // Clear previous scores and append new ones
                        $('#report-scores').empty();
                        response.scores.forEach(function (score) {
                            var scoreRow = `
                <tr>
                  <td>${score.subject}</td>
                  <td>${score.ca}</td>
                  <td>${score.exam}</td>
                  <td>${score.total}</td>
                  <td>${score.grade}</td>
                </tr>
              `;
                            $('#report-scores').append(scoreRow);
                        });

                        // Set the GPA
                        $('#gpa').text(response.gpa);

                        // Optionally, hide the modal
                        $('#scoresModal').modal('hide');
                    } else {
                        alert('Report not found');
                    }
                },
                error: function () {
                    alert('Error fetching report details');
                }
            });
        } else {
            console.error("Student ID or Term ID is missing.");
        }
    });

    // Handle Delete button click
    $('#scoresModal').on('click', '.delete-score-btn', function () {
        var scoreId = $(this).data('score-id'); // Get the score ID from the button's data attribute
        Swal.fire({
            title: 'Are you sure?',
            text: 'This will permanently delete this score.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'No, cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                // Perform the AJAX request to delete the score
                $.ajax({
                    url: `/reports/scores/delete-score/${scoreId}/`, // Correct endpoint URL
                    method: 'DELETE',
                    headers: { 'X-CSRFToken': getCSRFToken() }, // Pass CSRF token
                    success: function (response) {
                        if (response.status === 'success') {
                            Swal.fire({
                                title: 'Deleted!',
                                text: 'The score has been successfully deleted.',
                                icon: 'success',
                                confirmButtonText: 'OK'
                            });

                            // Remove the corresponding row from the UI
                            $('button.delete-score-btn')
                                .filter(function () {
                                    return $(this).data('score-id') === scoreId;
                                })
                                .closest('tr')
                                .remove();
                        } else {
                            Swal.fire({
                                title: 'Error!',
                                text: response.message,
                                icon: 'error',
                                confirmButtonText: 'OK'
                            });
                        }
                    },
                    error: function () {
                        Swal.fire({
                            title: 'Error!',
                            text: 'An unexpected error occurred.',
                            icon: 'error',
                            confirmButtonText: 'OK'
                        });
                    }
                });
            }
        });
    });



    // Reset form fields after successful form submission
    function resetFormFields() {
        $('#hidden-level').val('');
        $('#hidden-class-year').val('');
        $('#hidden-term').val('');
        $('#hidden-subject').val('');
        $('#student-rows').html('');
        $('#student-scores-section').addClass('d-none');
        $('#student-scores-title').text('Student Scores');
        $('.form-control').removeClass('is-invalid');
        $('.invalid-feedback').remove();
    }


    // ========== STUDENT SEARCH FUNCTIONALITY ==========

    // Search functionality for student list in formset
    $('#student-search-input').on('keyup', function() {
        var searchTerm = $(this).val().toLowerCase();

        $('#students-table tbody tr').each(function() {
            var studentName = $(this).find('td:first').text().toLowerCase();

            if (studentName.indexOf(searchTerm) === -1) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    });

    // Search functionality for student list in modal
    $('#modal-student-search-input').on('keyup', function() {
        var searchTerm = $(this).val().toLowerCase();

        $('#student-score-rows tr').each(function() {
            var studentName = $(this).find('td:first').text().toLowerCase();

            if (studentName.indexOf(searchTerm) === -1) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    });


    // ========== COMMENT MODAL HANDLERS ==========

    // Open comment modal when comment button is clicked
    $(document).on('click', '.add-comment-btn', function() {
        var studentId = $(this).data('student-id');
        var studentName = $(this).data('student-name');
        var academicComment = $(this).data('academic-comment') || '';
        var behavioralComment = $(this).data('behavioral-comment') || '';

        // Set modal data
        $('#comment-student-id').val(studentId);
        $('#comment-student-name').text(studentName);
        $('#academic-comment-input').val(academicComment);
        $('#behavioral-comment-input').val(behavioralComment);

        // Show/hide elements based on whether comments exist
        if (academicComment || behavioralComment) {
            $('#comment-exists-warning').removeClass('d-none');
            $('#delete-comment-btn').removeClass('d-none');
        } else {
            $('#comment-exists-warning').addClass('d-none');
            $('#delete-comment-btn').addClass('d-none');
        }

        // Show modal
        $('#studentCommentModal').modal('show');
    });

    // Save comments
    $('#save-comment-btn').click(function() {
        var studentId = $('#comment-student-id').val();
        var academicComment = $('#academic-comment-input').val().trim();
        var behavioralComment = $('#behavioral-comment-input').val().trim();

        // Validate at least one comment is provided
        if (!academicComment && !behavioralComment) {
            Swal.fire({
                title: 'Warning!',
                text: 'Please provide at least one comment (academic or behavioral).',
                icon: 'warning',
                confirmButtonText: 'OK'
            });
            return;
        }

        // Get current filter values to save comments to backend immediately
        var termId = $('#term-select').val();
        var classYearId = $('#class-year-select').val();
        var levelId = $('#level-select').val();
        var subjectId = $('#subject-select').val();

        // Save comments immediately to backend
        var formData = new FormData();
        formData.append('level', levelId);
        formData.append('class_year', classYearId);
        formData.append('term', termId);
        formData.append('subject', subjectId);
        formData.append('academic_comment_' + studentId, academicComment);
        formData.append('behavioral_comment_' + studentId, behavioralComment);
        formData.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());

        $.ajax({
            type: 'POST',
            url: '/dashboard/process_scores/',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                // Update button appearance
                var commentBtn = $('[data-student-id="' + studentId + '"].add-comment-btn');
                commentBtn.data('academic-comment', academicComment);
                commentBtn.data('behavioral-comment', behavioralComment);
                commentBtn.attr('data-academic-comment', academicComment);
                commentBtn.attr('data-behavioral-comment', behavioralComment);
                commentBtn.removeClass('btn-info').addClass('btn-warning');
                commentBtn.html('✓ Comments');
                commentBtn.attr('title', 'Edit comments');

                // Close modal
                $('#studentCommentModal').modal('hide');

                Swal.fire({
                    title: 'Success!',
                    text: 'Comments saved successfully!',
                    icon: 'success',
                    timer: 2000,
                    showConfirmButton: false
                });
            },
            error: function() {
                Swal.fire({
                    title: 'Error!',
                    text: 'Failed to save comments. Please try again.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        });
    });

    // Delete comments
    $('#delete-comment-btn').click(function() {
        Swal.fire({
            title: 'Are you sure?',
            text: 'This will delete both academic and behavioral comments for this student.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, delete',
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                var studentId = $('#comment-student-id').val();

                // Get current filter values to delete comments from backend
                var termId = $('#term-select').val();
                var classYearId = $('#class-year-select').val();
                var levelId = $('#level-select').val();
                var subjectId = $('#subject-select').val();

                // Delete comments from backend
                var formData = new FormData();
                formData.append('level', levelId);
                formData.append('class_year', classYearId);
                formData.append('term', termId);
                formData.append('subject', subjectId);
                formData.append('academic_comment_' + studentId, '');
                formData.append('behavioral_comment_' + studentId, '');
                formData.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());

                $.ajax({
                    type: 'POST',
                    url: '/dashboard/process_scores/',
                    data: formData,
                    processData: false,
                    contentType: false,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    success: function(response) {
                        // Clear comments from button
                        var commentBtn = $('[data-student-id="' + studentId + '"].add-comment-btn');
                        commentBtn.data('academic-comment', '');
                        commentBtn.data('behavioral-comment', '');
                        commentBtn.attr('data-academic-comment', '');
                        commentBtn.attr('data-behavioral-comment', '');

                        // Update button appearance
                        commentBtn.removeClass('btn-warning').addClass('btn-info');
                        commentBtn.html('+ Comments');
                        commentBtn.attr('title', 'Add comments');

                        // Clear modal inputs
                        $('#academic-comment-input').val('');
                        $('#behavioral-comment-input').val('');

                        // Close modal
                        $('#studentCommentModal').modal('hide');

                        Swal.fire({
                            title: 'Deleted!',
                            text: 'Comments deleted successfully!',
                            icon: 'success',
                            timer: 2000,
                            showConfirmButton: false
                        });
                    },
                    error: function() {
                        Swal.fire({
                            title: 'Error!',
                            text: 'Failed to delete comments. Please try again.',
                            icon: 'error',
                            confirmButtonText: 'OK'
                        });
                    }
                });
            }
        });
    });


});
