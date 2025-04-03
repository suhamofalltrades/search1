// This file contains JavaScript for the search page (index.html)

document.addEventListener('DOMContentLoaded', function() {
    // Get the search form and input
    const searchForm = document.querySelector('form');
    const searchInput = document.querySelector('input[name="q"]');
    
    // Create a suggestions container
    let suggestionsContainer = document.createElement('div');
    suggestionsContainer.classList.add('suggestions-container');
    searchForm.appendChild(suggestionsContainer);
    
    // Focus the search input when the page loads
    if (searchInput) {
        searchInput.focus();
        
        // Add event listener for search suggestions
        let debounceTimer;
        searchInput.addEventListener('input', function() {
            // Clear any previous timers
            clearTimeout(debounceTimer);
            
            const query = searchInput.value.trim();
            
            // Clear suggestions if query is too short
            if (query.length < 2) {
                suggestionsContainer.innerHTML = '';
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            // Debounce the suggestions request (300ms)
            debounceTimer = setTimeout(() => {
                // Make the API call for suggestions
                fetch(`/api/search-suggestions?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(suggestions => {
                        suggestionsContainer.innerHTML = '';
                        
                        if (suggestions.length > 0) {
                            suggestionsContainer.style.display = 'block';
                            
                            // Create suggestion items
                            suggestions.forEach(suggestion => {
                                const suggestionItem = document.createElement('div');
                                suggestionItem.classList.add('suggestion-item');
                                suggestionItem.textContent = suggestion;
                                
                                // Handle suggestion selection
                                suggestionItem.addEventListener('click', function() {
                                    searchInput.value = suggestion;
                                    suggestionsContainer.innerHTML = '';
                                    suggestionsContainer.style.display = 'none';
                                    searchForm.submit();
                                });
                                
                                suggestionsContainer.appendChild(suggestionItem);
                            });
                        } else {
                            suggestionsContainer.style.display = 'none';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching suggestions:', error);
                        suggestionsContainer.style.display = 'none';
                    });
            }, 300);
        });
        
        // Hide suggestions when clicking elsewhere
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
                suggestionsContainer.innerHTML = '';
                suggestionsContainer.style.display = 'none';
            }
        });
    }
    
    // Handle form submission
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            // Prevent submission if the query is empty
            if (!searchInput.value.trim()) {
                e.preventDefault();
                return false;
            }
            
            // Hide suggestions on form submit
            suggestionsContainer.innerHTML = '';
            suggestionsContainer.style.display = 'none';
            
            // Continue with normal form submission
            return true;
        });
    }
    
    // Toggle all checkboxes functionality
    const toggleAllBtn = document.getElementById('toggle-all-engines');
    if (toggleAllBtn) {
        toggleAllBtn.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('input[name="engines"]');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = !allChecked;
            });
        });
    }
});
