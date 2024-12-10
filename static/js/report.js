document.addEventListener('DOMContentLoaded', function () {
    const generateReportBtn = document.getElementById('generate-report-btn');

    generateReportBtn.addEventListener('click', function (e) {
        e.preventDefault();

        // Fetch the data from the report details section
        const studentName = document.getElementById('student-name').innerText;
        const classYear = document.getElementById('class-year').innerText;
        const term = document.getElementById('term').innerText;

        // Create an object with the required data for the report
        const reportData = {
            student_name: studentName,
            class_year: classYear,
            term: term,
            subjects: [],
            ca_scores: [],
            exam_scores: [],
            total_scores: [],
            grades: [],
            gpa: document.getElementById('gpa').innerText,
        };

        // Collect subject, CA, Exam, and Grade data
        const rows = document.getElementById('report-scores').children;
        Array.from(rows).forEach(row => {
            const subject = row.children[0].innerText;
            const caScore = row.children[1].innerText;
            const examScore = row.children[2].innerText;
            const totalScore = row.children[3].innerText;
            const grade = row.children[4].innerText;

            reportData.subjects.push(subject);
            reportData.ca_scores.push(caScore);
            reportData.exam_scores.push(examScore);
            reportData.total_scores.push(totalScore);
            reportData.grades.push(grade);
        });

        // AJAX request to generate the report
        fetch('/generate_report/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // CSRF token
            },
            body: JSON.stringify(reportData),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.report_url) {
                    // Open the generated report in a new tab
                    window.open(data.report_url, '_blank');
                } else {
                    // Handle error
                    alert('Error generating report. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An unexpected error occurred.');
            });
    });
});
