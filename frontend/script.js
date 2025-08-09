// Client Health Chatbot Frontend JavaScript

// Configuration
const API_BASE = window.location.origin;

// DOM Elements
const analysisForm = document.getElementById('analysisForm');
const resultsContainer = document.getElementById('resultsContainer');
const resultsContent = document.getElementById('resultsContent');
const historySection = document.getElementById('historySection');
const analysisSection = document.getElementById('analysisSection');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const viewHistoryBtn = document.getElementById('viewHistoryBtn');
const loadingModal = document.getElementById('loadingModal');
const errorModal = document.getElementById('errorModal');
const errorMessage = document.getElementById('errorMessage');

// Health categories configuration
const healthCategories = {
    "healthy": {
        "name": "Campaign Healthy",
        "icon": "🟢",
        "description": "Campaign is performing well, budget on track, client satisfied"
    },
    "might_need_attention": {
        "name": "Monitoring Needed",
        "icon": "🟡",
        "description": "Campaign shows some indicators that warrant closer monitoring or optimization"
    },
    "need_attention_positive": {
        "name": "Action Needed - Growth Opportunity",
        "icon": "🟠",
        "description": "Campaign needs attention but shows positive indicators for scaling or expansion"
    },
    "need_attention_negative": {
        "name": "Action Needed - Risk Management",
        "icon": "🔴",
        "description": "Campaign requires immediate attention due to budget, performance, or client satisfaction concerns"
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Form submission
    analysisForm.addEventListener('submit', handleAnalysisSubmit);
    
    // Navigation buttons
    newAnalysisBtn.addEventListener('click', showAnalysisSection);
    viewHistoryBtn.addEventListener('click', showHistorySection);
    
    // Load initial config
    loadConfig();
});

// Analysis form submission
async function handleAnalysisSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(analysisForm);
    const analysisData = {
        company_name: formData.get('companyName'),
        account_manager: formData.get('accountManager'),
        monthly_budget: parseFloat(formData.get('monthlyBudget')),
        campaign_duration_months: parseInt(formData.get('campaignDuration')),
        campaign_objectives: formData.get('campaignObjectives'),
        current_performance_metrics: formData.get('performanceMetrics'),
        budget_utilization: formData.get('budgetUtilization'),
        client_reported_notes: formData.get('clientNotes'),
        recent_changes_or_concerns: formData.get('recentChanges') || ''
    };
    
    // Validate required fields
    const validation = validateAnalysisData(analysisData);
    if (!validation.valid) {
        showError(validation.errors.join('\n'));
        return;
    }
    
    try {
        showModal('loadingModal');
        
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(analysisData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const result = await response.json();
        displayResults(result);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(`Analysis failed: ${error.message}`);
    } finally {
        hideModal('loadingModal');
    }
}

// Validate analysis data
function validateAnalysisData(data) {
    const errors = [];
    
    if (!data.company_name || data.company_name.trim().length === 0) {
        errors.push('Company name is required');
    }
    
    if (!data.account_manager || data.account_manager.trim().length === 0) {
        errors.push('Account manager is required');
    }
    
    if (!data.monthly_budget || data.monthly_budget <= 0) {
        errors.push('Valid monthly budget is required');
    }
    
    if (!data.campaign_duration_months || data.campaign_duration_months <= 0) {
        errors.push('Valid campaign duration is required');
    }
    
    const requiredTextFields = [
        'campaign_objectives',
        'current_performance_metrics',
        'budget_utilization',
        'client_reported_notes'
    ];
    
    let filledTextFields = 0;
    requiredTextFields.forEach(field => {
        if (data[field] && data[field].trim().length > 0) {
            filledTextFields++;
        }
    });
    
    if (filledTextFields < 2) {
        errors.push('Please provide at least campaign objectives and performance metrics or client notes');
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

// Display analysis results
function displayResults(result) {
    const category = healthCategories[result.category] || healthCategories["might_need_attention"];
    
    resultsContent.innerHTML = `
        <div class="health-status category-${result.category}">
            <div class="health-icon">${category.icon}</div>
            <div class="health-info">
                <h3>${category.name}</h3>
                <p>${category.description}</p>
            </div>
            <div class="confidence-badge">
                ${result.confidence}% Confidence
            </div>
        </div>

        <div class="assessment-section">
            <h3>🎯 Campaign Analysis</h3>
            <p>${result.reasoning}</p>
        </div>

        ${result.budget_assessment ? `
            <div class="assessment-section">
                <h3>💰 Budget Assessment</h3>
                <p>${result.budget_assessment}</p>
            </div>
        ` : ''}

        ${result.performance_assessment ? `
            <div class="assessment-section">
                <h3>📊 Performance Assessment</h3>
                <p>${result.performance_assessment}</p>
            </div>
        ` : ''}

        ${result.client_satisfaction ? `
            <div class="assessment-section">
                <h3>😊 Client Satisfaction</h3>
                <p>${result.client_satisfaction}</p>
            </div>
        ` : ''}

        ${result.recommendations && result.recommendations.length > 0 ? `
            <div class="assessment-section">
                <h3>💡 Action Items</h3>
                <ul class="assessment-list">
                    ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        ` : ''}

        ${result.risk_factors && result.risk_factors.length > 0 ? `
            <div class="assessment-section">
                <h3>⚠️ Risk Factors</h3>
                <ul class="assessment-list">
                    ${result.risk_factors.map(risk => `<li>${risk}</li>`).join('')}
                </ul>
            </div>
        ` : ''}

        ${result.positive_indicators && result.positive_indicators.length > 0 ? `
            <div class="assessment-section">
                <h3>✅ Opportunities & Strengths</h3>
                <ul class="assessment-list">
                    ${result.positive_indicators.map(indicator => `<li>${indicator}</li>`).join('')}
                </ul>
            </div>
        ` : ''}

        <div class="assessment-section">
            <p style="font-size: 0.9rem; color: #666; margin-top: 20px;">
                Analysis completed in ${result.processing_time.toFixed(2)} seconds
            </p>
        </div>
    `;
    
    resultsContainer.style.display = 'block';
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Show analysis section
function showAnalysisSection() {
    analysisSection.style.display = 'block';
    historySection.style.display = 'none';
    newAnalysisBtn.classList.add('btn-primary');
    newAnalysisBtn.classList.remove('btn-secondary');
    viewHistoryBtn.classList.add('btn-secondary');
    viewHistoryBtn.classList.remove('btn-primary');
}

// Show history section
async function showHistorySection() {
    analysisSection.style.display = 'none';
    historySection.style.display = 'block';
    viewHistoryBtn.classList.add('btn-primary');
    viewHistoryBtn.classList.remove('btn-secondary');
    newAnalysisBtn.classList.add('btn-secondary');
    newAnalysisBtn.classList.remove('btn-primary');
    
    await loadHistory();
}

// Load conversation history
async function loadHistory() {
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = '<div class="loading">Loading conversation history...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/conversations`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const conversations = await response.json();
        
        if (conversations.length === 0) {
            historyContent.innerHTML = `
                <div class="text-center" style="padding: 40px;">
                    <p style="color: #666; font-size: 1.1rem;">No analysis history found</p>
                    <p style="color: #888; margin-top: 8px;">Start analyzing campaigns to build your history</p>
                </div>
            `;
            return;
        }
        
        historyContent.innerHTML = conversations.map(conv => {
            const category = healthCategories[conv.category] || healthCategories["might_need_attention"];
            const timestamp = new Date(conv.timestamp).toLocaleString();
            
            return `
                <div class="history-item category-${conv.category}" onclick="viewConversation('${conv.conversation_id}')">
                    <div class="history-header">
                        <div class="history-company">${conv.company_name}</div>
                        <div class="history-timestamp">${timestamp}</div>
                    </div>
                    <div class="history-status">
                        <span>${category.icon} ${category.name}</span>
                        <span class="history-category">${conv.confidence}% confidence</span>
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('History loading error:', error);
        historyContent.innerHTML = `
            <div class="text-center" style="padding: 40px;">
                <p style="color: #ef4444;">Failed to load history</p>
                <p style="color: #888; margin-top: 8px;">${error.message}</p>
            </div>
        `;
    }
}

// View conversation details
async function viewConversation(conversationId) {
    try {
        const response = await fetch(`${API_BASE}/api/conversations/${conversationId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const conversation = await response.json();
        
        // Find the bot response with evaluation results
        const botResponse = conversation.events.find(event => event.event_type === 'bot_response');
        if (botResponse && botResponse.content.evaluation) {
            displayResults({
                ...botResponse.content.evaluation,
                conversation_id: conversationId,
                processing_time: botResponse.metadata.processing_time_seconds || 0
            });
            showAnalysisSection();
        }
        
    } catch (error) {
        console.error('Conversation loading error:', error);
        showError(`Failed to load conversation: ${error.message}`);
    }
}

// Load configuration
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/api/config`);
        if (response.ok) {
            const config = await response.json();
            // Update health categories if provided by backend
            if (config.health_categories) {
                Object.assign(healthCategories, config.health_categories);
            }
        }
    } catch (error) {
        console.log('Config loading failed, using defaults');
    }
}

// Modal functions
function showModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

function hideModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function closeModal(modalId) {
    hideModal(modalId);
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    showModal('errorModal');
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
