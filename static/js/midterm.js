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


    // Fetch Students when all filters are selected for midterm
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
                            // Default to 0 if midterm_score doesn't exist
                            var midtermScore = 0;

                            // Check if 'scores' is an array and then find midterm_score
                            if (item.scores && Array.isArray(item.scores)) {
                                item.scores.forEach(function (scoreItem) {
                                    // Check if midterm_score exists in the current score item
                                    if (scoreItem.midterm_score && scoreItem.midterm_score !== '0.00') {
                                        midtermScore = scoreItem.midterm_score;
                                    }
                                });
                            }

                            studentRows += '<tr>'
                            studentRows += '<td>' + item.student_name + '</td>'
                            studentRows += '<td><input type="number" name="midterm_score_' + item.student_id + '" value="' + midtermScore + '" class="form-control shadow-none" min="0" max="100" step="any"></td>'
                            studentRows += '<td><button type="button" class="btn btn-danger btn-sm remove-entry" data-student-id="' + item.student_id + '"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-x"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M18 6l-12 12"/><path d="M6 6l12 12" /></svg></button></td>'
                            studentRows += '</tr>'
                        })
                        $('#student-rows').html(studentRows)
                        // Show the student scores section and update the title
                        $('#student-scores-section').removeClass('d-none')
                        $('#student-scores-title').text('Student Midterm Scores for ' + data.subject_name) // Update the subject name dynamically
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
        var student_id = $(this).data('student-id')
        $(this).closest('tr').remove() // Remove the row from the table
    })

    // Handle AJAX form submission for midterm scores
    $('#midterm-scores-form').submit(function (e) {
        e.preventDefault() // Prevent regular form submission

        var formValid = true
        var formData = $(this).serializeArray() // Get all form data

        $('#students-table .form-control').each(function () {
            var input = $(this)
            var inputName = input.attr('name')
            var studentId = inputName.split('_')[2] // Extract the student ID from the name

            var midtermScore = $('[name="midterm_score_' + studentId + '"]').val()

            if (!midtermScore) {
                formValid = false
                // Highlight the fields with missing data
                $('[name="midterm_score_' + studentId + '"]').addClass('is-invalid')
                // Optionally, show an error message in each input's parent
                if (!$('.invalid-feedback').length) {
                    $('<div class="invalid-feedback">This field is required</div>').insertAfter(input)
                }
            } else {
                $('[name="midterm_score_' + studentId + '"]').removeClass('is-invalid')
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
})
