// ============================================
// BRD Test Case Automation - Main JavaScript
// ============================================

// Global variables
let selectedFiles = [];
let currentResults = null; // 🆕 Store current results for continue feature
const API_BASE_URL = window.location.origin;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectedFilesDiv = document.getElementById('selectedFiles');
const generateBtn = document.getElementById('generateBtn');
const targetCountInput = document.getElementById('targetCount');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const resultsContent = document.getElementById('resultsContent');
const breakdownContent = document.getElementById('breakdownContent');
const continueSection = document.getElementById('continueSection'); // 🆕
const continueBtn = document.getElementById('continueBtn'); // 🆕

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('BRD Test Case Automation initialized');

    // Load config
    loadConfig();

    // Setup event listeners
    setupEventListeners();
});

// ============================================
// Event Listeners Setup
// ============================================

function setupEventListeners() {
    // Click to select files
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Generate button
    generateBtn.addEventListener('click', generateTestCases);

    // 🆕 Continue button
    continueBtn.addEventListener('click', continueGeneration);

    // 🆕 Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', handleTabSwitch);
    });

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.body.addEventListener(eventName, preventDefaults, false);
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// ============================================
// File Selection Handlers
// ============================================

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
}

function addFiles(files) {
    // Filter only PDF files
    const pdfFiles = files.filter(file => file.type === 'application/pdf' || file.name.endsWith('.pdf'));

    if (pdfFiles.length === 0) {
        alert('⚠️ Vui lòng chọn file PDF!');
        return;
    }

    // Check file size (16MB limit)
    const oversizedFiles = pdfFiles.filter(file => file.size > 16 * 1024 * 1024);
    if (oversizedFiles.length > 0) {
        alert(`⚠️ File quá lớn: ${oversizedFiles[0].name}\nKích thước tối đa: 16MB`);
        return;
    }

    // Add files to selected list
    pdfFiles.forEach(file => {
        // Check if file already selected
        if (!selectedFiles.find(f => f.name === file.name)) {
            selectedFiles.push(file);
        }
    });

    renderSelectedFiles();
    updateGenerateButton();
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderSelectedFiles();
    updateGenerateButton();
}

function renderSelectedFiles() {
    if (selectedFiles.length === 0) {
        selectedFilesDiv.innerHTML = '';
        return;
    }

    const html = selectedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-icon">📄</div>
                <div class="file-details">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${formatFileSize(file.size)}</div>
                </div>
            </div>
            <button class="file-remove" onclick="removeFile(${index})">×</button>
        </div>
    `).join('');

    selectedFilesDiv.innerHTML = html;
}

function updateGenerateButton() {
    generateBtn.disabled = selectedFiles.length === 0;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Make removeFile global
window.removeFile = removeFile;

// ============================================
// API Calls
// ============================================

async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/config`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('modelInfo').textContent = data.config.model;
            document.getElementById('coverageInfo').textContent = `${data.config.coverage_target}%`;
        }
    } catch (error) {
        console.error('Failed to load config:', error);
    }
}

async function generateTestCases() {
    if (selectedFiles.length === 0) return;

    // Hide results, show progress
    resultsSection.style.display = 'none';
    progressSection.style.display = 'block';
    generateBtn.disabled = true;

    // Reset progress
    updateProgress(0, 'Đang chuẩn bị...');

    // Prepare form data
    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });
    formData.append('target_count', targetCountInput.value);

    try {
        updateProgress(20, 'Đang upload files...');

        const response = await fetch(`${API_BASE_URL}/api/generate-testcases`, {
            method: 'POST',
            body: formData
        });

        updateProgress(40, 'Đang extract text từ PDF...');

        const data = await response.json();

        updateProgress(100, 'Hoàn thành!');

        // 🆕 Store results for continue feature
        currentResults = data;

        // Show results after a short delay
        setTimeout(() => {
            displayResults(data);
        }, 500);

    } catch (error) {
        console.error('Error:', error);
        progressSection.style.display = 'none';
        alert(`❌ Lỗi: ${error.message}`);
        generateBtn.disabled = false;
    }
}

// ============================================
// 🆕 CONTINUE GENERATION FEATURE
// ============================================

async function continueGeneration() {
    if (!currentResults || !currentResults.results || currentResults.results.length === 0) {
        alert('⚠️ Không có kết quả để tiếp tục!');
        return;
    }

    const result = currentResults.results[0]; // Get first result

    if (!result.success) {
        alert('⚠️ Không thể tiếp tục từ kết quả lỗi!');
        return;
    }

    // Hide continue section, show progress
    continueSection.style.display = 'none';
    progressSection.style.display = 'block';
    continueBtn.disabled = true;

    updateProgress(0, 'Đang chuẩn bị tiếp tục generate...');

    try {
        // Calculate how many more test cases needed
        const remaining = result.estimated_total_needed - result.total_test_cases;
        const nextBatch = Math.min(remaining, 90); // Generate up to 90 at a time

        updateProgress(20, `Đang generate thêm ${nextBatch} test cases...`);

        // For now, we'll re-upload the same file with higher target
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        formData.append('target_count', result.total_test_cases + nextBatch);

        const response = await fetch(`${API_BASE_URL}/api/generate-testcases`, {
            method: 'POST',
            body: formData
        });

        updateProgress(60, 'Đang xử lý kết quả...');

        const data = await response.json();

        updateProgress(100, 'Hoàn thành!');

        // Update current results
        currentResults = data;

        // Show updated results
        setTimeout(() => {
            displayResults(data);
            alert(`✅ Đã generate thêm ${nextBatch} test cases thành công!`);
        }, 500);

    } catch (error) {
        console.error('Error continuing generation:', error);
        progressSection.style.display = 'none';
        continueSection.style.display = 'block';
        alert(`❌ Lỗi khi tiếp tục: ${error.message}`);
        continueBtn.disabled = false;
    }
}

function updateProgress(percentage, text) {
    progressFill.style.width = `${percentage}%`;
    progressText.textContent = text;
}

// ============================================
// 🆕 Tab Switching
// ============================================

function handleTabSwitch(e) {
    const targetTab = e.target.dataset.tab;

    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to clicked tab and corresponding content
    e.target.classList.add('active');
    document.getElementById(`tab-${targetTab}`).classList.add('active');
}

// ============================================
// 🆕 Breakdown Display Functions
// ============================================

function displayBreakdown(results) {
    let html = '';

    results.forEach(result => {
        if (result.success && result.batch_breakdown) {
            const breakdown = result.batch_breakdown;

            html += `
                <div class="breakdown-item">
                    <div class="breakdown-filename">📄 ${result.filename}</div>
                    <div class="breakdown-total">
                        <strong>Tổng số test cases:</strong> ${result.total_test_cases}
                    </div>
                    
                    <div class="breakdown-batches">
                        ${Object.entries(breakdown).map(([key, data]) => {
                            if (data.count > 0) {
                                return `
                                    <div class="batch-card">
                                        <div class="batch-header">
                                            <span class="batch-name">${data.name}</span>
                                            <span class="batch-percentage">${data.percentage}%</span>
                                        </div>
                                        <div class="batch-count">${data.count} test cases</div>
                                        <div class="batch-bar">
                                            <div class="batch-bar-fill" style="width: ${data.percentage}%"></div>
                                        </div>
                                    </div>
                                `;
                            }
                            return '';
                        }).join('')}
                    </div>
                    
                    <div class="breakdown-chart">
                        ${createPieChart(breakdown)}
                    </div>
                </div>
            `;
        }
    });

    if (html === '') {
        html = '<div class="no-breakdown"><p>⚠️ Không có dữ liệu phân tích batch</p></div>';
    }

    breakdownContent.innerHTML = html;
}

function createPieChart(breakdown) {
    // Simple CSS-based pie chart
    const data = Object.values(breakdown).filter(d => d.count > 0);

    if (data.length === 0) return '';

    const colors = ['#667eea', '#f39c12', '#2ecc71'];
    let cumulativePercentage = 0;

    const gradientStops = data.map((item, index) => {
        const start = cumulativePercentage;
        cumulativePercentage += item.percentage;
        const end = cumulativePercentage;

        return `${colors[index]} ${start}% ${end}%`;
    }).join(', ');

    return `
        <div class="pie-chart-container">
            <div class="pie-chart" style="background: conic-gradient(${gradientStops})"></div>
            <div class="pie-legend">
                ${data.map((item, index) => `
                    <div class="legend-item">
                        <span class="legend-color" style="background: ${colors[index]}"></span>
                        <span class="legend-text">${item.name}: ${item.count} (${item.percentage}%)</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// ============================================
// 🆕 Show/Hide Continue Section
// ============================================

function checkCoverageAndShowContinue(result) {
    const coverageThreshold = 80; // Show continue if < 80%

    if (result.coverage_percentage < coverageThreshold) {
        const remaining = result.estimated_total_needed - result.total_test_cases;
        const remainingPercentage = 100 - result.coverage_percentage;

        document.getElementById('remainingCount').textContent = remaining;
        document.getElementById('remainingPercentage').textContent = remainingPercentage.toFixed(1) + '%';

        continueSection.style.display = 'block';
        continueBtn.disabled = false;
    } else {
        continueSection.style.display = 'none';
    }
}

function displayResults(data) {
    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';
    generateBtn.disabled = false;

    let html = '';

    if (data.success) {
        html += `<div class="result-summary">
            <p><strong>✅ Thành công:</strong> ${data.successful_files}/${data.total_files} files</p>
        </div>`;
    }

    data.results.forEach(result => {
        if (result.success) {
            // 🆕 Check if need to show continue button
            checkCoverageAndShowContinue(result);

            html += `
                <div class="result-item">
                    <div class="result-filename">📄 ${result.filename}</div>
                    <div class="result-stats">
                        <div class="stat-item">
                            <span class="stat-label">Test Cases</span>
                            <span class="stat-value">${result.total_test_cases}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Estimated Total Needed</span>
                            <span class="stat-value">${result.estimated_total_needed || 'N/A'}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Coverage</span>
                            <span class="stat-value coverage-value ${result.coverage_percentage >= 80 ? 'coverage-good' : 'coverage-warning'}">${result.coverage_percentage}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Worksheet</span>
                            <span class="stat-value worksheet-name">${result.worksheet_name.substring(0, 30)}...</span>
                        </div>
                    </div>
                    <a href="${result.sheet_url}" target="_blank" class="result-link">
                        🔗 Mở Google Sheet
                    </a>
                </div>
            `;
        } else {
            html += `
                <div class="result-item error">
                    <div class="result-filename">📄 ${result.filename}</div>
                    <div class="error-message">❌ ${result.error}</div>
                </div>
            `;
        }
    });

    resultsContent.innerHTML = html;

    // 🆕 Display breakdown in second tab
    displayBreakdown(data.results);

    // Clear selected files after successful generation
    if (data.success) {
        // Don't clear files anymore - keep for continue feature
        // selectedFiles = [];
        // renderSelectedFiles();
        // updateGenerateButton();
    }
}

// ============================================
// Utility Functions
// ============================================

console.log('Main.js loaded successfully');