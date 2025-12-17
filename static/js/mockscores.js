$(document).ready(function () {
    // Fetch Levels
    $.ajax({
        url: '/get-levels/', // Endpoint to get levels
        dataType: 'json',
        success: function (data) {
            var levelSelect = $('#level-select')
            data.levels.forEach(function (level) {
                levelSelect.append('<option value="' + level.id + '">' + level.name + '</option>')
            })
        }
    })

    // Fetch Class Years, Terms, and Subjects based on selected Level
    $('#level-select').change(function () {
        var level_id = $(this).val()
        // Update hidden level field
        $('#hidden-level').val(level_id)

        if (level_id) {
            // Fetch Class Years for the selected Level
            $.ajax({
                url: '/get-classes-by-level/' + level_id + '/',
                dataType: 'json',
                success: function (data) {
                    var classYearSelect = $('#class-year-select')
                    classYearSelect.prop('disabled', false) // Enable class year dropdown
                    classYearSelect.empty().append('<option value="">Select Class Year</option>')
                    data.class_years.forEach(function (year) {
                        classYearSelect.append('<option value="' + year.id + '">' + year.name + '</option>')
                    })
                    // Reset Term and Subject dropdowns
                    $('#term-select').prop('disabled', true).empty().append('<option value="">Select Term</option>')
                    $('#subject-select').prop('disabled', true).empty().append('<option value="">Select Subject</option>')
                    // Reset hidden class-year, term, subject fields
                    $('#hidden-class-year').val('')
                    $('#hidden-term').val('')
                    $('#hidden-subject').val('')
                }
            })
        } else {
            // Reset all dropdowns and hidden fields when no level is selected
            $('#class-year-select').prop('disabled', true).empty().append('<option value="">Select Class Year</option>')
            $('#term-select').prop('disabled', true).empty().append('<option value="">Select Term</option>')
            $('#subject-select').prop('disabled', true).empty().append('<option value="">Select Subject</option>')
            // Reset hidden fields
            $('#hidden-level').val('')
            $('#hidden-class-year').val('')
            $('#hidden-term').val('')
            $('#hidden-subject').val('')
        }
    })

    // Fetch Terms and Subjects when Class Year is selected
    $('#class-year-select').change(function () {
        var class_year_id = $(this).val()
        var level_id = $('#level-select').val()
        // Update hidden class-year field
        $('#hidden-class-year').val(class_year_id)

        if (class_year_id) {
            // Fetch Terms for the selected Class Year
            $.ajax({
                url: '/get-terms-by-class-year/' + class_year_id + '/',
                dataType: 'json',
                success: function (data) {
                    var termSelect = $('#term-select')
                    termSelect.prop('disabled', false) // Enable term dropdown
                    termSelect.empty().append('<option value="">Select Term</option>')
                    data.terms.forEach(function (term) {
                        termSelect.append('<option value="' + term.id + '">' + term.name + '</option>')
                    })

                    // Fetch Subjects for the selected Class Year
                    $.ajax({
                        url: '/get-subjects-by-class-year/' + class_year_id + '/',
                        dataType: 'json',
                        success: function (data) {
                            var subjectSelect = $('#subject-select')
                            subjectSelect.prop('disabled', false) // Enable subject dropdown
                            subjectSelect.empty().append('<option value="">Select Subject</option>')
                            data.subjects.forEach(function (subject) {
                                subjectSelect.append('<option value="' + subject.id + '">' + subject.name + '</option>')
                            })
                        }
                    })
                }
            })
        } else {
            $('#term-select').prop('disabled', true).empty().append('<option value="">Select Term</option>')
            $('#subject-select').prop('disabled', true).empty().append('<option value="">Select Subject</option>')
            // Reset hidden term and subject fields
            $('#hidden-term').val('')
            $('#hidden-subject').val('')
        }
    })


    // Fetch Students when all filters are selected for mockscores
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
                    var isHeadClassTeacher = data.is_head_class_teacher || false;

                    if (data.student_data.length > 0) {
                        data.student_data.forEach(function (item) {
                            // Default to 0 if mock_score doesn't exist
                            var mockScore = 0;

                            // Check if 'scores' is an array and then find mock_score
                            if (item.scores && Array.isArray(item.scores)) {
                                item.scores.forEach(function (scoreItem) {
                                    // Check if mock_score exists in the current score item
                                    if (scoreItem.mock_score && scoreItem.mock_score !== '0.00') {
                                        mockScore = scoreItem.mock_score;
                                    }
                                });
                            }

                            // Extract mock report comments
                            var academicComment = item.mock_academic_comment || '';
                            var behavioralComment = item.mock_behavioral_comment || '';
                            var hasComments = academicComment || behavioralComment;

                            studentRows += '<tr>'
                            studentRows += '<td>' + item.student_name + '</td>'
                            studentRows += '<td><input type="number" name="mock_score_' + item.student_id + '" value="' + mockScore + '" class="form-control shadow-none" min="0" max="100" step="any"></td>'

                            // Add comment button column if user is head class teacher
                            if (isHeadClassTeacher) {
                                var commentBtnClass = hasComments ? 'btn-warning' : 'btn-info';
                                var commentBtnText = hasComments ? '✓ Comments' : '+ Comments';
                                studentRows += '<td><button type="button" class="btn ' + commentBtnClass + ' btn-sm mock-comment-btn" ' +
                                    'data-student-id="' + item.student_id + '" ' +
                                    'data-academic-comment="' + (academicComment || '') + '" ' +
                                    'data-behavioral-comment="' + (behavioralComment || '') + '">' +
                                    commentBtnText + '</button></td>';
                            }

                            studentRows += '<td><button type="button" class="btn btn-danger btn-sm remove-entry" data-student-id="' + item.student_id + '"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-x"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M18 6l-12 12"/><path d="M6 6l12 12" /></svg></button></td>'
                            studentRows += '</tr>'
                        })
                        $('#student-rows').html(studentRows)
                        // Show the student scores section and update the title
                        $('#student-scores-section').removeClass('d-none')
                        $('#student-scores-title').text('Student Mock  Scores for ' + data.subject_name) // Update the subject name dynamically
                    } else {
                        var colspanCount = isHeadClassTeacher ? 4 : 3;
                        $('#student-rows').html('<tr><td colspan="' + colspanCount + '">No students found for the selected filters.</td></tr>')
                        $('#student-scores-section').removeClass('d-none') // Show the section even if no students are found
                    }
                }
            })
        }
    })


    // Handle formset deletion
    $(document).on('click', '.remove-entry', function () {
        var student_id = $(this).data('student-id')
        $(this).closest('tr').remove() // Remove the row from the table
    })

    // Handle AJAX form submission for mock scores
    $('#mock-scores-form').submit(function (e) {
        e.preventDefault() // Prevent regular form submission

        var formValid = true
        var formData = $(this).serializeArray() // Get all form data

        $('#students-table .form-control').each(function () {
            var input = $(this)
            var inputName = input.attr('name')
            var studentId = inputName.split('_')[2] // Extract the student ID from the name

            var mockScore = $('[name="mock_score_' + studentId + '"]').val()

            if (!mockScore) {
                formValid = false
                // Highlight the fields with missing data
                $('[name="mock_score_' + studentId + '"]').addClass('is-invalid')
                // Optionally, show an error message in each input's parent
                if (!$('.invalid-feedback').length) {
                    $('<div class="invalid-feedback">This field is required</div>').insertAfter(input)
                }
            } else {
                $('[name="mock_score_' + studentId + '"]').removeClass('is-invalid')
                $(input).siblings('.invalid-feedback').remove()
            }
        })

        if (formValid) {
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
                            resetFormFields()
                        })
                    } else {
                        Swal.fire({
                            title: 'Error!',
                            text: response.message,
                            icon: 'error',
                            confirmButtonText: 'OK'
                        })
                    }
                },
                error: function () {
                    Swal.fire({
                        title: 'Error!',
                        text: 'An unexpected error occurred. Please try again.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    })
                }
            })
        }
    })


    // Event listener for when the "View" button is clicked
    $('#mockScoresModal').on('click', '.btn-info', function (event) {
        event.preventDefault(); // Prevent the default link behavior

        // Get the student ID and term ID from the data attributes
        var studentId = $(this).data('student-id');
        var termId = $(this).data('term-id');

        // Check if studentId and termId are defined
        if (studentId && termId) {
            // Perform the AJAX request to fetch the report details
            $.ajax({
                url: `/reports/get_mock_report_details/${studentId}/${termId}/`, // Dynamic path with student_id and term_id
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
                  <td>${score.mock_score}</td>
                  <td>${score.grade}</td>
                  <td>${score.gpa}</td>
                </tr>
              `;
                            $('#report-scores').append(scoreRow);
                        });

                        // Set the GPA
                        $('#gpa').text(response.total_gpa);

                        // Optionally, hide the modal
                        $('#mockScoresModal').modal('hide');
                    } else {
                        alert('Report not found');
                    }
                },
                error: function () {
                    alert('Error fetching report details');
                }
            });
        } else {
            console.error('Student ID or Term ID is missing.');
        }
    });







    // Reset form fields after successful form submission
    function resetFormFields() {
        $('#hidden-level').val('')
        $('#hidden-class-year').val('')
        $('#hidden-term').val('')
        $('#hidden-subject').val('')
        $('#student-rows').html('')
        $('#student-scores-section').addClass('d-none')
        $('#student-scores-title').text('Student Scores')
        $('.form-control').removeClass('is-invalid')
        $('.invalid-feedback').remove()
    }


    // ========== MOCK REPORT COMMENTS FUNCTIONALITY ==========

    // Handle comment button click
    $(document).on('click', '.mock-comment-btn', function() {
        var studentId = $(this).data('student-id');
        var academicComment = $(this).data('academic-comment');
        var behavioralComment = $(this).data('behavioral-comment');

        // Populate modal with existing comments
        $('#mock-comment-student-id').val(studentId);
        $('#mock-academic-comment-input').val(academicComment);
        $('#mock-behavioral-comment-input').val(behavioralComment);

        // Show delete button if comments exist
        if (academicComment || behavioralComment) {
            $('#mock-delete-comment-btn').show();
        } else {
            $('#mock-delete-comment-btn').hide();
        }

        // Show modal
        $('#mockCommentModal').modal('show');
    });

    // Handle save comments
    $('#mock-save-comment-btn').click(function() {
        var studentId = $('#mock-comment-student-id').val();
        var academicComment = $('#mock-academic-comment-input').val();
        var behavioralComment = $('#mock-behavioral-comment-input').val();

        // Get current filter values
        var termId = $('#term-select').val();
        var classYearId = $('#class-year-select').val();
        var levelId = $('#level-select').val();
        var subjectId = $('#subject-select').val();

        // Save comments via AJAX
        var formData = new FormData();
        formData.append('level', levelId);
        formData.append('class_year', classYearId);
        formData.append('term', termId);
        formData.append('subject', subjectId);
        formData.append('mock_academic_comment_' + studentId, academicComment);
        formData.append('mock_behavioral_comment_' + studentId, behavioralComment);
        formData.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());

        $.ajax({
            type: 'POST',
            url: '/dashboard/entries/mock-scores/',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                // Update button appearance
                var commentBtn = $('[data-student-id="' + studentId + '"].mock-comment-btn');
                commentBtn.data('academic-comment', academicComment);
                commentBtn.data('behavioral-comment', behavioralComment);
                commentBtn.attr('data-academic-comment', academicComment);
                commentBtn.attr('data-behavioral-comment', behavioralComment);
                commentBtn.removeClass('btn-info').addClass('btn-warning');
                commentBtn.html('✓ Comments');

                // Close modal
                $('#mockCommentModal').modal('hide');

                Swal.fire({
                    title: 'Success!',
                    text: 'Mock report comments saved successfully!',
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

    // Handle delete comments
    $('#mock-delete-comment-btn').click(function() {
        Swal.fire({
            title: 'Are you sure?',
            text: 'Do you want to delete these comments?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                var studentId = $('#mock-comment-student-id').val();

                // Get current filter values
                var termId = $('#term-select').val();
                var classYearId = $('#class-year-select').val();
                var levelId = $('#level-select').val();
                var subjectId = $('#subject-select').val();

                // Delete comments via AJAX
                var formData = new FormData();
                formData.append('level', levelId);
                formData.append('class_year', classYearId);
                formData.append('term', termId);
                formData.append('subject', subjectId);
                formData.append('mock_academic_comment_' + studentId, '');
                formData.append('mock_behavioral_comment_' + studentId, '');
                formData.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());

                $.ajax({
                    type: 'POST',
                    url: '/dashboard/entries/mock-scores/',
                    data: formData,
                    processData: false,
                    contentType: false,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    success: function(response) {
                        // Clear comments from button
                        var commentBtn = $('[data-student-id="' + studentId + '"].mock-comment-btn');
                        commentBtn.data('academic-comment', '');
                        commentBtn.data('behavioral-comment', '');
                        commentBtn.attr('data-academic-comment', '');
                        commentBtn.attr('data-behavioral-comment', '');

                        // Update button appearance
                        commentBtn.removeClass('btn-warning').addClass('btn-info');
                        commentBtn.html('+ Comments');

                        // Clear modal inputs
                        $('#mock-academic-comment-input').val('');
                        $('#mock-behavioral-comment-input').val('');

                        // Close modal
                        $('#mockCommentModal').modal('hide');

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

    // ========== STUDENT SEARCH FUNCTIONALITY ==========

    // Search functionality for student list
    $('#student-search-input').on('keyup', function() {
        var searchTerm = $(this).val().toLowerCase()

        $('#students-table tbody tr').each(function() {
            var studentName = $(this).find('td:first').text().toLowerCase()

            if (studentName.indexOf(searchTerm) === -1) {
                $(this).hide()
            } else {
                $(this).show()
            }
        })
    })
})
