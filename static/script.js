// CyberSecure Blockchain Voting System - Client-side Logic

document.addEventListener('DOMContentLoaded', () => {
    // 1. Voting Form Logic
    const voteForm = document.getElementById('voteForm');
    if (voteForm) {
        voteForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitVoteBtn');
            const alertBox = document.getElementById('voteAlert');
            const aiReport = document.getElementById('aiReport');
            
            // Disable submit to prevent double submission
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Transaction...';
            
            alertBox.style.display = 'none';
            aiReport.style.display = 'none';
            
            const formData = new FormData(voteForm);
            
            try {
                const response = await fetch('/vote', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                // Display main response alert
                alertBox.style.display = 'block';
                if (response.ok && data.success) {
                    alertBox.className = 'alert-box alert-success';
                    alertBox.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${data.message}`;
                    voteForm.reset();
                } else {
                    alertBox.className = 'alert-box alert-danger';
                    alertBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${data.message || 'Verification Error occurred.'}`;
                }
                
                // Display AI analysis if returned
                if (data.analysis) {
                    aiReport.style.display = 'block';
                    document.getElementById('aiStatus').innerText = data.analysis.status;
                    
                    const scoreBadge = document.getElementById('aiScore');
                    const score = parseFloat(data.analysis.fraud_score);
                    scoreBadge.innerText = score.toFixed(2);
                    
                    // Style badges based on risk severity
                    if (data.analysis.status === 'BLOCKED' || score >= 0.8) {
                        scoreBadge.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
                        scoreBadge.style.color = '#ef4444';
                        scoreBadge.style.border = '1px solid rgba(239, 68, 68, 0.4)';
                    } else if (data.analysis.status === 'SUSPICIOUS' || score >= 0.4) {
                        scoreBadge.style.backgroundColor = 'rgba(245, 158, 11, 0.15)';
                        scoreBadge.style.color = '#f59e0b';
                        scoreBadge.style.border = '1px solid rgba(245, 158, 11, 0.4)';
                    } else {
                        scoreBadge.style.backgroundColor = 'rgba(16, 185, 129, 0.15)';
                        scoreBadge.style.color = '#10b981';
                        scoreBadge.style.border = '1px solid rgba(16, 185, 129, 0.4)';
                    }
                    
                    document.getElementById('aiExplanation').innerText = data.analysis.security_explanation;
                }
                
            } catch (err) {
                alertBox.style.display = 'block';
                alertBox.className = 'alert-box alert-danger';
                alertBox.innerHTML = `<i class="fa-solid fa-wifi"></i> Network error: Unable to contact voting server.`;
                console.error(err);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fa-solid fa-fingerprint"></i> Cast Vote Securely';
            }
        });
    }

    // 2. Admin Auth forms (Login & Register)
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const authAlert = document.getElementById('authAlert');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            authAlert.style.display = 'none';
            const formData = new FormData(loginForm);
            
            try {
                const response = await fetch('/admin/login', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (response.ok && data.success) {
                    authAlert.style.display = 'block';
                    authAlert.className = 'alert-box alert-success';
                    authAlert.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Login verified. Authenticating...';
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    authAlert.style.display = 'block';
                    authAlert.className = 'alert-box alert-danger';
                    authAlert.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> ${data.message || 'Login failed.'}`;
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            authAlert.style.display = 'none';
            const formData = new FormData(registerForm);
            
            try {
                const response = await fetch('/admin/register', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (response.ok && data.success) {
                    authAlert.style.display = 'block';
                    authAlert.className = 'alert-box alert-success';
                    authAlert.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${data.message} Please log in.`;
                    registerForm.reset();
                    switchAuthTab('login');
                } else {
                    authAlert.style.display = 'block';
                    authAlert.className = 'alert-box alert-danger';
                    authAlert.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> ${data.message || 'Registration failed.'}`;
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    // 3. Admin Dashboard Statistics & Polling
    const isDashboardPage = document.getElementById('blockchainContainer') !== null;
    if (isDashboardPage) {
        // Run initial load
        refreshDashboard();
        // Setup polling interval (every 5 seconds)
        setInterval(refreshDashboard, 5000);
    }
});

// Switch login/register tabs
function switchAuthTab(type) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabs = document.querySelectorAll('.auth-tab');
    const alertBox = document.getElementById('authAlert');
    
    if (alertBox) alertBox.style.display = 'none';

    if (type === 'login') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        tabs[0].classList.add('active');
        tabs[1].classList.remove('active');
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        tabs[0].classList.remove('active');
        tabs[1].classList.add('active');
    }
}

// Chart instance reference
let voteChart = null;

async function refreshDashboard() {
    try {
        const response = await fetch('/admin/stats');
        if (!response.ok) return;
        const data = await response.json();

        // A. Update Metrics
        document.getElementById('metricTotalVotes').innerText = data.total_votes;
        
        const integrityEl = document.getElementById('metricLedgerIntegrity');
        if (data.chain_valid) {
            integrityEl.innerHTML = '<i class="fa-solid fa-circle-check" style="color: var(--status-approved);"></i> Secure';
        } else {
            integrityEl.innerHTML = '<i class="fa-solid fa-circle-xmark" style="color: var(--status-blocked);"></i> Compromised';
        }

        const alertsEl = document.getElementById('metricSecurityAlerts');
        const suspiciousOrBlockedLogs = data.logs.filter(l => l.status === 'SUSPICIOUS' || l.status === 'BLOCKED');
        if (suspiciousOrBlockedLogs.length > 0) {
            alertsEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: var(--status-blocked);"></i> ${suspiciousOrBlockedLogs.length} Alerts`;
        } else {
            alertsEl.innerHTML = '<i class="fa-solid fa-circle-check" style="color: var(--status-approved);"></i> None';
        }

        // B. Update Chart
        const chartCanvas = document.getElementById('voteBreakdownChart');
        if (chartCanvas) {
            const chartData = {
                labels: Object.keys(data.breakdown),
                datasets: [{
                    data: Object.values(data.breakdown),
                    backgroundColor: ['#00e5ff', '#0088ff', '#9ca3af'],
                    borderColor: 'rgba(10, 15, 29, 0.8)',
                    borderWidth: 2
                }]
            };

            if (voteChart) {
                voteChart.data = chartData;
                voteChart.update();
            } else {
                voteChart = new Chart(chartCanvas, {
                    type: 'doughnut',
                    data: chartData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: {
                                    color: '#f3f4f6',
                                    font: { family: 'Outfit', size: 11 }
                                }
                            }
                        }
                    }
                });
            }
        }

        // C. Update Blockchain Visualizer Scroll
        const blockchainContainer = document.getElementById('blockchainContainer');
        if (blockchainContainer) {
            let chainHTML = '';
            data.blocks.forEach((block, idx) => {
                const date = new Date(parseInt(block.timestamp) * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                
                chainHTML += `
                    <div class="block-node">
                        <div class="block-node-header">
                            <span class="block-index">#Block ${block.block_index}</span>
                            <span class="block-time">${date}</span>
                        </div>
                        <div class="block-node-body">
                            <p>Voter: <span>${block.voter_id}</span></p>
                            <p>Vote: <span>${block.candidate}</span></p>
                            <p class="hash-label">Prev Hash:</p>
                            <p class="hash-val">${block.previous_hash.substring(0, 16)}...</p>
                            <p class="hash-label">Current Hash:</p>
                            <p class="hash-val">${block.hash.substring(0, 16)}...</p>
                        </div>
                    </div>
                `;
                
                // Add connector between nodes except after last node
                if (idx < data.blocks.length - 1) {
                    chainHTML += `
                        <div class="block-connector">
                            <i class="fa-solid fa-circle-arrow-right"></i>
                        </div>
                    `;
                }
            });
            blockchainContainer.innerHTML = chainHTML;
        }

        // D. Update Audit Logs Table
        const logsBody = document.getElementById('auditLogsBody');
        if (logsBody) {
            let logsHTML = '';
            data.logs.forEach(log => {
                let statusBadge = '';
                if (log.status === 'APPROVED') {
                    statusBadge = '<span class="badge-status badge-status-approved">APPROVED</span>';
                } else if (log.status === 'SUSPICIOUS') {
                    statusBadge = '<span class="badge-status badge-status-suspicious">SUSPICIOUS</span>';
                } else {
                    statusBadge = '<span class="badge-status badge-status-blocked">BLOCKED</span>';
                }
                
                // Convert UTC time to local readable representation
                const dateStr = new Date(log.timestamp).toLocaleString();
                
                logsHTML += `
                    <tr>
                        <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; white-space: nowrap;">${dateStr}</td>
                        <td style="font-weight: 600;">${log.voter_id}</td>
                        <td style="font-family: 'JetBrains Mono', monospace;">${log.ip_address}</td>
                        <td>
                            <strong style="font-family: 'JetBrains Mono', monospace; color: ${log.fraud_score >= 0.8 ? '#ef4444' : log.fraud_score >= 0.4 ? '#f59e0b' : '#10b981'}">
                                ${log.fraud_score.toFixed(2)}
                            </strong>
                        </td>
                        <td>${statusBadge}</td>
                        <td style="color: var(--text-secondary); max-width: 300px; overflow: hidden; text-overflow: ellipsis;" title="${log.security_explanation}">${log.security_explanation}</td>
                    </tr>
                `;
            });
            
            if (data.logs.length === 0) {
                logsHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-secondary);">No audits logged in system database.</td></tr>`;
            }
            logsBody.innerHTML = logsHTML;
        }

    } catch (err) {
        console.error("Dashboard refresh error: ", err);
    }
}
