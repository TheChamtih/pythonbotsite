// Course filtering and tag management
document.addEventListener('DOMContentLoaded', function() {
    // Course tag filtering
    const tagButtons = document.querySelectorAll('.tag-filter');
    tagButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tag = this.dataset.tag;
            const courses = document.querySelectorAll('.course-card');
            
            courses.forEach(course => {
                const courseTags = course.dataset.tags.split(',');
                if (tag === 'all' || courseTags.includes(tag)) {
                    course.style.display = 'block';
                } else {
                    course.style.display = 'none';
                }
            });
            
            // Update active state of filter buttons
            tagButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Course search
    const searchInput = document.getElementById('courseSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const courses = document.querySelectorAll('.course-card');
            
            courses.forEach(course => {
                const title = course.querySelector('.card-title').textContent.toLowerCase();
                const description = course.querySelector('.card-text').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    course.style.display = 'block';
                } else {
                    course.style.display = 'none';
                }
            });
        });
    }
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Flash message auto-hide
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 300);
        }, 3000);
    });
});
document.addEventListener('DOMContentLoaded', function() {
    var modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
    modalTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', function() {
            var target = this.getAttribute('data-bs-target');
            var modal = document.querySelector(target);
            if (modal) {
                var modalInstance = new bootstrap.Modal(modal);
                modalInstance.show();
            }
        });
    });
});