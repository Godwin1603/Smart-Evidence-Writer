// script.js
// Global variables
let selectedFile = null;
let currentCaseId = null;
let currentEvidenceId = null;

// DOM elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('evidenceFile');
const selectFileBtn = document.getElementById('selectFileBtn');
const generateBtn = document.getElementById('generateBtn');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileType = document.getElementById('file-type');
const uploadSection = document.getElementById('upload-section');
const progressSection = document.getElementById('progress-section');
const progressText = document.getElementById('progress-text');
const progressFill = document.getElementById('progress-fill');
const reportSection = document.getElementById('report-section');
const reportContent = document.getElementById('report-content');
const downloadBtn = document.getElementById('downloadBtn');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');

// Advanced features
const advancedAnalysisToggle = document.getElementById('advancedAnalysis');
const analysisOptions = document.getElementById('analysisOptions');
const analysisType = document.getElementById('analysisType');
const reportLanguage = document.getElementById('reportLanguage');
const caseDescription = document.getElementById('caseDescription');
const officerId = document.getElementById('officerId');

// Case management
const viewCasesBtn = document.getElementById('viewCasesBtn');
const searchCasesBtn = document.getElementById('searchCasesBtn');
const createCaseBtn = document.getElementById('createCaseBtn');
const casesList = document.getElementById('cases-list');

// Q&A features
const questionInput = document.getElementById('questionInput');
const askQuestionBtn = document.getElementById('askQuestionBtn');
const qaResponse = document.getElementById('qa-response');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    checkSystemHealth();
});

function setupEventListeners() {
    // File selection button
    selectFileBtn.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop events
    dropZone.addEventListener('dragover', handleDragOver, false);
    dropZone.addEventListener('dragleave', handleDragLeave, false);
    dropZone.addEventListener('drop', handleFileDrop, false);

    // Generate report button
    generateBtn.addEventListener('click', generateReport);

    // New analysis button
    newAnalysisBtn.addEventListener('click', resetToUpload);

    // Advanced analysis toggle
    advancedAnalysisToggle.addEventListener('change', function() {
        analysisOptions.style.display = this.checked ? 'grid' : 'none';
    });

    // Case management
    viewCasesBtn.addEventListener('click', loadCases);
    searchCasesBtn.addEventListener('click', searchCases);
    createCaseBtn.addEventListener('click', createCase);

    // Q&A
    askQuestionBtn.addEventListener('click', askQuestion);
    questionInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            askQuestion();
        }
    });

    // Collapsible report sections
    reportContent.addEventListener('click', handleReportCollapse);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        const allowedTypes = ['image/jpeg', 'image/png', 'video/mp4', 'audio/mpeg', 'audio/wav'];
        if (allowedTypes.includes(file.type)) {
            processFile(file);
        } else {
            showError(`File type not supported: ${file.type}. Please use images, videos, or audio files.`);
        }
    }
}

function processFile(file) {
    selectedFile = file;

    // Update file info
    fileName.textContent = file.name;
    fileType.textContent = getFileTypeLabel(file.type);
    fileInfo.style.display = 'block';

    // Enable generate button
    generateBtn.disabled = false;
    
    // Update button text
    generateBtn.querySelector('.btn-text').textContent = `Analyze ${getFileTypeLabel(file.type)}`;
}

function getFileTypeLabel(mimeType) {
    if (mimeType.startsWith('image/')) return 'Image';
    if (mimeType.startsWith('video/')) return 'Video';
    if (mimeType.startsWith('audio/')) return 'Audio';
    return mimeType || 'Unknown';
}

async function generateReport() {
    if (!selectedFile) return;

    const useAdvanced = advancedAnalysisToggle.checked;
    const analysisTypeValue = analysisType.value;
    const languageValue = reportLanguage.value;
    const caseDescriptionValue = caseDescription.value;
    const officerIdValue = officerId.value;

    // Show progress
    uploadSection.style.display = 'none';
    reportSection.style.display = 'none';
    progressSection.style.display = 'block';
    generateBtn.disabled = true;

    try {
        updateProgress('Initializing analysis system...', 10);
        await sleep(500);

        const formData = new FormData();
        formData.append('evidence', selectedFile);
        
        if (useAdvanced) {
            formData.append('description', caseDescriptionValue);
            formData.append('officerId', officerIdValue);
            formData.append('language', languageValue);
            
            updateProgress('Running advanced AI analysis...', 30);
            await sleep(1000);
            
            const response = await fetch('http://127.0.0.1:5000/api/analyze-advanced', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                updateProgress('Compiling comprehensive report...', 80);
                await sleep(1000);
                updateProgress('Finalizing advanced analysis...', 95);
                await sleep(500);
                updateProgress('Advanced analysis complete!', 100);
                await sleep(600);
                
                currentCaseId = data.case_id;
                currentEvidenceId = data.evidence_id;
                displayReport(data);
            } else {
                throw new Error(data.error || 'Advanced analysis failed');
            }
        } else {
            // Standard analysis
            formData.append('language', languageValue);
            
            updateProgress('Uploading file to secure server...', 20);
            await sleep(800);

            updateProgress('Analyzing evidence with AI engine...', 50);
            await sleep(1200);

            const response = await fetch('http://127.0.0.1:5000/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                updateProgress('Compiling professional report...', 80);
                await sleep(1000);
                updateProgress('Finalizing analysis report...', 95);
                await sleep(500);
                updateProgress('Analysis complete!', 100);
                await sleep(600);

                displayReport(data);
            } else {
                throw new Error(data.error || 'Server returned an error response.');
            }
        }
    } catch (err) {
        console.error('Analysis error:', err);
        showError(`Analysis failed: ${err.message}`);
        resetUI();
    }
}

function updateProgress(text, percentage) {
    progressText.textContent = text;
    progressFill.style.width = `${percentage}%`;
}

function displayReport(data) {
    progressSection.style.display = 'none';
    reportSection.style.display = 'block';
    uploadSection.style.display = 'block';
    
    // Reset for next file
    generateBtn.disabled = true;
    fileInfo.style.display = 'none';
    selectedFile = null;
    fileInput.value = null;

    // Set download link
    downloadBtn.href = data.pdf_url;
    currentEvidenceId = data.evidence_id || data.report_id;

    // Parse and display report content
    const analysis = data.analysis || 'No analysis content was returned from the server.';
    const structuredReport = parseAnalysisToHTML(analysis);

    reportContent.innerHTML = structuredReport;
    
    // Scroll to report section
    reportSection.scrollIntoView({ behavior: 'smooth' });
}

function parseAnalysisToHTML(analysisText) {
    // Split by numbered sections or major headings
    const sections = analysisText.split(/\n(?=\d\.\s|===|SUMMARY:|SCENE ANALYSIS:|OBJECT TRACKING:|FACE ANALYSIS:|EXECUTIVE SUMMARY:|DETAILED ANALYSIS:|CHRONOLOGICAL TIMELINE:|KEY EVIDENCE FINDINGS:)/);
    
    let html = '';

    for (const section of sections) {
        if (!section.trim()) continue;

        const firstNewlineIndex = section.indexOf('\n');
        
        let title = '';
        let content = '';

        if (firstNewlineIndex !== -1) {
            title = section.substring(0, firstNewlineIndex).trim();
            content = section.substring(firstNewlineIndex + 1).trim();
        } else {
            title = section.trim();
            content = 'No detailed content available for this section.';
        }

        // Clean up title
        title = title.replace(/^===|===$/g, '').trim();

        // Make the first section open by default
        const isCollapsed = !title.startsWith('1.') && !title.includes('SUMMARY') && !title.includes('EXECUTIVE');

        html += `
            <div class="report-item ${isCollapsed ? 'collapsed' : ''}">
                <h3>${escapeHTML(title)}</h3>
                <div class="content">
                    ${applyHighlights(content)}
                </div>
            </div>
        `;
    }
    
    // Add empty state if no sections found
    if (!html) {
        html = `
            <div class="report-item">
                <h3>Analysis Report</h3>
                <div class="content">
                    <p>No structured analysis could be generated from the response.</p>
                    <p>Raw response: ${escapeHTML(analysisText)}</p>
                </div>
            </div>
        `;
    }
    
    return html;
}

function applyHighlights(content) {
    let highlightedText = escapeHTML(content);

    // Order matters for highlighting
    
    // 1. Red (Missing/Suspicious/Errors)
    highlightedText = highlightedText.replace(
        /\b(missed|missing|unclear|suspicious|not visible|obscured|unidentified|error|failed)\b/gi,
        '<span class="highlight-evidence">$&</span>'
    );

    // 2. Blue (Plates / Locations)
    highlightedText = highlightedText.replace(
        /\b(TN[-\s]?\d{1,2}[-\s]?[A-Z]{1,2}[-\s]?\d{1,4})\b/gi,
        '<span class="highlight-location">$&</span>'
    );
    
    highlightedText = highlightedText.replace(
        /\b(Chennai|Coimbatore|Madurai|Tiruchirappalli|Tirunelveli|Salem|Tiruppur|Erode|Kanchipuram|Vellore)\b/gi,
        '<span class="highlight-location">$&</span>'
    );

    // 3. Yellow (Timestamps)
    highlightedText = highlightedText.replace(
        /\b([01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?\b/g,
        '<span class="highlight-timestamp">$&</span>'
    );

    // 4. Green (Observations/Objects)
    highlightedText = highlightedText.replace(
        /\b(person|vehicle|object|activity|man|woman|car|bike|truck|individual|subject|face|object)\b/gi,
        '<span class="highlight-observation">$&</span>'
    );

    // 5. Advanced analysis highlights
    highlightedText = highlightedText.replace(
        /\b(advanced|detailed|forensic|analysis|tracking|detection)\b/gi,
        '<span class="highlight-advanced">$&</span>'
    );

    // 6. Confidence scores
    highlightedText = highlightedText.replace(
        /\b(confidence:?\s*\d+\.\d+)\b/gi,
        '<span class="highlight-forensic">$&</span>'
    );

    // Convert newlines to <br> tags and preserve paragraphs
    highlightedText = highlightedText.replace(/\n\n/g, '</p><p>');
    highlightedText = highlightedText.replace(/\n/g, '<br>');
    highlightedText = '<p>' + highlightedText + '</p>';

    return highlightedText;
}

function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, function(m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        }[m];
    });
}

function handleReportCollapse(e) {
    const header = e.target.closest('h3');
    if (header) {
        const reportItem = header.closest('.report-item');
        if (reportItem) {
            reportItem.classList.toggle('collapsed');
        }
    }
}

// Case Management Functions
async function loadCases() {
    try {
        showLoading('Loading cases...');
        const response = await fetch('/api/cases');
        const data = await response.json();
        
        if (response.ok) {
            displayCases(data.cases);
        } else {
            throw new Error(data.error || 'Failed to load cases');
        }
    } catch (err) {
        showError(`Error loading cases: ${err.message}`);
    }
}

function displayCases(cases) {
    if (cases.length === 0) {
        casesList.innerHTML = '<div class="case-item"><p class="no-cases">No cases found. Create your first case by uploading evidence with advanced analysis enabled.</p></div>';
        return;
    }
    
    const casesHTML = cases.map(caseItem => `
        <div class="case-item" onclick="viewCase('${caseItem.id}')">
            <div class="case-header">
                <span class="case-title">${escapeHTML(caseItem.title || 'Untitled Case')}</span>
                <span class="case-date">${formatDate(caseItem.createdAt)}</span>
            </div>
            <div class="case-description">
                ${escapeHTML(caseItem.description || 'No description provided')}
            </div>
            <div class="case-meta">
                <span>Officer: ${escapeHTML(caseItem.officerId || 'Unknown')}</span>
                <span>Evidence: ${caseItem.evidenceCount || 0} items</span>
            </div>
        </div>
    `).join('');
    
    casesList.innerHTML = casesHTML;
}

async function viewCase(caseId) {
    try {
        showLoading('Loading case evidence...');
        const response = await fetch(`/api/cases/${caseId}/evidence`);
        const data = await response.json();
        
        if (response.ok) {
            displayCaseEvidence(data.evidence, caseId);
        } else {
            throw new Error(data.error || 'Failed to load case evidence');
        }
    } catch (err) {
        showError(`Error loading case: ${err.message}`);
    }
}

function displayCaseEvidence(evidence, caseId) {
    if (evidence.length === 0) {
        casesList.innerHTML = `
            <div class="case-detail">
                <button class="btn-secondary" onclick="loadCases()">← Back to Cases</button>
                <h3>Case Evidence</h3>
                <p>No evidence found for this case.</p>
            </div>
        `;
        return;
    }
    
    const evidenceHTML = evidence.map(item => `
        <div class="evidence-item">
            <h4>${escapeHTML(item.filename)}</h4>
            <p><strong>Type:</strong> ${item.fileType || 'Unknown'} | <strong>Analysis:</strong> ${item.analysisType || 'standard'}</p>
            <p><strong>Added:</strong> ${formatDate(item.addedAt)}</p>
            <button class="btn-primary" onclick="viewEvidenceReport('${item.evidenceId}')">View Report</button>
        </div>
    `).join('');
    
    casesList.innerHTML = `
        <div class="case-detail">
            <button class="btn-secondary" onclick="loadCases()">← Back to Cases</button>
            <h3>Case Evidence</h3>
            ${evidenceHTML}
        </div>
    `;
}

function viewEvidenceReport(evidenceId) {
    window.open(`/reports/${evidenceId}`, '_blank');
}

async function searchCases() {
    const officerId = prompt('Enter Officer ID to search:');
    if (officerId) {
        try {
            showLoading('Searching cases...');
            const response = await fetch(`/api/cases?officerId=${encodeURIComponent(officerId)}`);
            const data = await response.json();
            
            if (response.ok) {
                displayCases(data.cases);
            } else {
                throw new Error(data.error || 'Search failed');
            }
        } catch (err) {
            showError(`Search error: ${err.message}`);
        }
    }
}

async function createCase() {
    const title = prompt('Enter case title:');
    if (title) {
        const description = prompt('Enter case description:');
        const officerId = prompt('Enter your officer ID:');
        
        try {
            const response = await fetch('/api/cases/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    description: description || '',
                    officerId: officerId || 'unknown'
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showSuccess('Case created successfully!');
                loadCases();
            } else {
                throw new Error(data.error || 'Failed to create case');
            }
        } catch (err) {
            showError(`Error creating case: ${err.message}`);
        }
    }
}

// Q&A Functions
async function askQuestion() {
    const question = questionInput.value.trim();
    if (!question) {
        showError('Please enter a question');
        return;
    }

    if (!currentEvidenceId) {
        showError('Please analyze evidence first to enable Q&A');
        return;
    }

    try {
        qaResponse.innerHTML = '<p>Thinking...</p>';
        
        const response = await fetch(`/api/evidence/${currentEvidenceId}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            qaResponse.innerHTML = `
                <p><strong>Question:</strong> ${escapeHTML(data.question)}</p>
                <p><strong>Answer:</strong> ${applyHighlights(data.answer)}</p>
                ${data.confidence ? `<p><em>Confidence: ${(data.confidence * 100).toFixed(1)}%</em></p>` : ''}
            `;
        } else {
            throw new Error(data.error || 'Failed to get answer');
        }
    } catch (err) {
        qaResponse.innerHTML = `<p>Error: ${escapeHTML(err.message)}</p>`;
    }
    
    questionInput.value = '';
}

// Utility Functions
function resetToUpload() {
    reportSection.style.display = 'none';
    uploadSection.style.display = 'block';
    fileInfo.style.display = 'none';
    selectedFile = null;
    fileInput.value = null;
    generateBtn.disabled = true;
    
    // Reset advanced options
    advancedAnalysisToggle.checked = false;
    analysisOptions.style.display = 'none';
    caseDescription.value = '';
    officerId.value = '';
    reportLanguage.value = 'en';
}

function resetUI() {
    progressSection.style.display = 'none';
    uploadSection.style.display = 'block';
    generateBtn.disabled = false;
    fileInfo.style.display = 'none';
    selectedFile = null;
    fileInput.value = null;
}

function formatDate(timestamp) {
    if (!timestamp) return 'Unknown date';
    
    try {
        const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (e) {
        return 'Invalid date';
    }
}

function showError(message) {
    alert(`Error: ${message}`);
}

function showSuccess(message) {
    alert(`Success: ${message}`);
}

function showLoading(message) {
    casesList.innerHTML = `<div class="case-item"><p>${message}</p></div>`;
}

async function checkSystemHealth() {
    try {
        const response = await fetch('/api/health');
        if (!response.ok) {
            console.warn('System health check failed');
        }
    } catch (err) {
        console.warn('Cannot connect to backend server');
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}