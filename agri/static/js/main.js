// ========================================
// Weather Insights Dynamic Functionality
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // REFRESH INDIVIDUAL CROP INSIGHTS
    // ========================================
    const refreshButtons = document.querySelectorAll('.refresh-insight');
    
    refreshButtons.forEach(button => {
        button.addEventListener('click', function() {
            const cropName = this.dataset.crop;
            const card = this.closest('.crop-insight-card');
            const insightBody = card.querySelector('.insight-body');
            
            // Show loading state
            this.innerHTML = '⏳ Loading...';
            this.disabled = true;
            insightBody.style.opacity = '0.5';
            
            // Fetch updated insight from API
            fetch(`/api/crop-insight/${cropName}/`)
                .then(response => {
                    if (!response.ok) throw new Error('Network error');
                    return response.json();
                })
                .then(data => {
                    // Update the card with new insights
                    updateCropInsightCard(insightBody, data.insights);
                    
                    // Reset button
                    this.innerHTML = '🔄 Refresh Insight';
                    this.disabled = false;
                    insightBody.style.opacity = '1';
                    
                    // Show success toast
                    showToast('Insight updated successfully!', 'success');
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.innerHTML = '🔄 Refresh Insight';
                    this.disabled = false;
                    insightBody.style.opacity = '1';
                    showToast('Failed to update insight', 'error');
                });
        });
    });
    
    // ========================================
    // SMOOTH ALERT ANIMATIONS
    // ========================================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert, index) => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                alert.style.transition = 'all 0.4s ease';
                alert.style.opacity = '1';
                alert.style.transform = 'translateY(0)';
            }, 50);
        }, index * 100);
    });
});


// ========================================
// UPDATE CROP INSIGHT CARD CONTENT
// ========================================
function updateCropInsightCard(insightBody, insights) {
    insightBody.innerHTML = '';
    
    insights.slice(0, 2).forEach(insight => {
        const insightHTML = `
            <div class="insight-item mb-3 alert alert-${insight.type}" role="alert">
                <div class="d-flex align-items-start">
                    <span class="insight-icon me-2">${insight.icon}</span>
                    <div class="flex-grow-1">
                        <strong class="d-block">${insight.message}</strong>
                        <small class="text-muted mt-1 d-block">💡 ${insight.action}</small>
                    </div>
                </div>
            </div>
        `;
        insightBody.innerHTML += insightHTML;
    });
}


// ========================================
// TOAST NOTIFICATION
// ========================================
function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.textContent = message;
    
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 9999;
        font-weight: 500;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);