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
    const clientDataText = formData.get('clientData');
    
    // Parse client data into individual clients
    const clients = parseClientData(clientDataText);
    
    if (clients.length === 0) {
        showError('No valid client data found. Please enter client information.');
        return;
    }
    
    // Validate each client
    const validationErrors = [];
    clients.forEach((client, index) => {
        const validation = validateAnalysisData(client);
        if (!validation.valid) {
            validationErrors.push(`Client ${index + 1}: ${validation.errors.join(', ')}`);
        }
    });
    
    if (validationErrors.length > 0) {
        showError(validationErrors.join('\n'));
        return;
    }
    
    try {
        showModal('loadingModal');
        
        // Send multi-client analysis request
        const response = await fetch(`${API_BASE}/api/analyze-multiple`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ clients: clients })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const results = await response.json();
        displayMultipleResults(results);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(`Analysis failed: ${error.message}`);
    } finally {
        hideModal('loadingModal');
    }
}

// Parse client data from text input
function parseClientData(text) {
    if (!text || text.trim().length === 0) {
        return [];
    }
    
    // Split by common separators (---, CLIENT:, or double newlines)
    const clientSections = text.split(/(?:^|\n)(?:---|CLIENT:|client:)/i)
        .map(section => section.trim())
        .filter(section => section.length > 0);
    
    // If no separators found, treat as single client
    if (clientSections.length === 1) {
        const client = parseClientSection(text);
        return client ? [client] : [];
    }
    
    // Parse each section
    const clients = [];
    clientSections.forEach(section => {
        const client = parseClientSection(section);
        if (client) {
            clients.push(client);
        }
    });
    
    return clients;
}

// Parse individual client section
function parseClientSection(text) {
    const client = {
        company_name: '',
        account_manager: '',
        csm: '',
        budget_tier: '',
        monthly_budget: 0,
        eight_week_spend_deviation: '',
        projected_2025_spend_deviation: '',
        campaign_duration_months: 6,
        campaign_objectives: '',
        current_performance_metrics: '',
        budget_utilization: '',
        client_reported_notes: '',
        notes: '',
        recent_changes_or_concerns: ''
    };
    
    // Extract information using various patterns
    const patterns = {
        company_name: /(?:company|client|name):\s*([^\n]+)/i,
        account_manager: /(?:account\s*manager|manager|am):\s*([^\n]+)/i,
        csm: /(?:csm|customer\s*success\s*manager):\s*([^\n]+)/i,
        budget_tier: /(?:budget\s*tier|tier):\s*([^\n]+)/i,
        monthly_budget: /(?:budget|monthly\s*budget):\s*\$?([0-9,]+)/i,
        eight_week_spend_deviation: /(?:8[-\s]*week\s*spend\s*deviation|8\s*week\s*deviation):\s*([^\n]+)/i,
        projected_2025_spend_deviation: /(?:2025\s*projected\s*spend\s*deviation|2025\s*projection):\s*([^\n]+)/i,
        campaign_duration_months: /(?:duration|campaign\s*duration):\s*([0-9]+)[\s]*(?:months?|mos?)/i,
        campaign_objectives: /(?:objectives?|goals?):\s*([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)/i,
        current_performance_metrics: /(?:performance|metrics|stats):\s*([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)/i,
        budget_utilization: /(?:budget\s*(?:status|utilization|spend)|spend|pacing):\s*([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)/i,
        client_reported_notes: /(?:client\s*(?:notes|feedback)|feedback|client\s*notes|satisfaction):\s*([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)/i,
        notes: /(?:^notes|additional\s*notes):\s*([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)/i,
        recent_changes_or_concerns: /(?:recent\s*changes?|changes?|concerns?):\s*([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)/i
    };
    
    // Try to extract data using patterns
    let hasValidData = false;
    
    for (const [field, pattern] of Object.entries(patterns)) {
        const match = text.match(pattern);
        if (match) {
            let value = match[1].trim();
            
            if (field === 'monthly_budget') {
                // Parse budget number
                const budgetNum = parseFloat(value.replace(/[,$]/g, ''));
                if (!isNaN(budgetNum)) {
                    client[field] = budgetNum;
                    hasValidData = true;
                }
            } else if (field === 'campaign_duration_months') {
                // Parse duration
                const duration = parseInt(value);
                if (!isNaN(duration)) {
                    client[field] = duration;
                }
            } else {
                client[field] = value;
                if (value.length > 0) {
                    hasValidData = true;
                }
            }
        }
    }
    
    // Try to extract company name from first line if not found
    if (!client.company_name) {
        const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        if (lines.length > 0) {
            // First non-empty line might be company name
            const firstLine = lines[0].replace(/^(?:client|company):\s*/i, '');
            if (firstLine.length > 0) {
                client.company_name = firstLine;
                hasValidData = true;
            }
        }
    }
    
    // If we couldn't extract structured data, treat the whole text as client notes
    if (!hasValidData && text.trim().length > 0) {
        client.company_name = 'Client Analysis';
        client.client_reported_notes = text.trim();
        hasValidData = true;
    }
    
    return hasValidData ? client : null;
}

// Validate analysis data
function validateAnalysisData(data) {
    const errors = [];
    
    if (!data.company_name || data.company_name.trim().length === 0) {
        errors.push('Company name is required');
    }
    
    // For multi-client input, we're more flexible with validation
    const allTextFields = [
        'campaign_objectives',
        'current_performance_metrics', 
        'budget_utilization',
        'client_reported_notes'
    ];
    
    let hasAnyContent = false;
    allTextFields.forEach(field => {
        if (data[field] && data[field].trim().length > 0) {
            hasAnyContent = true;
        }
    });
    
    if (!hasAnyContent) {
        errors.push('Please provide some campaign information (objectives, performance, budget status, or client notes)');
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
        ${(result.csm || result.budget_tier || result.eight_week_spend_deviation || result.projected_2025_spend_deviation || result.notes) ? `
            <div class="client-info-section">
                <h3>📋 Client Information</h3>
                <div class="client-info-grid">
                    ${result.budget_tier ? `<div class="info-item"><strong>Budget Tier:</strong> ${escapeHtml(result.budget_tier)}</div>` : ''}
                    ${result.csm ? `<div class="info-item"><strong>CSM:</strong> ${escapeHtml(result.csm)}</div>` : ''}
                    ${result.eight_week_spend_deviation ? `<div class="info-item"><strong>8-Week Spend Deviation:</strong> ${escapeHtml(result.eight_week_spend_deviation)}</div>` : ''}
                    ${result.projected_2025_spend_deviation ? `<div class="info-item"><strong>2025 Projected Deviation:</strong> ${escapeHtml(result.projected_2025_spend_deviation)}</div>` : ''}
                    ${result.notes ? `<div class="info-item info-notes"><strong>Notes:</strong> ${escapeHtml(result.notes)}</div>` : ''}
                </div>
            </div>
        ` : ''}
        
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

// Display multiple client analysis results
function displayMultipleResults(results) {
    if (!results || !Array.isArray(results) || results.length === 0) {
        showError('No results received from analysis');
        return;
    }
    
    if (results.length === 1) {
        // Single result, use existing display function
        displayResults(results[0]);
        return;
    }
    
    // Multiple results, create grid layout
    let totalProcessingTime = 0;
    const htmlContent = results.map((result, index) => {
        const category = healthCategories[result.category] || healthCategories["might_need_attention"];
        totalProcessingTime += result.processing_time || 0;
        
        return `
            <div class="client-result category-${result.category}">
                <div class="client-result-header">
                    <h3>${escapeHtml(result.company_name || `Client ${index + 1}`)}</h3>
                    ${result.budget_tier ? `<span class="budget-tier-badge">${escapeHtml(result.budget_tier)} Tier</span>` : ''}
                </div>
                <div class="client-result-content">
                    ${(result.csm || result.eight_week_spend_deviation || result.projected_2025_spend_deviation || result.notes) ? `
                        <div class="client-info-section">
                            <h4>📋 Client Information</h4>
                            <div class="client-info-grid">
                                ${result.csm ? `<div class="info-item"><strong>CSM:</strong> ${escapeHtml(result.csm)}</div>` : ''}
                                ${result.eight_week_spend_deviation ? `<div class="info-item"><strong>8-Week Spend Deviation:</strong> ${escapeHtml(result.eight_week_spend_deviation)}</div>` : ''}
                                ${result.projected_2025_spend_deviation ? `<div class="info-item"><strong>2025 Projected Deviation:</strong> ${escapeHtml(result.projected_2025_spend_deviation)}</div>` : ''}
                                ${result.notes ? `<div class="info-item info-notes"><strong>Notes:</strong> ${escapeHtml(result.notes)}</div>` : ''}
                            </div>
                        </div>
                    ` : ''}
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
                </div>
            </div>
        `;
    }).join('');
    
    resultsContent.innerHTML = `
        <div class="results-summary">
            <h3>📋 Analysis Summary</h3>
            <p>Analyzed ${results.length} client campaign${results.length > 1 ? 's' : ''} in ${totalProcessingTime.toFixed(2)} seconds</p>
        </div>
        <div class="results-grid">
            ${htmlContent}
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

