document.addEventListener('DOMContentLoaded', function() {
    const uploadContainer = document.querySelector('.image-upload-container');
    const uploadInput = document.getElementById('image-upload');
    const uploadPreview = document.getElementById('upload-preview');
    const uploadPrompt = document.getElementById('upload-prompt');
    const previewImage = document.getElementById('preview-image');
    const removeButton = document.getElementById('remove-image');
    const searchButton = document.getElementById('image-search-btn');
    
    if (!uploadContainer) return;
    
    // Handle click on upload area
    uploadContainer.addEventListener('click', function(e) {
        if (e.target !== removeButton && !removeButton.contains(e.target)) {
            uploadInput.click();
        }
    });
    
    // Handle drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadContainer.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadContainer.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadContainer.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        uploadContainer.classList.add('border-primary');
    }
    
    function unhighlight() {
        uploadContainer.classList.remove('border-primary');
    }
    
    uploadContainer.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length) {
            uploadInput.files = files;
            handleFiles(files);
        }
    }
    
    // Handle file selection
    uploadInput.addEventListener('change', function() {
        if (uploadInput.files.length) {
            handleFiles(uploadInput.files);
        }
    });
    
    function handleFiles(files) {
        const file = files[0];
        
        if (file && file.type.match('image.*')) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                uploadPreview.classList.remove('d-none');
                uploadPrompt.classList.add('d-none');
                searchButton.disabled = false;
            }
            
            reader.readAsDataURL(file);
        }
    }
    
    // Handle remove button
    removeButton.addEventListener('click', function(e) {
        e.stopPropagation();
        
        uploadInput.value = '';
        uploadPreview.classList.add('d-none');
        uploadPrompt.classList.remove('d-none');
        searchButton.disabled = true;
    });
});