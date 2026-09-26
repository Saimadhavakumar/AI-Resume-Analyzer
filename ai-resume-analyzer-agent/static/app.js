// app.js
// Frontend logic for AI Resume Analyzer web UI.

(function () {
    'use strict';

    // --- DOM Elements ---
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const removeFileBtn = document.getElementById('remove-file');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');

    const uploadSection = document.getElementById('upload-section');
    const processingSection = document.getElementById('processing-section');
    const resultsSection = document.getElementById('results-section');
    const errorSection = document.getElementById('error-section');
    const processingStatus = document.getElementById('processing-status');
    const progressFill = document.getElementById('progress-fill');
    const resultsMeta = document.getElementById('results-meta');
    const newAnalysisBtn = document.getElementById('new-analysis-btn');
    const retryBtn = document.getElementById('retry-btn');
    const errorMessage = document.getElementById('error-message');

    // --- State ---
    let selectedFile = null;

    // --- File size limits ---
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
    const ALLOWED_TYPES = ['.pdf', '.docx'];

    // --- Utility ---
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    function getFileExtension(name) {
        const idx = name.lastIndexOf('.');
        return idx >= 0 ? name.substring(idx).toLowerCase() : '';
    }

    function showSection(section) {
        [uploadSection, processingSection, resultsSection, errorSection].forEach(s => {
            s.classList.add('hidden');
        });
        section.classList.remove('hidden');
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // --- File Selection ---
    function handleFileSelect(file) {
        // Validate type
        const ext = getFileExtension(file.name);
        if (!ALLOWED_TYPES.includes(ext)) {
            alert(`Unsupported file type: "${ext}"\nPlease upload a PDF or DOCX file.`);
            return;
        }

        // Validate size
        if (file.size > MAX_FILE_SIZE) {
            alert(`File too large (${formatFileSize(file.size)}).\nMaximum allowed size is 10 MB.`);
            return;
        }

        if (file.size === 0) {
            alert('The selected file is empty. Please choose a valid resume file.');
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo.classList.remove('hidden');
        analyzeBtn.disabled = false;
    }

    function clearFile() {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.classList.add('hidden');
        analyzeBtn.disabled = true;
    }

    // --- Drag & Drop ---
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });

    // --- Processing Animation ---
    const PROCESSING_STEPS = [
        { text: 'Extracting text from document...', progress: 15 },
        { text: 'Cleaning and normalizing text...', progress: 30 },
        { text: 'Running NLP skill extraction...', progress: 45 },
        { text: 'Computing TF-IDF keyword analysis...', progress: 55 },
        { text: 'Sending to Ollama / Llama 3...', progress: 70 },
        { text: 'Waiting for LLM analysis...', progress: 85 },
        { text: 'Parsing structured results...', progress: 95 },
    ];

    let processingInterval = null;

    function startProcessingAnimation() {
        let step = 0;
        progressFill.style.width = '5%';
        processingStatus.textContent = PROCESSING_STEPS[0].text;

        processingInterval = setInterval(() => {
            step++;
            if (step < PROCESSING_STEPS.length) {
                processingStatus.textContent = PROCESSING_STEPS[step].text;
                progressFill.style.width = PROCESSING_STEPS[step].progress + '%';
            }
        }, 2500);
    }

    function stopProcessingAnimation() {
        if (processingInterval) {
            clearInterval(processingInterval);
            processingInterval = null;
        }
        progressFill.style.width = '100%';
    }

    // --- Analysis ---
    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // Switch to processing view
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        analyzeBtn.disabled = true;

        showSection(processingSection);
        startProcessingAnimation();

        // Prepare FormData
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData,
            });

            stopProcessingAnimation();

            const data = await response.json();

            if (!response.ok || data.error) {
                const msg = data.error || 'An unexpected error occurred.';
                const detail = data.detail || '';
                showError(msg + (detail ? '\n' + detail : ''));
                return;
            }

            renderResults(data);
            showSection(resultsSection);

        } catch (err) {
            stopProcessingAnimation();
            showError(
                'Could not connect to the analysis server. ' +
                'Please make sure the server is running and try again.\n\n' +
                'Error: ' + err.message
            );
        } finally {
            // Reset button state
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    // --- Error Display ---
    function showError(message) {
        errorMessage.textContent = message;
        showSection(errorSection);
    }

    retryBtn.addEventListener('click', () => {
        showSection(uploadSection);
    });

    // --- New Analysis ---
    newAnalysisBtn.addEventListener('click', () => {
        clearFile();
        showSection(uploadSection);
    });

    // --- Results Rendering ---
    function renderResults(data) {
        const llm = data.llm_analysis || {};
        const nlp = data.nlp_analysis || {};

        // Meta info
        resultsMeta.textContent =
            `${data.filename} · ${data.text_stats?.word_count || 0} words · ` +
            `Processed in ${data.processing_time_seconds}s`;

        // Score cards
        renderScoreCards(data);

        // Summary
        renderTextCard('summary-content', llm.summary);

        // Skills (combined NLP + LLM)
        renderSkills(llm.skills, nlp.skills_detected);

        // Strengths
        renderListCard('strengths-content', llm.strengths);

        // Weaknesses
        renderListCard('weaknesses-content', llm.weaknesses);

        // Experience
        renderAnalysisCard('experience-content', llm.experience_analysis);

        // Projects
        renderProjectsCard('projects-content', llm.projects_analysis);

        // Education
        renderTextCard('education-content', llm.education);

        // Certifications
        renderListCard('certifications-content', llm.certifications);

        // Improvement suggestions
        renderListCard('improvements-content', llm.improvement_suggestions);

        // ATS observations
        renderListCard('ats-content', llm.ats_observations);

        // Suggested roles
        renderRoles('roles-content', llm.suggested_roles);

        // TF-IDF keywords
        renderTfidf('tfidf-content', nlp.tfidf_keywords);
    }

    function renderScoreCards(data) {
        const container = document.getElementById('score-cards');
        container.innerHTML = '';

        const nlp = data.nlp_analysis || {};
        const sim = nlp.similarity_score || {};
        const skills = nlp.skills_detected || {};
        const llm = data.llm_analysis || {};

        const cards = [];

        // Keyword relevance score
        if (sim.score !== null && sim.score !== undefined) {
            const pct = (sim.score * 100).toFixed(0);
            cards.push({
                label: 'Keyword Relevance',
                value: sim.percentage || pct + '%',
                cls: parseFloat(pct) >= 50 ? 'success' : parseFloat(pct) >= 30 ? 'warning' : 'accent',
                detail: `${sim.matched_keywords?.length || 0}/${(sim.matched_keywords?.length || 0) + (sim.missing_keywords?.length || 0)} target keywords matched`,
            });
        }

        // Skills count
        const skillCount = skills.all_skills?.length || 0;
        if (skillCount > 0) {
            cards.push({
                label: 'Skills Detected',
                value: skillCount,
                cls: 'info',
                detail: 'Via NLP pattern matching',
            });
        }

        // Word count
        cards.push({
            label: 'Word Count',
            value: data.text_stats?.word_count || 0,
            cls: 'accent',
            detail: `${data.text_stats?.raw_characters || 0} characters extracted`,
        });

        // Processing time
        cards.push({
            label: 'Analysis Time',
            value: data.processing_time_seconds + 's',
            cls: 'accent',
            detail: 'Total processing time',
        });

        cards.forEach((card, i) => {
            const el = document.createElement('div');
            el.className = 'score-card';
            el.style.animationDelay = (i * 0.1) + 's';
            el.innerHTML = `
                <span class="score-label">${card.label}</span>
                <span class="score-value ${card.cls}">${card.value}</span>
                <span class="score-detail">${card.detail}</span>
            `;
            container.appendChild(el);
        });
    }

    function renderTextCard(containerId, text) {
        const el = document.getElementById(containerId);
        if (!text || (typeof text === 'string' && !text.trim())) {
            el.innerHTML = '<p style="color: var(--text-muted);">No data available.</p>';
            return;
        }
        el.innerHTML = `<p>${escapeHtml(text)}</p>`;
    }

    function renderListCard(containerId, items) {
        const el = document.getElementById(containerId);
        if (!items || !Array.isArray(items) || items.length === 0) {
            el.innerHTML = '<p style="color: var(--text-muted);">No data available.</p>';
            return;
        }
        el.innerHTML = '<ul>' + items.map(item => `<li>${escapeHtml(item)}</li>`).join('') + '</ul>';
    }

    function renderSkills(llmSkills, nlpSkills) {
        const el = document.getElementById('skills-content');
        let html = '';

        // Merge LLM and NLP categorized skills
        const categories = {};

        // NLP-detected skills (regex-based)
        if (nlpSkills?.categorized) {
            for (const [cat, skills] of Object.entries(nlpSkills.categorized)) {
                if (skills.length > 0) {
                    categories[cat] = { skills: [...skills], source: 'nlp' };
                }
            }
        }

        // LLM-detected skills
        if (llmSkills && typeof llmSkills === 'object') {
            const llmCategoryMap = {
                'programming_languages': 'Programming Languages',
                'frameworks_libraries': 'Frameworks & Libraries',
                'databases': 'Databases',
                'cloud_devops': 'Cloud & DevOps',
                'ai_ml': 'AI & ML',
                'tools': 'Tools & Platforms',
                'other': 'Other',
            };

            for (const [key, skills] of Object.entries(llmSkills)) {
                if (Array.isArray(skills) && skills.length > 0) {
                    const catName = llmCategoryMap[key] || key;
                    if (!categories[catName]) {
                        categories[catName] = { skills: [], source: 'llm' };
                    }
                    skills.forEach(s => {
                        if (!categories[catName].skills.includes(s)) {
                            categories[catName].skills.push(s);
                        }
                    });
                }
            }
        }

        if (Object.keys(categories).length === 0) {
            el.innerHTML = '<p style="color: var(--text-muted);">No skills detected.</p>';
            return;
        }

        for (const [cat, data] of Object.entries(categories)) {
            html += `
                <div class="skill-category">
                    <div class="skill-category-name">${escapeHtml(cat)}</div>
                    <div class="skill-tags">
                        ${data.skills.map(s =>
                            `<span class="skill-tag${data.source === 'nlp' ? ' nlp-detected' : ''}">${escapeHtml(s)}</span>`
                        ).join('')}
                    </div>
                </div>
            `;
        }

        // Method note
        if (nlpSkills?.method) {
            html += `<div class="method-note">${escapeHtml(nlpSkills.method)}</div>`;
        }

        el.innerHTML = html;
    }

    function renderAnalysisCard(containerId, analysis) {
        const el = document.getElementById(containerId);
        if (!analysis || typeof analysis !== 'object') {
            el.innerHTML = '<p style="color: var(--text-muted);">No data available.</p>';
            return;
        }

        let html = '';
        const labelMap = {
            'relevance': 'Relevance',
            'clarity': 'Clarity',
            'impact': 'Impact',
            'technical_depth': 'Technical Depth',
            'measurable_achievements': 'Achievements',
        };

        for (const [key, value] of Object.entries(analysis)) {
            if (typeof value === 'string' && value.trim()) {
                const label = labelMap[key] || key.replace(/_/g, ' ');
                html += `
                    <div class="analysis-item">
                        <span class="analysis-label">${escapeHtml(label)}</span>
                        <span class="analysis-value">${escapeHtml(value)}</span>
                    </div>
                `;
            }
        }

        el.innerHTML = html || '<p style="color: var(--text-muted);">No data available.</p>';
    }

    function renderProjectsCard(containerId, analysis) {
        const el = document.getElementById(containerId);
        if (!analysis || typeof analysis !== 'object') {
            el.innerHTML = '<p style="color: var(--text-muted);">No data available.</p>';
            return;
        }

        let html = '';
        const labelMap = {
            'technical_relevance': 'Technical Relevance',
            'technologies_used': 'Technologies Used',
            'clarity': 'Clarity',
            'measurable_impact': 'Measurable Impact',
            'engineering_ability': 'Engineering Ability',
        };

        for (const [key, value] of Object.entries(analysis)) {
            const label = labelMap[key] || key.replace(/_/g, ' ');
            if (Array.isArray(value)) {
                if (value.length > 0) {
                    html += `
                        <div class="analysis-item">
                            <span class="analysis-label">${escapeHtml(label)}</span>
                            <span class="analysis-value">${value.map(v => escapeHtml(v)).join(', ')}</span>
                        </div>
                    `;
                }
            } else if (typeof value === 'string' && value.trim()) {
                html += `
                    <div class="analysis-item">
                        <span class="analysis-label">${escapeHtml(label)}</span>
                        <span class="analysis-value">${escapeHtml(value)}</span>
                    </div>
                `;
            }
        }

        el.innerHTML = html || '<p style="color: var(--text-muted);">No data available.</p>';
    }

    function renderRoles(containerId, roles) {
        const el = document.getElementById(containerId);
        if (!roles || !Array.isArray(roles) || roles.length === 0) {
            el.innerHTML = '<p style="color: var(--text-muted);">No roles suggested.</p>';
            return;
        }

        el.innerHTML = `
            <div class="skill-tags">
                ${roles.map(r => `<span class="skill-tag">${escapeHtml(r)}</span>`).join('')}
            </div>
        `;
    }

    function renderTfidf(containerId, tfidf) {
        const el = document.getElementById(containerId);
        if (!tfidf || !tfidf.keywords || tfidf.keywords.length === 0) {
            el.innerHTML = '<p style="color: var(--text-muted);">No keyword analysis available.</p>';
            return;
        }

        const maxScore = tfidf.keywords[0][1] || 1;
        let html = '<div class="keyword-bar-container">';

        tfidf.keywords.slice(0, 15).forEach(([keyword, score]) => {
            const widthPct = Math.max((score / maxScore) * 100, 4);
            html += `
                <div class="keyword-bar">
                    <span class="keyword-name">${escapeHtml(keyword)}</span>
                    <div class="keyword-track">
                        <div class="keyword-fill" style="width: ${widthPct}%"></div>
                    </div>
                    <span class="keyword-score">${score.toFixed(3)}</span>
                </div>
            `;
        });

        html += '</div>';

        if (tfidf.method) {
            html += `<div class="method-note">${escapeHtml(tfidf.method)}</div>`;
        }

        el.innerHTML = html;

        // Animate bars on render
        requestAnimationFrame(() => {
            el.querySelectorAll('.keyword-fill').forEach(bar => {
                const target = bar.style.width;
                bar.style.width = '0%';
                requestAnimationFrame(() => {
                    bar.style.width = target;
                });
            });
        });
    }

    function escapeHtml(str) {
        if (typeof str !== 'string') return String(str);
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

})();
