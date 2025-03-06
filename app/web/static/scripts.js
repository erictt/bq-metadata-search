// BigQuery Metadata Search scripts

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle search form submission
    const searchForm = document.querySelector('.search-form form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            const searchInput = searchForm.querySelector('input[name="q"]');
            if (searchInput && searchInput.value.trim() === '') {
                event.preventDefault();
                searchInput.focus();
            }
        });
    }
    
    // Handle delete confirmation modals
    const deleteDatasetModal = document.getElementById('deleteDatasetModal');
    if (deleteDatasetModal) {
        deleteDatasetModal.addEventListener('show.bs.modal', function (event) {
            // You could add additional logic here if needed
            console.log('Delete dataset modal opened');
        });
    }
    
    const deleteTableModal = document.getElementById('deleteTableModal');
    if (deleteTableModal) {
        deleteTableModal.addEventListener('show.bs.modal', function (event) {
            // You could add additional logic here if needed
            console.log('Delete table modal opened');
        });
    }
    
    // Handle project selection in advanced search
    const projectSelect = document.getElementById('project_id');
    const datasetSelect = document.getElementById('dataset_id');
    
    if (projectSelect && datasetSelect) {
        // Function to update datasets dropdown
        const updateDatasets = async (projectId) => {
            // Clear current options except the first one
            while (datasetSelect.options.length > 1) {
                datasetSelect.remove(1);
            }
            
            // If no project selected, return
            if (!projectId) {
                return;
            }
            
            try {
                // Fetch datasets for the selected project
                const response = await fetch(`/datasets?project_id=${projectId}`);
                const datasets = await response.json();
                
                console.log('Fetched datasets:', datasets);
                
                // Add options for each dataset
                datasets.forEach(dataset => {
                    console.log('Processing dataset:', dataset);
                    const option = document.createElement('option');
                    option.value = dataset.id;
                    option.textContent = dataset.id;
                    datasetSelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error fetching datasets:', error);
            }
        };
        
        // Update datasets when project changes
        projectSelect.addEventListener('change', function() {
            console.log('Project changed to:', this.value);
            updateDatasets(this.value);
        });
        
        // Initial update if a project is already selected
        if (projectSelect.value) {
            updateDatasets(projectSelect.value);
        }
    }
});
