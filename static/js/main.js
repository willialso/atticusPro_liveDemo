// Professional Atticus Demo JavaScript - Complete Implementation
class AtticusDemo {
    constructor() {
        this.currentStep = 1;
        this.portfolio = null;
        this.strategies = [];
        this.customPositions = [];
        this.selectedStrategy = null;
        this.executionData = null;
        this.init();
    }

    init() {
        this.loadMarketData();
        this.bindEvents();
        this.updateStepIndicator();
    }

    async loadMarketData() {
        try {
            const response = await fetch('/api/market-data');
            const data = await response.json();
            
            if (data.success) {
                const priceElement = document.getElementById('live-btc-price');
                const marketElement = document.getElementById('market-data');
                
                if (priceElement) {
                    priceElement.textContent = `$${data.btc_price.toLocaleString()}`;
                }
                
                if (marketElement) {
                    marketElement.textContent = 
                        `BTC $${data.btc_price.toLocaleString()} • Volatility: ${(data.market_conditions.implied_volatility * 100).toFixed(0)}% • 7-Day: ${(data.market_conditions.price_trend_7d * 100).toFixed(1)}%`;
                }
            }
        } catch (error) {
            console.error('Failed to load market data:', error);
            document.getElementById('live-btc-price').textContent = 'Unavailable';
        }
    }

    bindEvents() {
        // Start demo
        const startBtn = document.getElementById('start-demo');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startDemo());
        }

        // Generate portfolio
        const generateBtn = document.getElementById('generate-portfolio');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generatePortfolio());
        }

        // Fund type change
        const fundTypeSelect = document.getElementById('fund-type');
        if (fundTypeSelect) {
            fundTypeSelect.addEventListener('change', (e) => this.updatePortfolioInfo(e.target.value));
            this.updatePortfolioInfo(fundTypeSelect.value); // Initial update
        }

        // Custom positions
        const addBtn = document.getElementById('add-position');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addCustomPosition());
        }

        const clearBtn = document.getElementById('clear-positions');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearPositions());
        }

        // Analyze strategies
        const analyzeBtn = document.getElementById('analyze-strategies');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeStrategies());
        }

        // Back to portfolio
        const backBtn = document.getElementById('back-to-portfolio');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.backToPortfolio());
        }
    }

    startDemo() {
        this.hideElement('intro-section');
        this.showElement('portfolio-section');
        this.currentStep = 1;
        this.updateStepIndicator();
        this.addAnimation('portfolio-section', 'animate-slide-up');
    }

    updatePortfolioInfo(fundType) {
        const livePriceElement = document.getElementById('live-btc-price');
        const livePriceText = livePriceElement ? livePriceElement.textContent : '$65,000';
        const livePrice = parseFloat(livePriceText.replace(/[$,]/g, '')) || 65000;
        
        const infoElement = document.getElementById('portfolio-info');
        if (!infoElement) return;
        
        if (fundType.includes('Small')) {
            const btcAllocation = 2000000 / livePrice;
            infoElement.innerHTML = 
                `<p class="text-white font-semibold text-lg">📊 <strong>Portfolio Specification:</strong> ~${btcAllocation.toFixed(1)} BTC position ($2M allocation) with realistic performance metrics and risk exposure</p>`;
        } else {
            const btcAllocation = 8500000 / livePrice;
            infoElement.innerHTML = 
                `<p class="text-white font-semibold text-lg">📊 <strong>Portfolio Specification:</strong> ~${btcAllocation.toFixed(1)} BTC position ($8.5M allocation) with institutional-scale exposure and complexity</p>`;
        }
    }

    async generatePortfolio() {
        try {
            const fundType = document.getElementById('fund-type').value;
            this.showLoading('generate-portfolio', 'Generating with real-time pricing...');

            const response = await fetch('/api/generate-portfolio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fund_type: fundType })
            });

            const data = await response.json();
            
            if (data.success) {
                this.portfolio = data.portfolio;
                this.displayPortfolioResults();
                this.hideLoading('generate-portfolio', 'Generate Professional Portfolio');
            } else {
                this.showError('Failed to generate portfolio: ' + data.error);
                this.hideLoading('generate-portfolio', 'Generate Professional Portfolio');
            }
        } catch (error) {
            console.error('Failed to generate portfolio:', error);
            this.showError('Failed to generate portfolio. Please try again.');
            this.hideLoading('generate-portfolio', 'Generate Professional Portfolio');
        }
    }

    displayPortfolioResults() {
        const portfolio = this.portfolio;
        const metricsElement = document.getElementById('portfolio-metrics');
        const resultsElement = document.getElementById('portfolio-results');
        const riskElement = document.getElementById('risk-analysis');
        
        if (!metricsElement || !resultsElement) return;

        // Create professional metrics display
        metricsElement.innerHTML = `
            <div class="metric-card">
                <div class="metric-value">$${(portfolio.aum / 1000000).toFixed(0)}M</div>
                <div class="metric-label">Total AUM</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${portfolio.total_btc_size.toFixed(1)} BTC</div>
                <div class="metric-label">BTC Position</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">$${(portfolio.total_current_value / 1000000).toFixed(1)}M</div>
                <div class="metric-label">Current Value</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">$${(portfolio.total_pnl / 1000000).toFixed(1)}M</div>
                <div class="metric-label">Unrealized P&L</div>
            </div>
        `;
        
        // Risk analysis
        const potentialLoss = portfolio.total_current_value * 0.25;
        if (riskElement) {
            riskElement.innerHTML = `
                <p class="text-white font-bold text-lg">⚠️ <strong>Risk Assessment:</strong> A 25% market decline would result in ${(potentialLoss / 1000000).toFixed(1)}M institutional loss without professional protection strategies</p>
            `;
        }
        
        resultsElement.classList.remove('hidden');
        this.addAnimation('portfolio-results', 'animate-slide-up');
    }

    async analyzeStrategies() {
        try {
            this.currentStep = 2;
            this.updateStepIndicator();

            this.hideElement('portfolio-section');
            this.showElement('strategy-section');

            // Update strategy banner
            const bannerElement = document.getElementById('strategy-portfolio-summary');
            if (bannerElement && this.portfolio) {
                const netBtc = this.portfolio.net_btc_exposure;
                const positionDirection = netBtc > 0 ? "Long" : netBtc < 0 ? "Short" : "Neutral";
                bannerElement.textContent = `Portfolio Analysis Complete: ${Math.abs(netBtc).toFixed(1)} BTC ${positionDirection} position • $${Math.abs(netBtc) * this.portfolio.current_btc_price / 1000000}M total value`;
            }

            // Show loading
            document.getElementById('strategy-list').innerHTML = `
                <div class="text-center py-12">
                    <div class="loading text-3xl mb-4">🔄</div>
                    <p class="text-2xl font-bold text-yellow-400">Analyzing live market conditions and generating institutional strategies...</p>
                    <p class="text-lg text-slate-300 mt-2">This may take 30-45 seconds</p>
                </div>
            `;

            // Simulate realistic loading time
            await new Promise(resolve => setTimeout(resolve, 3000));

            const response = await fetch('/api/generate-strategies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();
            
            if (data.success) {
                this.strategies = data.strategies;
                this.displayStrategies();
            } else {
                this.showError('Failed to generate strategies: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to analyze strategies:', error);
            this.showError('Failed to analyze strategies. Please try again.');
        }
    }

    displayStrategies() {
        let strategiesHtml = '';
        
        this.strategies.forEach((strategy, index) => {
            const priorityClass = strategy.priority === 'high' ? 'high-priority' : 
                                 strategy.priority === 'medium' ? 'medium-priority' : 'low-priority';
            const priorityIcon = strategy.priority === 'high' ? '🔥' : 
                                strategy.priority === 'medium' ? '⭐' : '💡';
            const priorityText = strategy.priority === 'high' ? 'HIGH PRIORITY' : 
                                strategy.priority === 'medium' ? 'RECOMMENDED' : 'ALTERNATIVE';

            const isIncome = strategy.pricing.total_premium < 0;
            const costColor = isIncome ? 'text-green-400' : 'text-blue-400';
            const costLabel = isIncome ? 'Income' : 'Cost';

            strategiesHtml += `
                <div class="strategy-card ${priorityClass} animate-slide-up">
                    <div class="flex justify-between items-start mb-6">
                        <div class="flex-1">
                            <h3 class="text-2xl font-bold text-yellow-400 mb-3">${priorityIcon} ${priorityText}: ${strategy.display_name}</h3>
                            <div class="space-y-2 text-slate-300 text-lg">
                                <p><strong>Coverage:</strong> ${strategy.target_exposure.toFixed(1)} BTC position</p>
                                <p><strong>Strategy:</strong> ${strategy.rationale}</p>
                                <p><strong>Duration:</strong> ${strategy.pricing.days_to_expiry} days • <strong>Expiry:</strong> ${strategy.pricing.expiry_date}</p>
                                <p><strong>Option Type:</strong> ${strategy.pricing.option_type}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-4 gap-4 mb-6">
                        <div class="metric-card">
                            <div class="metric-value ${costColor}">
                                ${costLabel}<br>
                                $${Math.abs(strategy.pricing.total_premium).toLocaleString()}
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${strategy.pricing.cost_as_pct.toFixed(1)}%</div>
                            <div class="metric-label">Portfolio Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${strategy.pricing.contracts_needed}</div>
                            <div class="metric-label">Contracts</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${(strategy.pricing.implied_volatility * 100).toFixed(0)}%</div>
                            <div class="metric-label">Volatility</div>
                        </div>
                    </div>
                    
                    <button onclick="demo.executeStrategy(${index})" class="w-full bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-slate-900 font-bold text-xl py-4 px-6 rounded-xl transition-all duration-300">
                        Execute ${strategy.display_name}
                    </button>
                </div>
            `;
        });

        document.getElementById('strategy-list').innerHTML = strategiesHtml;
    }

    async executeStrategy(strategyIndex) {
        try {
            this.currentStep = 3;
            this.updateStepIndicator();

            this.hideElement('strategy-section');
            this.showElement('execution-section');

            // Show professional loading
            document.getElementById('execution-results').innerHTML = `
                <div class="text-center py-12">
                    <div class="loading text-4xl mb-6">⚡</div>
                    <h3 class="text-3xl font-bold text-yellow-400 mb-4">Executing Strategy with Live Institutional Pricing</h3>
                    <p class="text-xl text-slate-300">Professional options execution in progress...</p>
                </div>
            `;

            // Simulate realistic execution time
            await new Promise(resolve => setTimeout(resolve, 3000));

            const response = await fetch('/api/execute-strategy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ strategy_index: strategyIndex })
            });

            const data = await response.json();
            
            if (data.success) {
                this.selectedStrategy = this.strategies[strategyIndex];
                this.executionData = data.execution;
                this.displayExecutionResults();
            } else {
                this.showError('Failed to execute strategy: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to execute strategy:', error);
            this.showError('Failed to execute strategy. Please try again.');
        }
    }

    displayExecutionResults() {
        const strategy = this.selectedStrategy;
        const execution = this.executionData;
        const outcomes = execution.outcomes;

        const resultsHtml = `
            <div class="execution-success animate-slide-up">
                <h3>🎯 Institutional Strategy Executed Successfully</h3>
                <p>Professional options strategy executed with live market pricing</p>
                <div class="mt-4">
                    <span class="text-2xl font-bold">⚡ Execution Time: ${execution.execution_time} seconds</span>
                </div>
            </div>

            <div class="bg-blue-600 rounded-xl p-6 mb-8 animate-slide-up">
                <p class="text-white text-xl font-semibold">✅ <strong>Execution Summary:</strong> Professional options strategy successfully executed for ${strategy.target_exposure.toFixed(1)} BTC position using live market pricing from institutional trading channels</p>
            </div>

            <h3 class="text-3xl font-bold text-yellow-400 mb-8 text-center">📋 Executed Contract Specifications</h3>

            <div class="grid lg:grid-cols-2 gap-8 mb-10">
                <div class="contract-detail-card animate-slide-up">
                    <h4>Contract Details</h4>
                    <p><strong>Strategy Type:</strong> ${strategy.pricing.option_type}</p>
                    <p><strong>Contracts Executed:</strong> ${strategy.pricing.contracts_needed} contracts</p>
                    <p><strong>Strike Price:</strong> $${strategy.pricing.strike_price.toLocaleString()}</p>
                    <p><strong>Expiry Date:</strong> ${strategy.pricing.expiry_date}</p>
                    <p><strong>Total Premium:</strong> $${Math.abs(strategy.pricing.total_premium).toLocaleString()}</p>
                    <p><strong>Premium per Contract:</strong> $${(Math.abs(strategy.pricing.total_premium) / strategy.pricing.contracts_needed).toLocaleString()}</p>
                </div>
                
                <div class="contract-detail-card animate-slide-up">
                    <h4>Protection Summary</h4>
                    <p><strong>Position Protected:</strong> ${strategy.target_exposure.toFixed(1)} BTC</p>
                    <p><strong>Entry Price:</strong> $${strategy.pricing.btc_spot_price.toLocaleString()}</p>
                    <p><strong>Breakeven Level:</strong> $${outcomes.breakeven_price.toLocaleString()}</p>
                    <p><strong>Maximum Risk:</strong> ${typeof outcomes.max_loss === 'string' ? outcomes.max_loss : '$' + outcomes.max_loss.toLocaleString()}</p>
                    <p><strong>Maximum Reward:</strong> ${outcomes.max_profit}</p>
                    <p><strong>Portfolio Impact:</strong> ${strategy.pricing.cost_as_pct.toFixed(2)}% of total value</p>
                </div>
            </div>

            <h3 class="text-3xl font-bold text-yellow-400 mb-8 text-center">📊 Professional Market Scenario Analysis</h3>
            
            <div class="bg-blue-600 rounded-xl p-6 mb-8 animate-slide-up">
                <p class="text-white text-lg font-semibold">💡 <strong>Professional Risk Assessment:</strong> These scenarios demonstrate exactly how your institutional portfolio will perform under various Bitcoin price movements with professional protection in place.</p>
            </div>

            <div class="space-y-4 mb-10">
                ${outcomes.scenarios.map((scenario, index) => {
                    const cardClass = index === 0 ? 'positive' : index === 1 ? 'warning' : 'negative';
                    const icon = index === 0 ? '🟢' : index === 1 ? '🟡' : '🔴';
                    return `
                        <div class="scenario-card ${cardClass} animate-slide-up">
                            <h5>${icon} Scenario ${index + 1}: ${scenario.condition}</h5>
                            <p><strong>${scenario.outcome}:</strong> ${scenario.details}</p>
                        </div>
                    `;
                }).join('')}
            </div>

            <div class="execution-success animate-slide-up">
                <h3>✅ Professional Portfolio Protection Successfully Deployed</h3>
                <p>Your institutional portfolio now has professional-grade downside protection while maintaining unlimited upside potential through sophisticated options strategies</p>
            </div>

            <div class="bg-slate-800 rounded-xl p-8 mb-8 animate-slide-up">
                <h4 class="text-2xl font-bold text-yellow-400 mb-4">🚀 Ready for Live Implementation?</h4>
                <div class="space-y-4 text-lg text-slate-300">
                    <p><strong>This demonstration showcases real institutional options strategies with live market pricing and immediately executable contracts.</strong></p>
                    <p><strong>All displayed strategies are available for immediate implementation through professional institutional trading channels.</strong></p>
                    <p><strong>Contact our institutional team to discuss implementing these professional protection strategies for your actual portfolio.</strong></p>
                </div>
                
                <div class="grid md:grid-cols-2 gap-6 mt-6">
                    <div class="metric-card">
                        <div class="metric-value">Multi-Exchange</div>
                        <div class="metric-label">Live Pricing Sources</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">Institutional</div>
                        <div class="metric-label">Strategy Grade</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">12-28 sec</div>
                        <div class="metric-label">Execution Speed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">24/7</div>
                        <div class="metric-label">Market Access</div>
                    </div>
                </div>
            </div>

            <div class="text-center space-x-6">
                <button onclick="demo.resetDemo()" class="bg-slate-600 hover:bg-slate-700 text-white font-bold text-lg py-4 px-8 rounded-xl transition-all duration-300">
                    🔄 Analyze New Portfolio
                </button>
                <a href="https://t.me/willialso" target="_blank" class="inline-block bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-bold text-lg py-4 px-8 rounded-xl transition-all duration-300">
                    💬 Contact Institutional Team
                </a>
            </div>
        `;

        document.getElementById('execution-results').innerHTML = resultsHtml;
    }

    addCustomPosition() {
        const btcAmount = parseFloat(document.getElementById('btc-amount').value);
        const positionType = document.getElementById('position-type').value;
        
        if (btcAmount > 0) {
            this.customPositions.push({ btc_amount: btcAmount, position_type: positionType });
            this.updatePositionsList();
            document.getElementById('btc-amount').value = '25';
            
            // Show success feedback
            this.showSuccessMessage(`Added ${btcAmount.toFixed(1)} BTC ${positionType} position`);
        } else {
            this.showError('Please enter a valid BTC amount');
        }
    }

    updatePositionsList() {
        const listElement = document.getElementById('positions-list');
        
        if (this.customPositions.length === 0) {
            listElement.innerHTML = '';
            return;
        }

        let html = '<h4 class="text-2xl font-bold text-yellow-400 mb-6 mt-8">📋 Portfolio Positions</h4>';
        
        this.customPositions.forEach((pos, index) => {
            const livePriceElement = document.getElementById('live-btc-price');
            const livePrice = livePriceElement ? parseFloat(livePriceElement.textContent.replace(/[$,]/g, '')) : 65000;
            const positionValue = pos.btc_amount * livePrice;
            
            html += `
                <div class="position-item">
                    <div class="flex justify-between items-center">
                        <span class="text-white text-lg font-semibold">
                            ${pos.btc_amount.toFixed(1)} BTC • ${pos.position_type === 'Long' ? '🟢 Long' : '🔴 Short'} • $${positionValue.toLocaleString()}
                        </span>
                        <button onclick="demo.removePosition(${index})" class="text-red-400 hover:text-red-300 font-bold text-lg px-3 py-1 rounded transition-all duration-300">
                            ❌ Remove
                        </button>
                    </div>
                </div>
            `;
        });

        const totalLong = this.customPositions.filter(p => p.position_type === 'Long').reduce((sum, p) => sum + p.btc_amount, 0);
        const totalShort = this.customPositions.filter(p => p.position_type === 'Short').reduce((sum, p) => sum + p.btc_amount, 0);
        const netBtc = totalLong - totalShort;

        html += `
            <div class="grid grid-cols-3 gap-4 mt-8">
                <div class="metric-card">
                    <div class="metric-value">${totalLong.toFixed(1)}</div>
                    <div class="metric-label">Long BTC</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${totalShort.toFixed(1)}</div>
                    <div class="metric-label">Short BTC</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${netBtc >= 0 ? '+' : ''}${netBtc.toFixed(1)}</div>
                    <div class="metric-label">Net BTC</div>
                </div>
            </div>
            <button onclick="demo.analyzeCustomPortfolio()" class="w-full mt-6 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-slate-900 font-bold text-xl py-4 px-6 rounded-xl transition-all duration-300">
                Analyze Custom Portfolio Protection
            </button>
        `;

        listElement.innerHTML = html;
    }

    async analyzeCustomPortfolio() {
        try {
            const response = await fetch('/api/create-custom-portfolio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ positions: this.customPositions })
            });

            const data = await response.json();
            
            if (data.success) {
                this.portfolio = data.portfolio;
                await this.analyzeStrategies();
            } else {
                this.showError('Failed to create custom portfolio: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to analyze custom portfolio:', error);
            this.showError('Failed to analyze custom portfolio. Please try again.');
        }
    }

    removePosition(index) {
        this.customPositions.splice(index, 1);
        this.updatePositionsList();
        this.showSuccessMessage('Position removed successfully');
    }

    clearPositions() {
        this.customPositions = [];
        this.updatePositionsList();
        this.showSuccessMessage('All positions cleared');
    }

    backToPortfolio() {
        this.currentStep = 1;
        this.updateStepIndicator();
        this.hideElement('strategy-section');
        this.showElement('portfolio-section');
        this.strategies = [];
    }

    updateStepIndicator() {
        // Update step circles and labels
        for (let i = 1; i <= 3; i++) {
            const stepElement = document.getElementById(`step-${i}`);
            if (!stepElement) continue;
            
            stepElement.classList.remove('active', 'completed', 'inactive');
            
            if (i < this.currentStep) {
                stepElement.classList.add('completed');
                stepElement.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
                stepElement.style.color = 'white';
                stepElement.style.borderColor = '#10b981';
            } else if (i === this.currentStep) {
                stepElement.classList.add('active');
                stepElement.style.background = 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)';
                stepElement.style.color = '#1e293b';
                stepElement.style.borderColor = '#fbbf24';
            } else {
                stepElement.classList.add('inactive');
                stepElement.style.background = '#475569';
                stepElement.style.color = '#cbd5e1';
                stepElement.style.borderColor = '#64748b';
            }
        }

        // Update progress bar
        const progressBar = document.getElementById('progress-bar');
        const currentStepText = document.getElementById('current-step-text');
        if (progressBar) {
            const progressPercentage = (this.currentStep / 3) * 100;
            progressBar.style.width = `${progressPercentage}%`;
        }
        if (currentStepText) {
            currentStepText.textContent = this.currentStep;
        }
    }

    resetDemo() {
        // Reset all state
        this.currentStep = 1;
        this.portfolio = null;
        this.strategies = [];
        this.customPositions = [];
        this.selectedStrategy = null;
        this.executionData = null;
        
        // Show intro section
        this.showElement('intro-section');
        this.hideElement('portfolio-section');
        this.hideElement('strategy-section');
        this.hideElement('execution-section');
        
        // Reset forms
        const resultsElement = document.getElementById('portfolio-results');
        if (resultsElement) {
            resultsElement.classList.add('hidden');
        }
        
        const positionsElement = document.getElementById('positions-list');
        if (positionsElement) {
            positionsElement.innerHTML = '';
        }
        
        this.updateStepIndicator();
        this.loadMarketData();
        this.showSuccessMessage('Demo reset complete - starting new analysis');
    }

    // Utility functions
    hideElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add('hidden');
        }
    }

    showElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove('hidden');
        }
    }

    addAnimation(elementId, animationClass) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add(animationClass);
            setTimeout(() => {
                element.classList.remove(animationClass);
            }, 600);
        }
    }

    showLoading(buttonId, text) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = true;
            button.innerHTML = `<span class="loading">🔄</span> ${text}`;
        }
    }

    hideLoading(buttonId, originalText) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }

    showSuccessMessage(message) {
        // Create temporary success message
        const successDiv = document.createElement('div');
        successDiv.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-up';
        successDiv.innerHTML = `✅ ${message}`;
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }

    showError(message) {
        // Create temporary error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-up';
        errorDiv.innerHTML = `❌ ${message}`;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

// Initialize demo when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.demo = new AtticusDemo();
});

// Global function for strategy execution (called from dynamic HTML)
window.demo = null;
