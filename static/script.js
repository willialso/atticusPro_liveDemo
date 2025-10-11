// Atticus Professional v17.0 - Complete Interactive Demo
class AttticusProfessionalDemo {
    constructor() {
        this.currentStep = 1;
        this.portfolioAnalysis = null;
        this.selectedStrategy = null;
        this.marketData = null;
        
        this.init();
    }
    
    init() {
        this.loadMarketData();
        this.loadPlatformExposure();
        this.setupEventListeners();
        
        // Update data every 30 seconds
        setInterval(() => {
            this.loadMarketData();
            this.loadPlatformExposure();
        }, 30000);
    }
    
    setupEventListeners() {
        // Contact form
        document.getElementById('contact-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleContactSubmit(e);
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideContact();
                this.hideLoading();
            }
        });
    }
    
    async loadMarketData() {
        try {
            const response = await fetch('/api/market-data');
            const data = await response.json();
            
            this.marketData = data;
            this.updateMarketDisplay(data);
        } catch (error) {
            console.error('Market data error:', error);
            this.updateMarketDisplay({
                btc_price: 'Error',
                volatility: 'N/A',
                risk_free_rate: 4.75
            });
        }
    }
    
    updateMarketDisplay(data) {
        const btcPrice = document.getElementById('btc-price');
        const volatility = document.getElementById('volatility');
        
        if (btcPrice) {
            btcPrice.textContent = typeof data.btc_price === 'number' 
                ? `$${data.btc_price.toLocaleString()}` 
                : data.btc_price;
        }
        
        if (volatility) {
            volatility.textContent = typeof data.volatility === 'number'
                ? `${data.volatility}%`
                : data.volatility;
        }
    }
    
    async loadPlatformExposure() {
        try {
            const response = await fetch('/api/platform-exposure');
            const data = await response.json();
            
            if (data.success) {
                this.updateExposureDisplay(data.exposure);
            }
        } catch (error) {
            console.error('Platform exposure error:', error);
        }
    }
    
    updateExposureDisplay(exposure) {
        const elements = {
            'client-exposure': exposure.total_client_long_btc || 0,
            'platform-hedges': exposure.total_platform_hedges_btc || 0,
            'platform-net': exposure.net_exposure_btc || 0,
            'net-exposure': exposure.net_exposure_btc || 0,
            'coverage-ratio': exposure.hedge_coverage_ratio 
                ? `${(exposure.hedge_coverage_ratio * 100).toFixed(1)}%`
                : 'N/A'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = typeof value === 'number' && id !== 'coverage-ratio'
                    ? `${value.toFixed(2)} BTC`
                    : value;
            }
        });
    }
    
    showStep(stepNumber) {
        // Hide all steps
        document.querySelectorAll('.workflow-step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show target step
        const targetStep = document.getElementById(`step-${stepNumber}`);
        if (targetStep) {
            targetStep.classList.add('active');
        }
        
        this.currentStep = stepNumber;
    }
    
    async analyzePortfolio(portfolioType) {
        this.showLoading('Analyzing institutional portfolio...');
        
        try {
            const response = await fetch('/api/analyze-portfolio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: portfolioType })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.portfolioAnalysis = data.analysis;
                this.displayAnalysisResults(data.analysis);
                this.showStep(2);
            } else {
                alert('Error analyzing portfolio: ' + data.error);
            }
        } catch (error) {
            console.error('Portfolio analysis error:', error);
            alert('Error analyzing portfolio. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    async analyzeCustomPosition() {
        const size = document.getElementById('custom-size').value;
        const type = document.getElementById('custom-type').value;
        
        if (!size || size <= 0) {
            alert('Please enter a valid BTC position size.');
            return;
        }
        
        this.showLoading('Analyzing custom position...');
        
        try {
            const response = await fetch('/api/analyze-portfolio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    custom_params: { size: parseFloat(size), type: type }
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.portfolioAnalysis = data.analysis;
                this.displayAnalysisResults(data.analysis);
                this.showStep(2);
            } else {
                alert('Error analyzing position: ' + data.error);
            }
        } catch (error) {
            console.error('Custom analysis error:', error);
            alert('Error analyzing position. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    displayAnalysisResults(analysis) {
        const container = document.getElementById('analysis-results');
        
        const html = `
            <div class="analysis-card">
                <h4>Portfolio Overview</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Institution:</span>
                        <span class="metric-value">${analysis.profile.name}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">BTC Position:</span>
                        <span class="metric-value">${analysis.positions.btc_size} BTC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Position Value:</span>
                        <span class="metric-value">$${analysis.positions.btc_value.toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Current BTC Price:</span>
                        <span class="metric-value">$${analysis.positions.current_price.toLocaleString()}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Risk Analysis</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">1-Day VaR (95%):</span>
                        <span class="metric-value">$${analysis.risk_metrics.var_1d_95.toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">30-Day VaR (95%):</span>
                        <span class="metric-value">$${analysis.risk_metrics.var_30d_95.toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Annual Volatility:</span>
                        <span class="metric-value">${(analysis.risk_metrics.volatility * 100).toFixed(1)}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Max Drawdown (30%):</span>
                        <span class="metric-value">$${analysis.risk_metrics.max_drawdown_30pct.toLocaleString()}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Scenario Analysis</h4>
                <div class="risk-scenarios">
                    ${analysis.scenarios.filter(s => s.change_pct < 0).map(scenario => `
                        <div class="scenario-card">
                            <h5>${scenario.change_pct}% BTC Decline</h5>
                            <div class="scenario-value">$${Math.abs(scenario.pnl).toLocaleString()}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Hedge Recommendation</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Recommended Strategy:</span>
                        <span class="metric-value">${analysis.hedge_recommendation.strategy.replace('_', ' ').toUpperCase()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Hedge Ratio:</span>
                        <span class="metric-value">${(analysis.hedge_recommendation.hedge_ratio * 100).toFixed(0)}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Hedge Size:</span>
                        <span class="metric-value">${analysis.hedge_recommendation.hedge_size_btc} BTC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Risk Tolerance:</span>
                        <span class="metric-value">${analysis.profile.risk_tolerance?.toUpperCase() || 'MODERATE'}</span>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        document.getElementById('generate-strategy-btn').style.display = 'block';
    }
    
    async generateStrategy() {
        this.showLoading('Generating hedging strategy with real Black-Scholes pricing...');
        
        try {
            const response = await fetch('/api/generate-strategy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    strategy_type: this.portfolioAnalysis.hedge_recommendation.strategy
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.selectedStrategy = data.strategy;
                this.displayStrategyResults(data.strategy);
                this.showStep(3);
            } else {
                alert('Error generating strategy: ' + data.error);
            }
        } catch (error) {
            console.error('Strategy generation error:', error);
            alert('Error generating strategy. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    displayStrategyResults(strategy) {
        const container = document.getElementById('strategy-results');
        
        const html = `
            <div class="analysis-card">
                <h4>${strategy.strategy_name}</h4>
                <p style="color: var(--text-light); margin-bottom: 24px;">
                    Professional ${strategy.strategy_type.replace('_', ' ')} strategy with institutional-grade pricing and execution.
                </p>
                
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Position Size:</span>
                        <span class="metric-value">${strategy.position_size} BTC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Strike Price:</span>
                        <span class="metric-value">$${(strategy.strike_price || strategy.protection_level).toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Time to Expiry:</span>
                        <span class="metric-value">${strategy.time_to_expiry_days} days</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Cost Percentage:</span>
                        <span class="metric-value">${strategy.cost_percentage}%</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Pricing Breakdown</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Base Premium:</span>
                        <span class="metric-value">$${(strategy.base_premium_total || strategy.net_premium_base || 0).toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Platform Markup:</span>
                        <span class="metric-value">$${strategy.platform_markup.toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Execution Fee:</span>
                        <span class="metric-value">$${strategy.execution_fee}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Total Client Cost:</span>
                        <span class="metric-value">$${strategy.total_client_cost.toLocaleString()}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Strategy Outcomes</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Maximum Loss:</span>
                        <span class="metric-value">$${(strategy.max_loss || 0).toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Break-Even Price:</span>
                        <span class="metric-value">$${(strategy.breakeven || strategy.break_even || 0).toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Protection Level:</span>
                        <span class="metric-value">$${(strategy.protection_level || strategy.strike_price || 0).toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Platform Revenue:</span>
                        <span class="metric-value">$${strategy.platform_revenue.toLocaleString()}</span>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 32px;">
                <button class="cta-btn" onclick="demo.executeStrategy()">
                    Execute Strategy →
                </button>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    async executeStrategy() {
        this.showLoading('Executing strategy via institutional channels...');
        
        try {
            const response = await fetch('/api/execute-strategy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayExecutionResults(data.execution);
                this.showStep(4);
                
                // Update platform exposure display
                this.loadPlatformExposure();
            } else {
                alert('Error executing strategy: ' + data.error);
            }
        } catch (error) {
            console.error('Execution error:', error);
            alert('Error executing strategy. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    displayExecutionResults(execution) {
        const container = document.getElementById('execution-results');
        
        const html = `
            <div class="analysis-card" style="background: rgba(22, 163, 74, 0.1); border-color: rgba(22, 163, 74, 0.3);">
                <h4>✅ Execution Completed</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Status:</span>
                        <span class="metric-value">${execution.execution_summary.status.toUpperCase()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Contracts Filled:</span>
                        <span class="metric-value">${execution.execution_summary.contracts_filled} BTC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Total Premium:</span>
                        <span class="metric-value">$${execution.execution_summary.total_premium_client.toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Platform Revenue:</span>
                        <span class="metric-value">$${execution.execution_summary.platform_revenue.toLocaleString()}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Portfolio Impact</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Institution:</span>
                        <span class="metric-value">${execution.portfolio_impact.institution}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">VaR Before:</span>
                        <span class="metric-value">$${execution.portfolio_impact.var_reduction.before.toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">VaR After:</span>
                        <span class="metric-value">$${execution.portfolio_impact.var_reduction.after.toLocaleString()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Risk Reduction:</span>
                        <span class="metric-value" style="color: var(--success);">${execution.portfolio_impact.var_reduction.reduction_pct}%</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Platform Exposure Management</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Total Client Positions:</span>
                        <span class="metric-value">${execution.platform_exposure.client_positions_btc.toFixed(2)} BTC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Platform Hedges:</span>
                        <span class="metric-value">${execution.platform_exposure.platform_hedges_btc.toFixed(2)} BTC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Net Exposure:</span>
                        <span class="metric-value">${execution.platform_exposure.net_exposure_btc.toFixed(2)} BTC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Hedge Action:</span>
                        <span class="metric-value">${execution.platform_exposure.platform_hedge_action.status.toUpperCase()}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Execution Venues</h4>
                <div style="display: grid; gap: 12px;">
                    ${execution.execution_summary.execution_venues.map(venue => `
                        <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255,255,255,0.05); border-radius: 6px;">
                            <span>${venue.exchange.toUpperCase()}</span>
                            <span>${venue.size} BTC (${venue.liquidity} liquidity)</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    resetDemo() {
        this.currentStep = 1;
        this.portfolioAnalysis = null;
        this.selectedStrategy = null;
        
        this.showStep(1);
        
        // Reset form inputs
        document.getElementById('custom-size').value = '';
        document.getElementById('generate-strategy-btn').style.display = 'none';
        
        // Clear results
        document.getElementById('analysis-results').innerHTML = '';
        document.getElementById('strategy-results').innerHTML = '';
        document.getElementById('execution-results').innerHTML = '';
    }
    
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.demo-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Update navigation
        document.querySelectorAll('.nav-step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show target section and update nav
        const targetSection = document.getElementById(`${sectionName}-section`);
        const targetNav = document.querySelector(`[data-section="${sectionName}"]`);
        
        if (targetSection) targetSection.classList.add('active');
        if (targetNav) targetNav.classList.add('active');
    }
    
    showContact() {
        document.getElementById('contact-modal').style.display = 'block';
    }
    
    hideContact() {
        document.getElementById('contact-modal').style.display = 'none';
    }
    
    showLoading(message = 'Processing...') {
        const overlay = document.getElementById('loading');
        const text = document.getElementById('loading-text');
        
        if (text) text.textContent = message;
        overlay.classList.add('active');
    }
    
    hideLoading() {
        document.getElementById('loading').classList.remove('active');
    }
    
    handleContactSubmit(e) {
        e.preventDefault();
        
        this.showLoading('Sending demo request...');
        
        // Simulate API call
        setTimeout(() => {
            this.hideLoading();
            this.hideContact();
            alert('Thank you! Our institutional team will contact you within 24 hours.');
            e.target.reset();
        }, 2000);
    }
}

// Global functions for onclick handlers
function showSection(section) {
    demo.showSection(section);
}

function analyzePortfolio(type) {
    demo.analyzePortfolio(type);
}

function analyzeCustomPosition() {
    demo.analyzeCustomPosition();
}

function generateStrategy() {
    demo.generateStrategy();
}

function resetDemo() {
    demo.resetDemo();
}

function showContact() {
    demo.showContact();
}

function hideContact() {
    demo.hideContact();
}

// Initialize demo
let demo;

document.addEventListener('DOMContentLoaded', function() {
    demo = new AttticusProfessionalDemo();
    
    // Modal click outside to close
    document.getElementById('contact-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            hideContact();
        }
    });
});
