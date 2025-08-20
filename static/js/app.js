// Global variables
let currentUser = null;
let accounts = [];
let transactions = [];
let authToken = null;

// API Configuration
const API_BASE = '/api';

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 4px;
        color: white;
        z-index: 3000;
        animation: slideInRight 0.3s ease;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// API functions
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...(authToken && { 'Authorization': `Bearer ${authToken}` })
        },
        ...options
    };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Authentication
async function login(email, password) {
    try {
        const data = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        await loadUserData();
        hideLoginModal();
        showNotification('Login realizado com sucesso!', 'success');
        
    } catch (error) {
        showNotification('Erro no login: ' + error.message, 'error');
    }
}

async function register(userData) {
    try {
        await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        showNotification('Registro realizado com sucesso! Faça login.', 'success');
        showLoginForm();
        
    } catch (error) {
        showNotification('Erro no registro: ' + error.message, 'error');
    }
}

async function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    showLoginModal();
    showNotification('Logout realizado com sucesso!', 'success');
}

async function loadUserData() {
    try {
        currentUser = await apiCall('/auth/me');
        document.getElementById('user-name').textContent = currentUser.full_name;
        
        await loadAccounts();
        await loadRecentTransactions();
        updateDashboard();
        
    } catch (error) {
        console.error('Error loading user data:', error);
        logout();
    }
}

// Account management
async function loadAccounts() {
    try {
        accounts = await apiCall('/accounts/');
        renderAccounts();
        updateAccountSelects();
        
    } catch (error) {
        showNotification('Erro ao carregar contas: ' + error.message, 'error');
    }
}

async function createAccount(accountData) {
    try {
        const newAccount = await apiCall('/accounts/', {
            method: 'POST',
            body: JSON.stringify(accountData)
        });
        
        accounts.push(newAccount);
        renderAccounts();
        updateAccountSelects();
        closeModal('create-account-modal');
        showNotification('Conta criada com sucesso!', 'success');
        
    } catch (error) {
        showNotification('Erro ao criar conta: ' + error.message, 'error');
    }
}

function renderAccounts() {
    const container = document.getElementById('accounts-list');
    
    if (accounts.length === 0) {
        container.innerHTML = '<p>Nenhuma conta encontrada. Crie sua primeira conta!</p>';
        return;
    }
    
    container.innerHTML = accounts.map(account => `
        <div class="account-card">
            <div class="account-header">
                <div>
                    <div class="account-type">${account.account_type === 'checking' ? 'Conta Corrente' : 'Poupança'}</div>
                    <div class="account-details">
                        Conta: ${account.account_number}<br>
                        Banco: ${account.bank_code} | Agência: ${account.branch_code}
                        ${account.pix_key ? `<br>PIX: ${account.pix_key}` : ''}
                    </div>
                </div>
                <div class="account-status ${account.is_active ? 'active' : 'inactive'}">
                    ${account.is_active ? 'Ativa' : 'Inativa'}
                </div>
            </div>
            <div class="account-balance">${formatCurrency(account.balance)}</div>
            <div class="account-actions">
                <button class="btn-primary btn-small" onclick="viewAccountDetails(${account.id})">
                    Ver Detalhes
                </button>
                <button class="btn-secondary btn-small" onclick="editAccount(${account.id})">
                    Editar
                </button>
            </div>
        </div>
    `).join('');
}

function updateAccountSelects() {
    const senderSelect = document.getElementById('sender-account');
    const receiverSelect = document.getElementById('receiver-account');
    
    const activeAccounts = accounts.filter(acc => acc.is_active);
    
    const options = activeAccounts.map(account => 
        `<option value="${account.id}">${account.account_number} - ${formatCurrency(account.balance)}</option>`
    ).join('');
    
    if (senderSelect) {
        senderSelect.innerHTML = '<option value="">Selecione uma conta</option>' + options;
    }
    
    if (receiverSelect) {
        receiverSelect.innerHTML = '<option value="">Selecione uma conta</option>' + options;
    }
}

// Transaction management
async function loadRecentTransactions() {
    try {
        transactions = await apiCall('/transactions/?limit=10');
        renderRecentTransactions();
        
    } catch (error) {
        showNotification('Erro ao carregar transações: ' + error.message, 'error');
    }
}

async function loadTransactionHistory(filters = {}) {
    try {
        const params = new URLSearchParams();
        
        if (filters.status) params.append('status', filters.status);
        if (filters.start_date) params.append('start_date', filters.start_date);
        if (filters.end_date) params.append('end_date', filters.end_date);
        
        const url = `/transactions/?${params.toString()}`;
        const data = await apiCall(url);
        
        renderTransactionHistory(data);
        
    } catch (error) {
        showNotification('Erro ao carregar histórico: ' + error.message, 'error');
    }
}

function renderRecentTransactions() {
    const container = document.getElementById('recent-transactions');
    
    if (transactions.length === 0) {
        container.innerHTML = '<p>Nenhuma transação encontrada.</p>';
        return;
    }
    
    container.innerHTML = transactions.slice(0, 5).map(transaction => `
        <div class="transaction-item">
            <div class="transaction-info">
                <div class="transaction-description">
                    ${transaction.description || 'Transferência'}
                </div>
                <div class="transaction-meta">
                    <span>${formatDate(transaction.created_at)}</span>
                    <span>${transaction.transaction_type.replace('_', ' ').toUpperCase()}</span>
                </div>
            </div>
            <div class="transaction-amount">
                <div class="amount-value ${transaction.sender_id === currentUser.id ? 'negative' : 'positive'}">
                    ${transaction.sender_id === currentUser.id ? '-' : '+'}${formatCurrency(transaction.amount)}
                </div>
                <div class="transaction-status status-${transaction.status}">
                    ${getStatusText(transaction.status)}
                </div>
            </div>
        </div>
    `).join('');
}

function renderTransactionHistory(transactions) {
    const container = document.getElementById('transaction-history');
    
    if (transactions.length === 0) {
        container.innerHTML = '<p>Nenhuma transação encontrada.</p>';
        return;
    }
    
    container.innerHTML = transactions.map(transaction => `
        <div class="transaction-item">
            <div class="transaction-info">
                <div class="transaction-description">
                    ${transaction.description || 'Transferência'}
                </div>
                <div class="transaction-meta">
                    <span>ID: ${transaction.transaction_id}</span>
                    <span>${formatDate(transaction.created_at)}</span>
                    <span>${transaction.transaction_type.replace('_', ' ').toUpperCase()}</span>
                </div>
            </div>
            <div class="transaction-amount">
                <div class="amount-value ${transaction.sender_id === currentUser.id ? 'negative' : 'positive'}">
                    ${transaction.sender_id === currentUser.id ? '-' : '+'}${formatCurrency(transaction.amount)}
                </div>
                <div class="transaction-status status-${transaction.status}">
                    ${getStatusText(transaction.status)}
                </div>
                ${transaction.status === 'pending' && transaction.sender_id === currentUser.id ? 
                    `<button class="btn-secondary btn-small" onclick="cancelTransaction('${transaction.transaction_id}')">Cancelar</button>` : ''
                }
            </div>
        </div>
    `).join('');
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'Pendente',
        'processing': 'Processando',
        'completed': 'Concluída',
        'failed': 'Falhou',
        'cancelled': 'Cancelada'
    };
    return statusMap[status] || status;
}

async function createTransfer(transferData) {
    try {
        const response = await apiCall('/transfers/instant', {
            method: 'POST',
            body: JSON.stringify(transferData)
        });
        
        showNotification('Transferência realizada com sucesso!', 'success');
        clearTransferForm();
        await loadAccounts();
        await loadRecentTransactions();
        updateDashboard();
        
    } catch (error) {
        showNotification('Erro na transferência: ' + error.message, 'error');
    }
}

async function cancelTransaction(transactionId) {
    try {
        await apiCall(`/transfers/${transactionId}/cancel`, {
            method: 'POST'
        });
        
        showNotification('Transferência cancelada com sucesso!', 'success');
        await loadTransactionHistory();
        
    } catch (error) {
        showNotification('Erro ao cancelar transferência: ' + error.message, 'error');
    }
}

// Dashboard
function updateDashboard() {
    // Update total balance
    const totalBalance = accounts.reduce((sum, account) => sum + parseFloat(account.balance), 0);
    document.getElementById('total-balance').textContent = formatCurrency(totalBalance);
    document.getElementById('account-count').textContent = `${accounts.length} conta${accounts.length !== 1 ? 's' : ''}`;
    
    // Update today's transactions
    const today = new Date().toDateString();
    const todayTransactions = transactions.filter(t => 
        new Date(t.created_at).toDateString() === today && t.sender_id === currentUser.id
    );
    
    const todayAmount = todayTransactions.reduce((sum, t) => sum + parseFloat(t.amount), 0);
    
    document.getElementById('today-transfers').textContent = todayTransactions.length;
    document.getElementById('today-amount').textContent = formatCurrency(todayAmount);
    
    // Update pending transactions
    const pendingTransactions = transactions.filter(t => 
        t.status === 'pending' && t.sender_id === currentUser.id
    );
    
    const pendingAmount = pendingTransactions.reduce((sum, t) => sum + parseFloat(t.amount), 0);
    
    document.getElementById('pending-transfers').textContent = pendingTransactions.length;
    document.getElementById('pending-amount').textContent = formatCurrency(pendingAmount);
}

// UI Management
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(`${sectionName}-section`).classList.add('active');
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    document.querySelector(`[onclick="showSection('${sectionName}')"]`).classList.add('active');
}

function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function showLoginModal() {
    showModal('login-modal');
}

function hideLoginModal() {
    closeModal('login-modal');
}

function showLoginForm() {
    closeModal('register-modal');
    showModal('login-modal');
}

function showRegisterForm() {
    closeModal('login-modal');
    showModal('register-modal');
}

function showCreateAccountForm() {
    showModal('create-account-modal');
}

function clearTransferForm() {
    document.getElementById('transfer-form').reset();
    document.querySelectorAll('.transfer-fields').forEach(field => {
        field.style.display = 'none';
    });
}

// QR Code generation
function generateQRCode() {
    // For demonstration purposes, we'll show a simple QR code
    // In a real implementation, you'd generate a PIX QR code
    const qrContainer = document.getElementById('qr-code-container');
    qrContainer.innerHTML = `
        <div style="width: 200px; height: 200px; background: #f0f0f0; border: 2px dashed #ccc; 
                    display: flex; align-items: center; justify-content: center; margin: 0 auto;">
            <div style="text-align: center; color: #666;">
                <i class="fas fa-qrcode" style="font-size: 3rem; margin-bottom: 0.5rem;"></i><br>
                QR Code PIX<br>
                <small>Implementação completa necessária</small>
            </div>
        </div>
    `;
    showModal('qr-modal');
}

// Export transactions
async function exportTransactions() {
    try {
        const params = new URLSearchParams();
        
        const startDate = document.getElementById('filter-start-date').value;
        const endDate = document.getElementById('filter-end-date').value;
        
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${API_BASE}/transactions/export/csv?${params.toString()}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to export transactions');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'transactions.csv';
        a.click();
        window.URL.revokeObjectURL(url);
        
        showNotification('Exportação realizada com sucesso!', 'success');
        
    } catch (error) {
        showNotification('Erro na exportação: ' + error.message, 'error');
    }
}

// Filter transactions
function filterTransactions() {
    const filters = {
        status: document.getElementById('filter-status').value,
        start_date: document.getElementById('filter-start-date').value,
        end_date: document.getElementById('filter-end-date').value
    };
    
    loadTransactionHistory(filters);
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Check for existing auth token
    const savedToken = localStorage.getItem('authToken');
    if (savedToken) {
        authToken = savedToken;
        loadUserData();
    } else {
        showLoginModal();
    }
    
    // Login form
    document.getElementById('login-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        await login(email, password);
    });
    
    // Register form
    document.getElementById('register-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        const userData = {
            email: document.getElementById('register-email').value,
            username: document.getElementById('register-username').value,
            full_name: document.getElementById('register-fullname').value,
            cpf: document.getElementById('register-cpf').value,
            password: document.getElementById('register-password').value
        };
        await register(userData);
    });
    
    // Create account form
    document.getElementById('create-account-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        const accountData = {
            account_type: document.getElementById('account-type').value,
            bank_code: document.getElementById('bank-code').value,
            branch_code: document.getElementById('branch-code').value,
            pix_key: document.getElementById('pix-key').value || null,
            pix_key_type: document.getElementById('pix-key-type').value || null
        };
        await createAccount(accountData);
        e.target.reset();
    });
    
    // Transfer form
    document.getElementById('transfer-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const transferType = document.getElementById('transfer-type').value;
        const senderAccountId = document.getElementById('sender-account').value;
        const amount = document.getElementById('transfer-amount').value.replace(/[^\d,]/g, '').replace(',', '.');
        
        if (!senderAccountId || !amount) {
            showNotification('Preencha todos os campos obrigatórios', 'error');
            return;
        }
        
        const transferData = {
            amount: parseFloat(amount),
            currency: 'BRL',
            description: document.getElementById('transfer-description').value,
            transaction_type: 'instant_transfer'
        };
        
        if (transferType === 'internal') {
            transferData.receiver_account_id = parseInt(document.getElementById('receiver-account').value);
        } else if (transferType === 'pix') {
            transferData.pix_key = document.getElementById('pix-key-input').value;
        } else if (transferType === 'external') {
            transferData.external_recipient_name = document.getElementById('recipient-name').value;
            transferData.external_recipient_account = document.getElementById('recipient-account').value;
            transferData.external_recipient_bank = document.getElementById('recipient-bank').value;
            transferData.external_recipient_document = document.getElementById('recipient-document').value;
        }
        
        // Add sender_account_id as query parameter
        const url = `/transfers/instant?sender_account_id=${senderAccountId}`;
        
        try {
            await apiCall(url, {
                method: 'POST',
                body: JSON.stringify(transferData)
            });
            
            showNotification('Transferência realizada com sucesso!', 'success');
            clearTransferForm();
            await loadAccounts();
            await loadRecentTransactions();
            updateDashboard();
            
        } catch (error) {
            showNotification('Erro na transferência: ' + error.message, 'error');
        }
    });
    
    // Transfer type change
    document.getElementById('transfer-type').addEventListener('change', function() {
        const transferType = this.value;
        
        // Hide all transfer fields
        document.querySelectorAll('.transfer-fields').forEach(field => {
            field.style.display = 'none';
        });
        
        // Show relevant fields
        if (transferType === 'internal') {
            document.getElementById('internal-transfer-fields').style.display = 'block';
        } else if (transferType === 'pix') {
            document.getElementById('pix-transfer-fields').style.display = 'block';
        } else if (transferType === 'external') {
            document.getElementById('external-transfer-fields').style.display = 'block';
        }
    });
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('href').substring(1);
            showSection(section);
            
            // Load section-specific data
            if (section === 'history') {
                loadTransactionHistory();
            }
        });
    });
    
    // Currency input formatting
    document.getElementById('transfer-amount').addEventListener('input', function(e) {
        let value = e.target.value.replace(/[^\d]/g, '');
        if (value) {
            value = (parseInt(value) / 100).toFixed(2);
            e.target.value = 'R$ ' + value.replace('.', ',');
        }
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key closes modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
});