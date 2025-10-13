// Atticus Professional v17.3 - CFO Feedback Implementation
class AttticusProfessionalDemo {
    constructor() {
        this.currentStep = 1;
        this.portfolioAnalysis = null;
        this.availableStrategies = null;
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
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
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
                risk_free_rate: 5
            });
        }
    }
    
    // NO DECIMAL POINTS - CFO REQUEST
    formatCurrency(value) {
        if (typeof value !== 'number') return value;
        return `$${Math.round(value).toLocaleString()}`;
    }
    
    formatBTC(value) {
        if (typeof value !== 'number') return value;
        return `${Math.round(value)} BTC`;
    }
    
    formatPercentage(value) {
        if (typeof value !== 'number') return value;
        return `${Math.round(value)}%`;
    }
    
    updateMarketDisplay(data) {
        const btcPrice = document.getElementById('btc-price');
        const volatility = document.getElementById('volatility');
        
        if (btcPrice) {
            btcPrice.textContent = typeof data.btc_price === 'number' 
                ? this.formatCurrency(data.btc_price)
                : data.btc_price;
        }
        
        if (volatility) {
            volatility.textContent = typeof data.volatility === 'number'
                ? this.formatPercentage(data.volatility)
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
                ? this.formatPercentage(exposure.hedge_coverage_ratio * 100)
                : 'N/A'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = typeof value === 'number' && id !== 'coverage-ratio'
                    ? this.formatBTC(value)
                    : value;
            }
        });
    }
    
    showStep(stepNumber) {
        document.querySelectorAll('.workflow-step').forEach(step => {
            step.classList.remove('active');
        });
        
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
                        <span class="metric-label">Institution</span>
                        <span class="metric-value">${analysis.profile.name}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">BTC Position</span>
                        <span class="metric-value">${Math.round(analysis.positions.btc_size)} BTC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Position Value</span>
                        <span class="metric-value">${this.formatCurrency(analysis.positions.btc_value)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Current BTC Price</span>
                        <span class="metric-value">${this.formatCurrency(analysis.positions.current_price)}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Risk Analysis</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">1-Day VaR (95%)</span>
                        <span class="metric-value">${this.formatCurrency(analysis.risk_metrics.var_1d_95)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">30-Day VaR (95%)</span>
                        <span class="metric-value">${this.formatCurrency(analysis.risk_metrics.var_30d_95)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Annual Volatility</span>
                        <span class="metric-value">${this.formatPercentage(analysis.risk_metrics.volatility * 100)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Max Drawdown (30%)</span>
                        <span class="metric-value">${this.formatCurrency(analysis.risk_metrics.max_drawdown_30pct)}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Scenario Analysis</h4>
                <div class="risk-scenarios">
                    ${analysis.scenarios.filter(s => s.change_pct < 0).map(scenario => `
                        <div class="scenario-card">
                            <h5>${scenario.change_pct}% BTC Decline</h5>
                            <div class="scenario-value">${this.formatCurrency(Math.abs(scenario.pnl))}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Hedge Recommendation</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Risk Tolerance</span>
                        <span class="metric-value">${analysis.profile.risk_tolerance?.toUpperCase() || 'MODERATE'}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Recommended Hedge Ratio</span>
                        <span class="metric-value">${this.formatPercentage(analysis.hedge_recommendation.hedge_ratio * 100)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Hedge Size</span>
                        <span class="metric-value">${Math.round(analysis.hedge_recommendation.hedge_size_btc)} BTC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Available Strategies</span>
                        <span class="metric-value">${analysis.hedge_recommendation.preferred_strategies?.length || 1} Options</span>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        document.getElementById('generate-strategy-btn').style.display = 'inline-block';
    }
    
    async generateStrategies() {
        this.showLoading('Generating multiple hedging strategies...');
        
        try {
            const response = await fetch('/api/generate-strategies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.availableStrategies = data.strategies;
                this.displayStrategies(data.strategies, data.analysis_context);
                this.showStep(3);
            } else {
                alert('Error generating strategies: ' + data.error);
            }
        } catch (error) {
            console.error('Strategy generation error:', error);
            alert('Error generating strategies. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    displayStrategies(strategies, context) {
        const container = document.getElementById('strategy-results');
        
        let html = `
            <div style="text-align: center; margin-bottom: 40px; padding: 28px; background: linear-gradient(135deg, rgba(251,191,36,0.1) 0%, rgba(37,99,235,0.1) 100%); border-radius: 20px; border: 2px solid rgba(251,191,36,0.3);">
                <h4 style="color: var(--warning-light); margin-bottom: 16px; font-size: 24px;">Smart Strategy Recommendations for ${context.institution}</h4>
                <p style="color: var(--text-bright); font-size: 18px;">Based on ${context.risk_tolerance} risk tolerance and ${Math.round(context.position_size)} BTC position</p>
            </div>
            
            <div class="strategies-grid">
        `;
        
        strategies.forEach((strategy, index) => {
            const isRecommended = strategy.recommended || index === 0;
            
            html += `
                <div class="strategy-option ${isRecommended ? 'recommended' : ''}" onclick="demo.selectStrategy('${strategy.strategy_type}')">
                    <div class="strategy-header">
                        <div class="strategy-name">${strategy.strategy_name}</div>
                        <div class="strategy-cost">${Math.round(strategy.cost_percentage || strategy.income_percentage || 0)}%</div>
                    </div>
                    
                    <div class="strategy-description">${strategy.strategy_description}</div>
                    
                    <div class="strategy-metrics">
                        <div class="strategy-metric">
                            <span class="metric-label">Total Cost/Income</span>
                            <span class="metric-value">${this.formatCurrency(strategy.total_client_cost || strategy.total_net_received || 0)}</span>
                        </div>
                        <div class="strategy-metric">
                            <span class="metric-label">Max Loss/Upside</span>
                            <span class="metric-value">${this.formatCurrency(strategy.max_loss || strategy.max_upside || 0)}</span>
                        </div>
                        <div class="strategy-metric">
                            <span class="metric-label">Protection Level</span>
                            <span class="metric-value">${this.formatCurrency(strategy.protection_level || strategy.strike_price || strategy.call_strike || 0)}</span>
                        </div>
                        <div class="strategy-metric">
                            <span class="metric-label">Complexity</span>
                            <span class="metric-value">${strategy.complexity || 'Low'}</span>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <h6 style="color: var(--success); margin-bottom: 10px; font-size: 15px; font-weight: 700;">Key Benefits:</h6>
                        <ul style="color: var(--text-bright); font-size: 15px; margin-left: 18px; line-height: 1.4;">
                            ${strategy.key_benefits?.slice(0, 3).map(benefit => `<li style="margin-bottom: 6px;">${benefit}</li>`).join('') || '<li>Professional execution</li>'}
                        </ul>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 14px; background: linear-gradient(135deg, rgba(251,191,36,0.2) 0%, rgba(37,99,235,0.2) 100%); border-radius: 12px; text-align: center; border: 2px solid rgba(251,191,36,0.4);">
                        <span style="color: var(--warning-light); font-weight: 700; font-size: 15px;">Click to Select Strategy</span>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    async selectStrategy(strategyType) {
        this.showLoading('Selecting strategy for execution...');
        
        try {
            const response = await fetch('/api/select-strategy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ strategy_type: strategyType })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.selectedStrategy = data.strategy;
                this.displaySelectedStrategy(data.strategy);
                setTimeout(() => {
                    this.executeStrategy();
                }, 1500);
            } else {
                alert('Error selecting strategy: ' + data.error);
            }
        } catch (error) {
            console.error('Strategy selection error:', error);
            alert('Error selecting strategy. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    displaySelectedStrategy(strategy) {
        const container = document.getElementById('strategy-results');
        const summaryHtml = `
            <div style="background: linear-gradient(135deg, rgba(16,185,129,0.2) 0%, rgba(5,150,105,0.2) 100%); border: 3px solid var(--success); border-radius: 16px; padding: 28px; margin-bottom: 28px; text-align: center;">
                <h4 style="color: var(--success); margin-bottom: 12px; font-size: 24px;">✅ ${strategy.strategy_name} Selected</h4>
                <p style="color: var(--text-bright); font-size: 17px;">Proceeding to execution via institutional channels...</p>
            </div>
        `;
        container.innerHTML = summaryHtml + container.innerHTML;
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
            <div class="analysis-card" style="background: linear-gradient(135deg, rgba(16,185,129,0.2) 0%, rgba(5,150,105,0.1) 100%); border-color: var(--success);">
                <h4>✅ Execution Completed Successfully</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Strategy Executed</span>
                        <span class="metric-value">${execution.execution_summary.strategy_name}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Status</span>
                        <span class="metric-value" style="color: var(--success);">${execution.execution_summary.status.toUpperCase()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Contracts Filled</span>
                        <span class="metric-value">${Math.round(execution.execution_summary.contracts_filled)} BTC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Total Premium</span>
                        <span class="metric-value">${this.formatCurrency(execution.execution_summary.total_premium_client)}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Portfolio Impact</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Institution</span>
                        <span class="metric-value">${execution.portfolio_impact.institution}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">VaR Before</span>
                        <span class="metric-value">${this.formatCurrency(execution.portfolio_impact.var_reduction.before)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">VaR After</span>
                        <span class="metric-value">${this.formatCurrency(execution.portfolio_impact.var_reduction.after)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Risk Reduction</span>
                        <span class="metric-value" style="color: var(--success);">${execution.portfolio_impact.var_reduction.reduction_pct}%</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Platform Exposure Management</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Total Client Positions</span>
                        <span class="metric-value">${this.formatBTC(execution.platform_exposure.client_positions_btc)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Platform Hedges</span>
                        <span class="metric-value">${this.formatBTC(execution.platform_exposure.platform_hedges_btc)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Net Exposure</span>
                        <span class="metric-value">${this.formatBTC(execution.platform_exposure.net_exposure_btc)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Hedge Action</span>
                        <span class="metric-value">${execution.platform_exposure.platform_hedge_action.status.toUpperCase()}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>Execution Venues</h4>
                <div style="display: grid; gap: 12px;">
                    ${execution.execution_summary.execution_venues.map(venue => `
                        <div style="display: flex; justify-content: space-between; padding: 16px 20px; background: linear-gradient(135deg, rgba(30,41,59,0.2) 0%, rgba(37,99,235,0.1) 100%); border-radius: 12px; border: 1px solid rgba(251,191,36,0.2);">
                            <span style="font-weight: 700; font-size: 16px; color: var(--warning-light);">${venue.exchange.toUpperCase()}</span>
                            <span style="font-size: 16px; color: var(--text-bright);">${Math.round(venue.size)} BTC (${venue.liquidity} liquidity)</span>
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
        this.availableStrategies = null;
        this.selectedStrategy = null;
        
        this.showStep(1);
        
        document.getElementById('custom-size').value = '';
        document.getElementById('generate-strategy-btn').style.display = 'none';
        
        document.getElementById('analysis-results').innerHTML = '';
        document.getElementById('strategy-results').innerHTML = '';
        document.getElementById('execution-results').innerHTML = '';
    }
    
    showSection(sectionName) {
        document.querySelectorAll('.demo-section').forEach(section => {
            section.classList.remove('active');
        });
        
        document.querySelectorAll('.nav-step').forEach(step => {
            step.classList.remove('active');
        });
        
        const targetSection = document.getElementById(`${sectionName}-section`);
        const targetNav = document.querySelector(`[data-section="${sectionName}"]`);
        
        if (targetSection) targetSection.classList.add('active');
        if (targetNav) targetNav.classList.add('active');
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
    demo.generateStrategies();
}

function resetDemo() {
    demo.resetDemo();
}

// Initialize demo
let demo;

document.addEventListener('DOMContentLoaded', function() {
    demo = new AttticusProfessionalDemo();
});
