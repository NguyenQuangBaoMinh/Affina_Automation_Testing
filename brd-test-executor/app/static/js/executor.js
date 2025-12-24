/**
 * BRD Test Executor - Phase 2
 * Frontend JavaScript
 */

// Global state
let worksheets = [];
let selectedWorksheet = null;
let executionId = null;

// DOM Elements
const worksheetSelect = document.getElementById('worksheetSelect');
const testCountSpan = document.getElementById('testCount');
const browserSelect = document.getElementById('browserSelect');
const headlessCheck = document.getElementById('headlessCheck');
const runTestsBtn = document.getElementById('runTestsBtn');
const sheetNameSpan = document.getElementById('sheetName');
const sheetUrlLink = document.getElementById('sheetUrl');

const executionSection = document.getElementById('executionSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');

const execStatus = document.getElementById('execStatus');
const execId = document.getElementById('execId');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const passedCount = document.getElementById('passedCount');
const failedCount = document.getElementById('failedCount');
const pendingCount = document.getElementById('pendingCount');
const currentTest = document.getElementById('currentTest');
const viewResultsBtn = document.getElementById('viewResultsBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 BRD Test Executor initialized');
    loadConfig();
    loadWorksheets();
    setupEventListeners();
});

/**
 * Load application config
 */
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        
        if (data.success) {
            console.log('✓ Config loaded:', data.config);
            
            // Set browser default
            browserSelect.value = data.config.browser || 'chromium';
            headlessCheck.checked = data.config.headless || false;
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

/**
 * Load worksheets from API
 */
async function loadWorksheets() {
    try {
        console.log('📋 Loading worksheets...');
        
        const response = await fetch('/api/worksheets');
        const data = await response.json();
        
        if (!data.success) {
            showError(data.error || 'Failed to load worksheets');
            return;
        }
        
        worksheets = data.worksheets;
        
        console.log(`✓ Loaded ${worksheets.length} worksheets`);
        
        // Update sheet info
        sheetNameSpan.textContent = data.sheet_name;
        sheetUrlLink.href = data.sheet_url;
        
        // Populate dropdown
        populateWorksheetDropdown();
        
    } catch (error) {
        console.error('Error loading worksheets:', error);
        showError('Failed to connect to server. Please make sure the server is running.');
    }
}

/**
 * Populate worksheet dropdown
 */
function populateWorksheetDropdown() {
    // Clear existing options
    worksheetSelect.innerHTML = '<option value="">-- Select a worksheet --</option>';
    
    // Add worksheet options
    worksheets.forEach((ws, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${ws.name} (${ws.test_count} tests)`;
        worksheetSelect.appendChild(option);
    });
    
    console.log(`✓ Dropdown populated with ${worksheets.length} worksheets`);
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Worksheet selection change
    worksheetSelect.addEventListener('change', (e) => {
        const index = e.target.value;
        
        if (index === '') {
            selectedWorksheet = null;
            testCountSpan.textContent = '0 test cases';
            runTestsBtn.disabled = true;
        } else {
            selectedWorksheet = worksheets[index];
            testCountSpan.textContent = `${selectedWorksheet.test_count} test cases`;
            runTestsBtn.disabled = false;
            
            console.log('✓ Selected worksheet:', selectedWorksheet.name);
        }
    });
    
    // Run tests button
    runTestsBtn.addEventListener('click', runTests);
}

/**
 * Run tests
 */
async function runTests() {
    if (!selectedWorksheet) {
        alert('Please select a worksheet first');
        return;
    }
    
    console.log('🚀 Starting test execution...');
    
    // Hide error section
    errorSection.style.display = 'none';
    
    // Show execution section
    executionSection.style.display = 'block';
    
    // Reset progress
    updateProgress(0, selectedWorksheet.test_count, 0, 0);
    execStatus.textContent = 'Starting...';
    execStatus.className = 'status-badge status-running';
    currentTest.textContent = 'Initializing...';
    
    // Disable run button
    runTestsBtn.disabled = true;
    runTestsBtn.textContent = '⏳ Running...';
    
    try {
        const requestData = {
            worksheet_name: selectedWorksheet.name,
            browser: browserSelect.value,
            headless: headlessCheck.checked
        };
        
        console.log('Request:', requestData);
        
        const response = await fetch('/api/run-tests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to start test execution');
        }
        
        console.log('✓ Test execution started:', data.execution_id);
        
        executionId = data.execution_id;
        execId.textContent = executionId;
        execStatus.textContent = 'Pending (Implementation coming soon)';
        currentTest.textContent = data.message;
        
        // Show view results button
        viewResultsBtn.style.display = 'inline-block';
        viewResultsBtn.href = selectedWorksheet.url;
        
        // Re-enable button
        setTimeout(() => {
            runTestsBtn.disabled = false;
            runTestsBtn.textContent = '🚀 Run Tests';
        }, 2000);
        
    } catch (error) {
        console.error('Error running tests:', error);
        showError(error.message);
        
        // Re-enable button
        runTestsBtn.disabled = false;
        runTestsBtn.textContent = '🚀 Run Tests';
    }
}

/**
 * Update progress display
 */
function updateProgress(completed, total, passed, failed) {
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    const pending = total - completed;
    
    progressFill.style.width = `${percentage}%`;
    progressText.textContent = `${completed}/${total} (${percentage}%)`;
    
    passedCount.textContent = passed;
    failedCount.textContent = failed;
    pendingCount.textContent = pending;
}

/**
 * Show error message
 */
function showError(message) {
    errorSection.style.display = 'block';
    errorMessage.textContent = message;
    console.error('❌ Error:', message);
}

/**
 * Hide error message
 */
function hideError() {
    errorSection.style.display = 'none';
}

// Export for debugging
window.testExecutor = {
    worksheets,
    selectedWorksheet,
    loadWorksheets,
    runTests
};

console.log(' Executor.js loaded successfully');
