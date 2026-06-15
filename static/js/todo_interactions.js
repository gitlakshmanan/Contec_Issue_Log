// Modern To-Do List Interactive Features
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all interactive features
    initializeTaskInteractions();
    initializeSearchFeatures();
    initializeKeyboardShortcuts();
    initializeAnimations();
    
    // Task interaction features
    function initializeTaskInteractions() {
        // Add click handlers for task completion
        const taskIcons = document.querySelectorAll('.task-complete-icon, .task-incomplete-icon');
        taskIcons.forEach(icon => {
            icon.addEventListener('click', function(e) {
                e.preventDefault();
                animateTaskToggle(this);
            });
        });
        
        // Add hover effects to task wrappers
        const taskWrappers = document.querySelectorAll('.task-wrapper');
        taskWrappers.forEach(wrapper => {
            wrapper.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(5px)';
            });
            
            wrapper.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
            });
        });
    }
    
    // Search functionality enhancements
    function initializeSearchFeatures() {
        const searchInput = document.querySelector('input[name="search-area"]');
        if (searchInput) {
            // Auto-focus search input if no value
            if (!searchInput.value) {
                searchInput.focus();
            }
            
            // Clear search on double-click
            searchInput.addEventListener('dblclick', function() {
                this.value = '';
                this.form.submit();
            });
        }
    }
    
    // Keyboard shortcuts
    function initializeKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + N for new task
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                const createLink = document.querySelector('a[href*="task-create"]');
                if (createLink) {
                    window.location.href = createLink.href;
                }
            }
            
            // Escape to clear search
            if (e.key === 'Escape') {
                const searchInput = document.querySelector('input[name="search-area"]');
                if (searchInput && searchInput.value) {
                    searchInput.value = '';
                    searchInput.form.submit();
                }
            }
        });
    }
    
    // Animation enhancements
    function initializeAnimations() {
        // Animate task items on load
        const taskWrappers = document.querySelectorAll('.task-wrapper');
        taskWrappers.forEach((wrapper, index) => {
            wrapper.style.opacity = '0';
            wrapper.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                wrapper.style.transition = 'all 0.5s ease';
                wrapper.style.opacity = '1';
                wrapper.style.transform = 'translateY(0)';
            }, index * 100);
        });
        
        // Animate stats on load
        const statNumbers = document.querySelectorAll('.stat-number');
        statNumbers.forEach(stat => {
            animateNumber(stat);
        });
    }
    
    // Helper functions
    function animateTaskToggle(icon) {
        icon.style.transform = 'scale(0.8)';
        icon.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            icon.style.transform = 'scale(1.1)';
        }, 100);
        
        setTimeout(() => {
            icon.style.transform = 'scale(1)';
        }, 200);
    }
    
    function animateNumber(element) {
        const target = parseInt(element.textContent);
        const duration = 1000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    }
    
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.style.opacity = '0.7';
                submitBtn.style.pointerEvents = 'none';
            }
        });
    });
});