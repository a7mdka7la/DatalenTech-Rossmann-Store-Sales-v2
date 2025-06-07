// Configuration
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 
    'http://localhost:8000' : 'https://your-api-url.com';

// Check if we're running on a different port in development
const DEV_API_PORT = 8000;
const CURRENT_HOST = window.location.hostname;
const API_URL = `http://${CURRENT_HOST}:${DEV_API_PORT}`;

// Use the appropriate API URL based on environment
const FINAL_API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 
    API_URL : API_BASE_URL;

// Global variables
let batchPredictionCount = 0;
let currentBatchResults = [];

// DOM elements
const elements = {
    apiStatus: document.getElementById('apiStatus'),
    statusIndicator: document.getElementById('statusIndicator'),
    statusText: document.getElementById('statusText'),
    singlePredictionForm: document.getElementById('singlePredictionForm'),
    singleResult: document.getElementById('singleResult'),
    batchPredictions: document.getElementById('batchPredictions'),
    addPredictionBtn: document.getElementById('addPrediction'),
    clearBatchBtn: document.getElementById('clearBatch'),
    submitBatchBtn: document.getElementById('submitBatch'),
    batchResults: document.getElementById('batchResults'),
    modelInfo: document.getElementById('modelInfo'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    errorModal: document.getElementById('errorModal'),
    errorMessage: document.getElementById('errorMessage')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    await checkApiHealth();
    await loadModelInfo();
    setupEventListeners();
    setDefaultDate();
}

// API Health Check
async function checkApiHealth() {
    try {
        const response = await fetch(`${FINAL_API_URL}/health`);
        const data = await response.json();
        
        if (data.model_loaded) {
            updateApiStatus('healthy', 'API Connected - Model Ready');
        } else {
            updateApiStatus('unhealthy', 'API Connected - Model Not Loaded');
        }
    } catch (error) {
        updateApiStatus('unhealthy', 'API Disconnected');
        console.error('API health check failed:', error);
    }
}

function updateApiStatus(status, text) {
    elements.statusIndicator.className = `status-indicator ${status}`;
    elements.statusText.textContent = text;
}

// Load Model Information
async function loadModelInfo() {
    try {
        const response = await fetch(`${FINAL_API_URL}/model/info`);
        
        if (!response.ok) {
            throw new Error('Failed to load model info');
        }
        
        const data = await response.json();
        displayModelInfo(data);
    } catch (error) {
        elements.modelInfo.innerHTML = '<div class="error">Failed to load model information</div>';
        console.error('Failed to load model info:', error);
    }
}

function displayModelInfo(info) {
    const featuresHtml = info.features.map(feature => 
        `<span class="feature-tag">${feature}</span>`
    ).join('');
    
    elements.modelInfo.innerHTML = `
        <div class="model-info-item">
            <h4>Model Type</h4>
            <p>${info.model_type}</p>
        </div>
        <div class="model-info-item">
            <h4>Training Dataset</h4>
            <p>${info.trained_on}</p>
        </div>
        <div class="model-info-item">
            <h4>Version</h4>
            <p>${info.version}</p>
        </div>
        <div class="model-info-item">
            <h4>Total Features</h4>
            <p>${info.total_features}</p>
        </div>
        <div class="model-info-item" style="grid-column: 1 / -1;">
            <h4>Features Used</h4>
            <div class="features-list">
                ${featuresHtml}
            </div>
        </div>
        <div class="model-info-item" style="grid-column: 1 / -1;">
            <h4>Requirements</h4>
            <p>${info.model_requirements}</p>
        </div>
    `;
}

// Event Listeners
function setupEventListeners() {
    // Single prediction form
    elements.singlePredictionForm.addEventListener('submit', handleSinglePrediction);
    
    // Batch prediction controls
    elements.addPredictionBtn.addEventListener('click', addBatchPrediction);
    elements.clearBatchBtn.addEventListener('click', clearBatchPredictions);
    elements.submitBatchBtn.addEventListener('click', handleBatchPrediction);
    
    // Download results
    document.getElementById('downloadResults').addEventListener('click', downloadResults);
}

function setDefaultDate() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const dateInput = document.getElementById('date');
    dateInput.value = tomorrow.toISOString().split('T')[0];
}

// Single Prediction Handler
async function handleSinglePrediction(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    // Convert numeric fields
    data.store = parseInt(data.store);
    data.promo = parseInt(data.promo);
    data.school_holiday = parseInt(data.school_holiday);
    
    if (data.day_of_week) {
        data.day_of_week = parseInt(data.day_of_week);
    }
      showLoading(true);
    
    try {
        const response = await fetch(`${FINAL_API_URL}/predict/simple`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Prediction failed');
        }
        
        const result = await response.json();
        displaySingleResult(result);
        
    } catch (error) {
        showError(`Prediction failed: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function displaySingleResult(result) {
    document.getElementById('resultStore').textContent = result.store;
    document.getElementById('resultDate').textContent = result.date;
    document.getElementById('resultSales').textContent = `$${result.forecasted_sales.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    document.getElementById('resultConfidence').textContent = result.confidence_score ? 
        `${(result.confidence_score * 100).toFixed(1)}%` : 'N/A';
    
    elements.singleResult.style.display = 'block';
    elements.singleResult.classList.add('success-animation');
    
    // Remove animation class after animation completes
    setTimeout(() => {
        elements.singleResult.classList.remove('success-animation');
    }, 500);
}

// Batch Prediction Handlers
function addBatchPrediction() {
    batchPredictionCount++;
    
    const batchItem = document.createElement('div');
    batchItem.className = 'batch-item';
    batchItem.innerHTML = `
        <h4>
            Prediction ${batchPredictionCount}
            <button type="button" class="remove-batch" onclick="removeBatchPrediction(this)">
                <i class="fas fa-times"></i> Remove
            </button>
        </h4>
        <form class="prediction-form">
            <div class="form-row">
                <div class="form-group">
                    <label>Store ID</label>
                    <input type="number" name="store" min="1" required>
                </div>
                <div class="form-group">
                    <label>Date</label>
                    <input type="date" name="date" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Promotion</label>
                    <select name="promo" required>
                        <option value="0">No Promotion</option>
                        <option value="1">Promotion Active</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>State Holiday</label>
                    <select name="state_holiday" required>
                        <option value="0">No Holiday</option>
                        <option value="a">Public Holiday</option>
                        <option value="b">Easter Holiday</option>
                        <option value="c">Christmas</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>School Holiday</label>
                    <select name="school_holiday" required>
                        <option value="0">No School Holiday</option>
                        <option value="1">School Holiday</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Day of Week</label>
                    <select name="day_of_week">
                        <option value="">Auto-calculate</option>
                        <option value="1">Monday</option>
                        <option value="2">Tuesday</option>
                        <option value="3">Wednesday</option>
                        <option value="4">Thursday</option>
                        <option value="5">Friday</option>
                        <option value="6">Saturday</option>
                        <option value="7">Sunday</option>
                    </select>
                </div>
            </div>
        </form>
    `;
    
    elements.batchPredictions.appendChild(batchItem);
    updateBatchControls();
    
    // Set default date for new prediction
    const dateInput = batchItem.querySelector('input[name="date"]');
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + batchPredictionCount);
    dateInput.value = tomorrow.toISOString().split('T')[0];
}

function removeBatchPrediction(button) {
    button.closest('.batch-item').remove();
    updateBatchControls();
}

function clearBatchPredictions() {
    elements.batchPredictions.innerHTML = '';
    elements.batchResults.style.display = 'none';
    batchPredictionCount = 0;
    updateBatchControls();
}

function updateBatchControls() {
    const itemCount = elements.batchPredictions.children.length;
    elements.submitBatchBtn.style.display = itemCount > 0 ? 'block' : 'none';
}

async function handleBatchPrediction() {
    const batchItems = elements.batchPredictions.querySelectorAll('.batch-item');
    const predictions = [];
    
    // Collect data from all batch items
    for (const item of batchItems) {
        const form = item.querySelector('.prediction-form');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Convert numeric fields
        data.store = parseInt(data.store);
        data.promo = parseInt(data.promo);
        data.school_holiday = parseInt(data.school_holiday);
        
        if (data.day_of_week) {
            data.day_of_week = parseInt(data.day_of_week);
        }
        
        predictions.push(data);
    }
    
    if (predictions.length === 0) {
        showError('Please add at least one prediction');
        return;
    }
      showLoading(true);
    
    try {
        const response = await fetch(`${FINAL_API_URL}/predict/batch/simple`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ predictions })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Batch prediction failed');
        }
        
        const result = await response.json();
        displayBatchResults(result);
        
    } catch (error) {
        showError(`Batch prediction failed: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function displayBatchResults(result) {
    currentBatchResults = result.predictions;
    
    document.getElementById('totalPredictions').textContent = result.total_predictions;
    
    const tableHtml = `
        <table>
            <thead>
                <tr>
                    <th>Store</th>
                    <th>Date</th>
                    <th>Forecasted Sales</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody>
                ${result.predictions.map(pred => `
                    <tr>
                        <td>${pred.store}</td>
                        <td>${pred.date}</td>
                        <td>$${pred.forecasted_sales.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        <td>${pred.confidence_score ? `${(pred.confidence_score * 100).toFixed(1)}%` : 'N/A'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    document.getElementById('batchResultsTable').innerHTML = tableHtml;
    elements.batchResults.style.display = 'block';
    elements.batchResults.classList.add('success-animation');
    
    // Remove animation class after animation completes
    setTimeout(() => {
        elements.batchResults.classList.remove('success-animation');
    }, 500);
}

// Utility Functions
function showLoading(show) {
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorModal.style.display = 'flex';
}

function closeErrorModal() {
    elements.errorModal.style.display = 'none';
}

function downloadResults() {
    if (currentBatchResults.length === 0) {
        showError('No results to download');
        return;
    }
    
    // Create CSV content
    const headers = ['Store', 'Date', 'Forecasted Sales', 'Confidence Score'];
    const csvContent = [
        headers.join(','),
        ...currentBatchResults.map(result => [
            result.store,
            result.date,
            result.forecasted_sales.toFixed(2),
            result.confidence_score ? result.confidence_score.toFixed(4) : 'N/A'
        ].join(','))
    ].join('\n');
    
    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rossmann_predictions_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Auto-refresh API health check every 30 seconds
setInterval(checkApiHealth, 30000);

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    if (event.target === elements.errorModal) {
        closeErrorModal();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // ESC to close modal
    if (event.key === 'Escape') {
        closeErrorModal();
    }
    
    // Ctrl+Enter to submit single prediction
    if (event.ctrlKey && event.key === 'Enter') {
        if (document.activeElement.closest('#singlePredictionForm')) {
            elements.singlePredictionForm.dispatchEvent(new Event('submit'));
        }
    }
});
