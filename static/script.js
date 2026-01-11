/**
 * Delhi Metro Route Finder
 * Enhanced JavaScript for route finding with autocomplete, 
 * multiple route options, and improved visualization.
 * 
 * @author Delhi Metro Route Finder Project
 * @version 2.0.0
 */

document.addEventListener('DOMContentLoaded', function() {
    // ==================== DOM Elements ====================
    const elements = {
        // Search inputs
        sourceSearch: document.getElementById('source-search'),
        destinationSearch: document.getElementById('destination-search'),
        sourceHidden: document.getElementById('source'),
        destinationHidden: document.getElementById('destination'),
        sourceSuggestions: document.getElementById('source-suggestions'),
        destinationSuggestions: document.getElementById('destination-suggestions'),
        
        // Buttons
        findRouteBtn: document.getElementById('find-route-btn'),
        swapBtn: document.getElementById('swap-stations-btn'),
        routeTypeBtns: document.querySelectorAll('.route-type-btn'),
        smartCardToggle: document.getElementById('smart-card-toggle'),
        
        // Map controls
        zoomInBtn: document.getElementById('zoom-in-btn'),
        zoomOutBtn: document.getElementById('zoom-out-btn'),
        resetViewBtn: document.getElementById('reset-view-btn'),
        
        // Results
        resultDiv: document.getElementById('result'),
        errorDiv: document.getElementById('error-message'),
        routeComparison: document.getElementById('route-comparison'),
        comparisonCards: document.getElementById('comparison-cards'),
        selectedRoute: document.getElementById('selected-route'),
        
        // Summary elements
        totalDistanceSpan: document.getElementById('total-distance'),
        stationsCountSpan: document.getElementById('stations-count'),
        estimatedTimeSpan: document.getElementById('estimated-time'),
        fareSpan: document.getElementById('fare'),
        fareType: document.getElementById('fare-type'),
        fareSavings: document.getElementById('fare-savings'),
        savingsAmount: document.getElementById('savings-amount'),
        lineChangesAlert: document.getElementById('line-changes-alert'),
        lineChangesText: document.getElementById('line-changes-text'),
        
        // Map and path
        metroMap: document.getElementById('metro-map'),
        pathList: document.getElementById('path-list')
    };
    
    // ==================== State Management ====================
    const state = {
        selectedRouteType: 'shortest',
        useSmartCard: false,
        currentZoom: 1,
        allStations: window.METRO_DATA?.allStations || [],
        popularStations: window.METRO_DATA?.popularStations || [],
        interchangeStations: window.METRO_DATA?.interchangeStations || [],
        currentRoute: null
    };
    
    // ==================== Line Colors ====================
    const LINE_COLORS = {
        'Yellow': '#FBC02D',
        'Blue': '#1E88E5',
        'Blue Branch': '#29B6F6',
        'Red': '#E53935',
        'Green': '#43A047',
        'Green Branch': '#8BC34A',
        'Violet': '#8E24AA',
        'Magenta': '#FF00FF',
        'Pink': '#D81B60',
        'Grey': '#757575',
        'Orange': '#FB8C00',
        'Aqua': '#00ACC1'
    };
    
    // ==================== Initialization ====================
    function init() {
        setupAutocomplete();
        setupEventListeners();
        setupKeyboardNavigation();
    }
    
    // ==================== Autocomplete Setup ====================
    function setupAutocomplete() {
        // Source station autocomplete
        setupStationSearch(
            elements.sourceSearch, 
            elements.sourceHidden, 
            elements.sourceSuggestions
        );
        
        // Destination station autocomplete
        setupStationSearch(
            elements.destinationSearch, 
            elements.destinationHidden, 
            elements.destinationSuggestions
        );
    }
    
    function setupStationSearch(inputEl, hiddenEl, suggestionsEl) {
        let debounceTimer;
        
        inputEl.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = this.value.trim();
            
            if (query.length < 2) {
                hideSuggestions(suggestionsEl);
                hiddenEl.value = '';
                return;
            }
            
            debounceTimer = setTimeout(() => {
                const matches = searchStations(query);
                showSuggestions(matches, inputEl, hiddenEl, suggestionsEl);
            }, 150);
        });
        
        inputEl.addEventListener('focus', function() {
            if (this.value.length >= 2) {
                const matches = searchStations(this.value.trim());
                showSuggestions(matches, inputEl, hiddenEl, suggestionsEl);
            }
        });
        
        inputEl.addEventListener('blur', function() {
            // Delay to allow click on suggestion
            setTimeout(() => hideSuggestions(suggestionsEl), 200);
        });
        
        // Keyboard navigation for suggestions
        inputEl.addEventListener('keydown', function(e) {
            handleSuggestionKeyboard(e, suggestionsEl, inputEl, hiddenEl);
        });
    }
    
    function searchStations(query) {
        const queryLower = query.toLowerCase();
        const matches = state.allStations.filter(station => 
            station.toLowerCase().includes(queryLower)
        );
        
        // Sort: stations starting with query first, then alphabetically
        matches.sort((a, b) => {
            const aStarts = a.toLowerCase().startsWith(queryLower);
            const bStarts = b.toLowerCase().startsWith(queryLower);
            if (aStarts && !bStarts) return -1;
            if (!aStarts && bStarts) return 1;
            return a.localeCompare(b);
        });
        
        return matches.slice(0, 8); // Limit to 8 suggestions
    }
    
    function showSuggestions(matches, inputEl, hiddenEl, suggestionsEl) {
        if (matches.length === 0) {
            suggestionsEl.innerHTML = '<div class="no-results">No stations found</div>';
            suggestionsEl.classList.remove('hidden');
            return;
        }
        
        suggestionsEl.innerHTML = matches.map((station, index) => {
            const isInterchange = state.interchangeStations.includes(station);
            const isPopular = state.popularStations.includes(station);
            
            return `
                <div class="suggestion-item ${index === 0 ? 'selected' : ''}" 
                     data-station="${station}" 
                     tabindex="-1">
                    <span class="station-name">${highlightMatch(station, inputEl.value)}</span>
                    ${isInterchange ? '<span class="badge interchange">🔄 Interchange</span>' : ''}
                    ${isPopular ? '<span class="badge popular">⭐</span>' : ''}
                </div>
            `;
        }).join('');
        
        // Add click handlers
        suggestionsEl.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', function() {
                selectStation(this.dataset.station, inputEl, hiddenEl, suggestionsEl);
            });
        });
        
        suggestionsEl.classList.remove('hidden');
    }
    
    function highlightMatch(text, query) {
        const index = text.toLowerCase().indexOf(query.toLowerCase());
        if (index === -1) return text;
        
        const before = text.slice(0, index);
        const match = text.slice(index, index + query.length);
        const after = text.slice(index + query.length);
        
        return `${before}<strong>${match}</strong>${after}`;
    }
    
    function selectStation(station, inputEl, hiddenEl, suggestionsEl) {
        inputEl.value = station;
        hiddenEl.value = station;
        hideSuggestions(suggestionsEl);
        inputEl.classList.add('valid');
    }
    
    function hideSuggestions(suggestionsEl) {
        suggestionsEl.classList.add('hidden');
    }
    
    function handleSuggestionKeyboard(e, suggestionsEl, inputEl, hiddenEl) {
        const items = suggestionsEl.querySelectorAll('.suggestion-item');
        const selected = suggestionsEl.querySelector('.suggestion-item.selected');
        
        if (!items.length || suggestionsEl.classList.contains('hidden')) return;
        
        let currentIndex = Array.from(items).indexOf(selected);
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentIndex = (currentIndex + 1) % items.length;
                updateSelectedSuggestion(items, currentIndex);
                break;
            case 'ArrowUp':
                e.preventDefault();
                currentIndex = currentIndex <= 0 ? items.length - 1 : currentIndex - 1;
                updateSelectedSuggestion(items, currentIndex);
                break;
            case 'Enter':
                e.preventDefault();
                if (selected) {
                    selectStation(selected.dataset.station, inputEl, hiddenEl, suggestionsEl);
                }
                break;
            case 'Escape':
                hideSuggestions(suggestionsEl);
                break;
        }
    }
    
    function updateSelectedSuggestion(items, index) {
        items.forEach((item, i) => {
            item.classList.toggle('selected', i === index);
        });
        items[index].scrollIntoView({ block: 'nearest' });
    }
    
    // ==================== Event Listeners ====================
    function setupEventListeners() {
        // Find route button
        elements.findRouteBtn.addEventListener('click', handleFindRoute);
        
        // Swap stations button
        elements.swapBtn.addEventListener('click', swapStations);
        
        // Route type buttons
        elements.routeTypeBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                elements.routeTypeBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                state.selectedRouteType = this.dataset.type;
            });
        });
        
        // Smart card toggle
        elements.smartCardToggle.addEventListener('change', function() {
            state.useSmartCard = this.checked;
            // Re-calculate fare if route is displayed
            if (state.currentRoute) {
                updateFareDisplay(state.currentRoute.fare);
            }
        });
        
        // Quick station buttons
        document.querySelectorAll('.quick-station-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const station = this.dataset.station;
                const target = this.dataset.target;
                
                if (target === 'source') {
                    elements.sourceSearch.value = station;
                    elements.sourceHidden.value = station;
                    elements.sourceSearch.classList.add('valid');
                } else {
                    elements.destinationSearch.value = station;
                    elements.destinationHidden.value = station;
                    elements.destinationSearch.classList.add('valid');
                }
            });
        });
        
        // Map zoom controls
        elements.zoomInBtn?.addEventListener('click', () => zoomMap(0.2));
        elements.zoomOutBtn?.addEventListener('click', () => zoomMap(-0.2));
        elements.resetViewBtn?.addEventListener('click', resetMapView);
    }
    
    function setupKeyboardNavigation() {
        // Enter key to find route
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.target.closest('.suggestions-dropdown')) {
                if (elements.sourceHidden.value && elements.destinationHidden.value) {
                    handleFindRoute();
                }
            }
        });
    }
    
    // ==================== Route Finding ====================
    function handleFindRoute() {
        const source = elements.sourceHidden.value || elements.sourceSearch.value.trim();
        const destination = elements.destinationHidden.value || elements.destinationSearch.value.trim();
        
        // Validation
        if (!source || !destination) {
            showError('Please select both source and destination stations');
            return;
        }
        
        if (source.toLowerCase() === destination.toLowerCase()) {
            showError('Source and destination cannot be the same station. Please select different stations.');
            return;
        }
        
        // Show loading state
        setLoadingState(true);
        hideError();
        
        // Make API request
        findRoute(source, destination);
    }
    
    function findRoute(source, destination) {
        fetch('/find_route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source: source,
                destination: destination,
                route_type: state.selectedRouteType,
                use_smart_card: state.useSmartCard
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || `Server error: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            setLoadingState(false);
            
            if (data.status === 'success') {
                if (data.routes) {
                    // Multiple routes returned (Compare mode)
                    displayRouteComparison(data.routes);
                } else {
                    // Single route
                    displayRoute(data);
                }
            } else {
                showError(data.message || 'Failed to find route');
            }
        })
        .catch(error => {
            setLoadingState(false);
            console.error('Route finding error:', error);
            showError(error.message || 'An error occurred. Please try again.');
        });
    }
    
    // ==================== Display Functions ====================
    function displayRoute(data) {
        state.currentRoute = data;
        
        // Hide comparison, show single route
        elements.routeComparison.classList.add('hidden');
        elements.selectedRoute.classList.remove('hidden');
        
        // Update summary cards
        elements.totalDistanceSpan.textContent = data.distance.toFixed(2);
        elements.stationsCountSpan.textContent = data.stations_count;
        elements.estimatedTimeSpan.textContent = data.estimated_time || Math.round(data.stations_count * 2.5);
        
        // Update fare display
        updateFareDisplay(data.fare);
        
        // Update line changes alert
        updateLineChangesAlert(data.line_changes);
        
        // Render map visualization
        renderMetroMap(data.path, data.station_lines, data.line_changes);
        
        // Render station list
        renderStationList(data.path, data.station_lines, data.line_changes);
        
        // Show results
        elements.resultDiv.classList.remove('hidden');
        
        // Scroll to results
        elements.resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    function displayRouteComparison(routes) {
        state.currentRoute = routes[0];
        
        // Show comparison section
        elements.routeComparison.classList.remove('hidden');
        
        // Generate comparison cards
        elements.comparisonCards.innerHTML = routes.map((route, index) => {
            const routeLabel = route.route_type === 'shortest' ? '⚡ Fastest Route' : '🔄 Fewest Changes';
            const isSelected = index === 0;
            const fare = state.useSmartCard ? route.fare.smart_card_fare : route.fare.token_fare;
            
            return `
                <div class="comparison-card ${isSelected ? 'selected' : ''}" data-index="${index}">
                    <div class="card-header">
                        <span class="route-label">${routeLabel}</span>
                        ${isSelected ? '<span class="selected-badge">Selected</span>' : ''}
                    </div>
                    <div class="card-stats">
                        <div class="stat">
                            <span class="stat-value">${route.distance.toFixed(1)} km</span>
                            <span class="stat-label">Distance</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${route.stations_count}</span>
                            <span class="stat-label">Stations</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${route.line_changes.length}</span>
                            <span class="stat-label">Changes</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">₹${fare}</span>
                            <span class="stat-label">Fare</span>
                        </div>
                    </div>
                    <button class="select-route-btn" ${isSelected ? 'disabled' : ''}>
                        ${isSelected ? 'Currently Showing' : 'Show This Route'}
                    </button>
                </div>
            `;
        }).join('');
        
        // Add click handlers for route selection
        elements.comparisonCards.querySelectorAll('.comparison-card').forEach((card, index) => {
            card.addEventListener('click', () => {
                // Update selection
                elements.comparisonCards.querySelectorAll('.comparison-card').forEach(c => {
                    c.classList.remove('selected');
                    c.querySelector('.selected-badge')?.remove();
                    c.querySelector('.select-route-btn').disabled = false;
                    c.querySelector('.select-route-btn').textContent = 'Show This Route';
                });
                
                card.classList.add('selected');
                card.querySelector('.card-header').insertAdjacentHTML('beforeend', 
                    '<span class="selected-badge">Selected</span>');
                card.querySelector('.select-route-btn').disabled = true;
                card.querySelector('.select-route-btn').textContent = 'Currently Showing';
                
                // Display selected route
                displayRoute(routes[index]);
            });
        });
        
        // Display first route by default
        displayRoute(routes[0]);
    }
    
    function updateFareDisplay(fare) {
        if (typeof fare === 'object') {
            const displayFare = state.useSmartCard ? fare.smart_card_fare : fare.token_fare;
            elements.fareSpan.textContent = displayFare;
            elements.fareType.textContent = state.useSmartCard ? 'Smart Card Fare' : 'Token Fare';
            
            if (!state.useSmartCard && fare.savings > 0) {
                elements.savingsAmount.textContent = fare.savings;
                elements.fareSavings.classList.remove('hidden');
            } else {
                elements.fareSavings.classList.add('hidden');
            }
        } else {
            elements.fareSpan.textContent = fare;
            elements.fareType.textContent = 'Estimated Fare';
            elements.fareSavings.classList.add('hidden');
        }
    }
    
    function updateLineChangesAlert(lineChanges) {
        if (!lineChanges || lineChanges.length === 0) {
            elements.lineChangesAlert.classList.add('hidden');
            return;
        }
        
        const changeCount = lineChanges.length;
        const changeText = changeCount === 1 
            ? '1 line change required' 
            : `${changeCount} line changes required`;
        
        elements.lineChangesText.textContent = changeText;
        elements.lineChangesAlert.classList.remove('hidden');
    }
    
    // ==================== Metro Map Visualization ====================
    function renderMetroMap(path, stationLines, lineChanges) {
        const mapContainer = elements.metroMap;
        mapContainer.innerHTML = '';
        
        if (path.length === 0) return;
        
        // Create SVG for better line rendering
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'metro-svg');
        svg.setAttribute('viewBox', '0 0 100 100');
        svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
        
        // Calculate positions
        const positions = calculateStationPositions(path);
        
        // Create line change stations set for highlighting
        const lineChangeStations = new Set(lineChanges.map(lc => lc.station));
        
        // Draw lines first (so they appear behind stations)
        const linesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        linesGroup.setAttribute('class', 'metro-lines-group');
        
        for (let i = 0; i < path.length - 1; i++) {
            const stationInfo = stationLines.find(sl => sl.station === path[i]);
            const nextStationInfo = stationLines.find(sl => sl.station === path[i + 1]);
            
            const currentLines = stationInfo?.lines || [];
            const nextLines = nextStationInfo?.lines || [];
            const commonLines = currentLines.filter(l => nextLines.includes(l));
            
            const lineColor = getLineColor(commonLines[0] || currentLines[0] || 'Grey');
            
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', positions[i].x);
            line.setAttribute('y1', positions[i].y);
            line.setAttribute('x2', positions[i + 1].x);
            line.setAttribute('y2', positions[i + 1].y);
            line.setAttribute('stroke', lineColor);
            line.setAttribute('stroke-width', '2');
            line.setAttribute('stroke-linecap', 'round');
            line.setAttribute('class', 'metro-line-segment');
            
            // Add animation
            line.style.animation = `drawLine 0.5s ease-out ${i * 0.1}s forwards`;
            line.style.strokeDasharray = '100';
            line.style.strokeDashoffset = '100';
            
            linesGroup.appendChild(line);
        }
        
        svg.appendChild(linesGroup);
        
        // Draw stations
        const stationsGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        stationsGroup.setAttribute('class', 'metro-stations-group');
        
        path.forEach((station, index) => {
            const pos = positions[index];
            const stationInfo = stationLines.find(sl => sl.station === station);
            const lines = stationInfo?.lines || [];
            const isInterchange = lines.length > 1;
            const isLineChange = lineChangeStations.has(station);
            const isStart = index === 0;
            const isEnd = index === path.length - 1;
            
            // Station group
            const stationGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            stationGroup.setAttribute('class', 'station-group');
            stationGroup.setAttribute('data-station', station);
            
            // Station circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', pos.x);
            circle.setAttribute('cy', pos.y);
            circle.setAttribute('r', isStart || isEnd ? 3.5 : isInterchange ? 3 : 2.5);
            circle.setAttribute('class', `station-circle ${isStart ? 'start' : ''} ${isEnd ? 'end' : ''} ${isLineChange ? 'line-change' : ''}`);
            circle.setAttribute('fill', isStart ? '#43A047' : isEnd ? '#E53935' : '#FFFFFF');
            circle.setAttribute('stroke', isStart ? '#43A047' : isEnd ? '#E53935' : getLineColor(lines[0]));
            circle.setAttribute('stroke-width', '1.5');
            
            // Animation
            circle.style.animation = `popIn 0.3s ease-out ${index * 0.08}s forwards`;
            circle.style.opacity = '0';
            circle.style.transform = 'scale(0)';
            circle.style.transformOrigin = `${pos.x}px ${pos.y}px`;
            
            stationGroup.appendChild(circle);
            
            // Station label - alternate above/below to prevent overlap
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            const isAbove = index % 2 === 0; // Alternate label position
            const labelY = isAbove ? pos.y - 5 : pos.y + 6;
            
            label.setAttribute('x', pos.x);
            label.setAttribute('y', labelY);
            label.setAttribute('class', 'station-label');
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('dominant-baseline', isAbove ? 'auto' : 'hanging');
            label.textContent = truncateStationName(station, 10);
            
            // Show all labels, not just on hover
            label.style.opacity = '1';
            label.style.fontSize = '2.2px';
            label.style.fill = '#333';
            label.style.fontWeight = (isStart || isEnd) ? 'bold' : 'normal';
            
            stationGroup.appendChild(label);
            stationsGroup.appendChild(stationGroup);
        });
        
        svg.appendChild(stationsGroup);
        mapContainer.appendChild(svg);
        
        // Add CSS for animations
        addMapAnimationStyles();
    }
    
    function truncateStationName(name, maxLength = 10) {
        if (name.length <= maxLength) return name;
        return name.substring(0, maxLength - 1) + '…';
    }
    
    function calculateStationPositions(path) {
        const positions = [];
        const count = path.length;
        
        if (count <= 5) {
            // Simple horizontal layout for short routes with more spacing
            for (let i = 0; i < count; i++) {
                positions.push({
                    x: 15 + (i * (70 / Math.max(count - 1, 1))),
                    y: 50
                });
            }
        } else {
            // Serpentine layout for longer routes - fewer stations per row for more spacing
            const stationsPerRow = Math.min(8, Math.ceil(Math.sqrt(count * 1.5)));
            const rows = Math.ceil(count / stationsPerRow);
            const rowHeight = 70 / Math.max(rows, 1);
            
            for (let i = 0; i < count; i++) {
                const row = Math.floor(i / stationsPerRow);
                const col = i % stationsPerRow;
                const isReversedRow = row % 2 === 1;
                
                // Calculate x with padding on sides
                const xSpacing = 70 / Math.max(stationsPerRow - 1, 1);
                const x = isReversedRow 
                    ? 85 - (col * xSpacing)
                    : 15 + (col * xSpacing);
                const y = 20 + (row * rowHeight);
                
                positions.push({ x, y });
            }
        }
        
        return positions;
    }
    
    function getLineColor(lineName) {
        return LINE_COLORS[lineName] || '#757575';
    }
    
    function addMapAnimationStyles() {
        if (document.getElementById('map-animation-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'map-animation-styles';
        style.textContent = `
            @keyframes drawLine {
                to { stroke-dashoffset: 0; }
            }
            @keyframes popIn {
                to { opacity: 1; transform: scale(1); }
            }
            .station-group:hover .station-circle {
                transform: scale(1.3);
                filter: drop-shadow(0 0 3px rgba(0,0,0,0.3));
            }
            .station-group:hover .station-label {
                font-weight: bold;
                font-size: 3px !important;
            }
            .metro-svg {
                width: 100%;
                height: 100%;
                min-height: 300px;
            }
        `;
        document.head.appendChild(style);
    }
    
    // ==================== Station List Rendering ====================
    function renderStationList(path, stationLines, lineChanges) {
        const lineChangeStations = new Map();
        lineChanges.forEach(lc => lineChangeStations.set(lc.station, lc));
        
        elements.pathList.innerHTML = path.map((station, index) => {
            const stationInfo = stationLines.find(sl => sl.station === station);
            const lines = stationInfo?.lines || [];
            const lineChange = lineChangeStations.get(station);
            const isStart = index === 0;
            const isEnd = index === path.length - 1;
            
            let stationClass = 'station-item';
            if (isStart) stationClass += ' start-station';
            if (isEnd) stationClass += ' end-station';
            if (lineChange) stationClass += ' line-change-station';
            
            const lineIndicators = lines.map(line => 
                `<span class="line-badge" style="background-color: ${getLineColor(line)}">${line}</span>`
            ).join('');
            
            let lineChangeHtml = '';
            if (lineChange) {
                lineChangeHtml = `
                    <div class="line-change-notice">
                        <span class="change-icon">🔄</span>
                        Change from <strong>${lineChange.from_lines[0]}</strong> to 
                        <strong>${lineChange.to_lines[0]}</strong> Line
                    </div>
                `;
            }
            
            return `
                <li class="${stationClass}">
                    <div class="station-marker">
                        <span class="marker-dot ${isStart ? 'start' : ''} ${isEnd ? 'end' : ''}"></span>
                        ${index < path.length - 1 ? '<span class="marker-line"></span>' : ''}
                    </div>
                    <div class="station-info">
                        <span class="station-name">${station}</span>
                        <div class="station-lines">${lineIndicators}</div>
                        ${lineChangeHtml}
                    </div>
                    <span class="station-number">${index + 1}</span>
                </li>
            `;
        }).join('');
    }
    
    // ==================== Map Controls ====================
    function zoomMap(delta) {
        state.currentZoom = Math.max(0.5, Math.min(2, state.currentZoom + delta));
        elements.metroMap.style.transform = `scale(${state.currentZoom})`;
    }
    
    function resetMapView() {
        state.currentZoom = 1;
        elements.metroMap.style.transform = 'scale(1)';
    }
    
    // ==================== Utility Functions ====================
    function swapStations() {
        const tempValue = elements.sourceSearch.value;
        const tempHidden = elements.sourceHidden.value;
        
        elements.sourceSearch.value = elements.destinationSearch.value;
        elements.sourceHidden.value = elements.destinationHidden.value;
        
        elements.destinationSearch.value = tempValue;
        elements.destinationHidden.value = tempHidden;
        
        // Animate swap button
        elements.swapBtn.classList.add('rotating');
        setTimeout(() => elements.swapBtn.classList.remove('rotating'), 300);
    }
    
    function setLoadingState(isLoading) {
        const btnText = elements.findRouteBtn.querySelector('.btn-text');
        const btnLoading = elements.findRouteBtn.querySelector('.btn-loading');
        
        if (isLoading) {
            btnText.classList.add('hidden');
            btnLoading.classList.remove('hidden');
            elements.findRouteBtn.disabled = true;
        } else {
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
            elements.findRouteBtn.disabled = false;
        }
    }
    
    function showError(message) {
        elements.errorDiv.innerHTML = `
            <span class="error-icon">⚠️</span>
            <span class="error-text">${message}</span>
        `;
        elements.errorDiv.classList.remove('hidden');
        elements.resultDiv.classList.add('hidden');
        
        // Scroll to error
        elements.errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    function hideError() {
        elements.errorDiv.classList.add('hidden');
    }
    
    // ==================== Initialize ====================
    init();
});
