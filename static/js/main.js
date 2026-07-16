document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('statusText');
    const statsSection = document.getElementById('statsSection');
    const resultsSection = document.getElementById('resultsSection');
    const resultsTableBody = document.getElementById('resultsTableBody');
    const searchBtn = document.querySelector('.search-btn');

    let currentTaskId = null;
    let pollInterval = null;

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (!query) return;

        // Reset UI
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Searching...';
        progressSection.classList.remove('d-none');
        statsSection.classList.add('d-none');
        resultsSection.classList.add('d-none');
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
        progressBar.classList.add('progress-bar-animated');
        resultsTableBody.innerHTML = '';
        statusText.textContent = 'Initiating search...';

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            
            if (data.task_id) {
                currentTaskId = data.task_id;
                startPolling(currentTaskId);
            }
        } catch (error) {
            console.error('Search error:', error);
            statusText.textContent = 'Error starting search. Check console.';
            resetSearchBtn();
        }
    });

    function startPolling(taskId) {
        if (pollInterval) clearInterval(pollInterval);
        
        pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/status/${taskId}`);
                if (response.status === 404) {
                    clearInterval(pollInterval);
                    return;
                }
                const data = await response.json();
                
                // Update Progress
                progressBar.style.width = `${data.progress}%`;
                progressBar.textContent = `${data.progress}%`;
                statusText.textContent = data.status;

                if (data.progress === 100) {
                    clearInterval(pollInterval);
                    progressBar.classList.remove('progress-bar-animated');
                    resetSearchBtn();
                    
                    if (data.result) {
                        renderResults(data.result);
                        updateStats(data.result);
                        
                        // Setup export buttons
                        document.getElementById('exportCompanies').onclick = () => {
                            window.location.href = `/api/export/${taskId}?format=companies`;
                        };
                        document.getElementById('exportExcel').onclick = () => {
                            window.location.href = `/api/export/${taskId}?format=excel`;
                        };
                        document.getElementById('exportCsv').onclick = () => {
                            window.location.href = `/api/export/${taskId}?format=csv`;
                        };
                    } else if (data.error) {
                        statusText.textContent = `Failed: ${data.error}`;
                        progressBar.classList.add('bg-danger');
                    }
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, 1000);
    }

    function renderResults(leads) {
        resultsTableBody.innerHTML = '';
        
        leads.forEach(lead => {
            const tr = document.createElement('tr');
            
            let websiteHtml = lead.Website ? `<a href="${lead.Website}" target="_blank" class="text-info text-decoration-none"><i class="fa-solid fa-link"></i> Link</a>` : '-';
            
            let scoreClass = 'score-low';
            if (lead['Lead Score'] >= 70) scoreClass = 'score-high';
            else if (lead['Lead Score'] >= 40) scoreClass = 'score-medium';
            
            let metaHtml = lead['Meta Ads (Yes/No)'] === 'Yes' ? '<span class="badge bg-success"><i class="fa-brands fa-meta me-1"></i>Yes</span>' : '<span class="badge bg-secondary">No</span>';

            tr.innerHTML = `
                <td class="fw-semibold text-white">${lead['Company Name']}</td>
                <td class="text-muted"><small>${lead['Category']}</small></td>
                <td>${websiteHtml}</td>
                <td>${lead['Phone'] || '-'}</td>
                <td>${lead['Email'] ? `<a href="mailto:${lead['Email'].split(',')[0]}" class="text-decoration-none text-light">${lead['Email'].split(',')[0]}</a>` : '-'}</td>
                <td>${metaHtml}</td>
                <td>${lead['Google Rating'] > 0 ? `<i class="fa-solid fa-star text-warning me-1"></i>${lead['Google Rating']} <small class="text-muted">(${lead['Reviews']})</small>` : '-'}</td>
                <td><span class="score-badge ${scoreClass}">${lead['Lead Score']}/100</span></td>
            `;
            resultsTableBody.appendChild(tr);
        });
        
        resultsSection.classList.remove('d-none');
    }

    function updateStats(leads) {
        document.getElementById('statTotal').textContent = leads.length;
        
        const validLeads = leads.filter(l => l['Phone'] || l['Email']).length;
        document.getElementById('statValid').textContent = validLeads;
        
        const metaAds = leads.filter(l => l['Meta Ads (Yes/No)'] === 'Yes').length;
        document.getElementById('statMeta').textContent = metaAds;
        
        const avgScore = leads.length > 0 ? Math.round(leads.reduce((sum, l) => sum + l['Lead Score'], 0) / leads.length) : 0;
        document.getElementById('statScore').textContent = avgScore;
        
        statsSection.classList.remove('d-none');
    }

    function resetSearchBtn() {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fa-solid fa-magnifying-glass me-2"></i>Find Companies';
    }
});
