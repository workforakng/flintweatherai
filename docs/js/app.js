// FlintWeatherAI - Frontend JavaScript
// Author: AkNG
// Version: 1.0

let currentWeatherData = null;
let currentTab = 'overview';
let temperatureUnit = 'C';
let isDarkTheme = false;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌤️ FlintWeatherAI v1.0 Initialized');
    loadThemePreference();
    loadUnitPreference();
    loadWeather();
});

// Theme Management
function loadThemePreference() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    isDarkTheme = savedTheme === 'dark';
    updateTheme();
}

function toggleTheme() {
    isDarkTheme = !isDarkTheme;
    updateTheme();
    localStorage.setItem('theme', isDarkTheme ? 'dark' : 'light');
}

function updateTheme() {
    document.documentElement.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
    const track = document.querySelector('.theme-toggle-track');
    if (track) {
        track.classList.toggle('active', isDarkTheme);
    }
}

// Unit Management
function loadUnitPreference() {
    temperatureUnit = localStorage.getItem('unit') || 'C';
    const unitSelect = document.getElementById('unitSelect');
    if (unitSelect) unitSelect.value = temperatureUnit;
}

function changeUnit(unit) {
    temperatureUnit = unit;
    localStorage.setItem('unit', unit);
    if (currentWeatherData) {
        renderWeatherData(currentWeatherData);
    }
}

// Settings Panel
function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    panel.classList.toggle('active');
}

// Tab Navigation
function switchTab(tabName) {
    currentTab = tabName;
    
    // Update tab buttons
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Re-render content
    if (currentWeatherData) {
        renderWeatherData(currentWeatherData);
    }
}

// Weather Loading
async function loadWeather() {
    showLoader('Getting your location...');
    
    if (!navigator.geolocation) {
        showError('Geolocation not supported');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const { latitude, longitude } = position.coords;
            await fetchWeatherData(latitude, longitude);
        },
        (error) => {
            console.error('Geolocation error:', error);
            showError('Location access denied. Please search manually.');
        }
    );
}

async function fetchWeatherData(lat, lon) {
    try {
        showLoader('Fetching weather data...');
        
        const response = await fetch('/api/weather', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: lat, longitude: lon })
        });
        
        if (!response.ok) {
            throw new Error('Weather fetch failed');
        }
        
        const data = await response.json();
        currentWeatherData = data;
        renderWeatherData(data);
        
    } catch (error) {
        console.error('Weather fetch error:', error);
        showError('Failed to load weather data. Please try again.');
    }
}

// Search Functionality
async function performSearch() {
    const input = document.getElementById('searchInput');
    const query = input.value.trim();
    
    if (!query) return;
    
    try {
        showLoader('Searching locations...');
        
        const response = await fetch('/api/search-location', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            const first = data.results[0];
            await fetchWeatherData(first.latitude, first.longitude);
            input.value = '';
        } else {
            showError('No locations found. Try another search.');
        }
        
    } catch (error) {
        console.error('Search error:', error);
        showError('Search failed. Please try again.');
    }
}

// Refresh Weather
async function refreshWeather() {
    if (!currentWeatherData) {
        loadWeather();
        return;
    }
    
    const location = currentWeatherData.location;
    if (location) {
        await fetchWeatherData(location.latitude, location.longitude);
    }
}

// Render Weather Data
function renderWeatherData(data) {
    const mainContent = document.getElementById('mainContent');
    
    switch (currentTab) {
        case 'overview':
            mainContent.innerHTML = renderOverviewTab(data);
            break;
        case 'hourly':
            mainContent.innerHTML = renderHourlyTab(data);
            loadHourlyForecast(data.location.latitude, data.location.longitude);
            break;
        case 'forecast':
            mainContent.innerHTML = renderForecastTab(data);
            break;
        case 'details':
            mainContent.innerHTML = renderDetailsTab(data);
            break;
    }
}

// Overview Tab
function renderOverviewTab(data) {
    const { current_weather, location, weather_tips, forecast } = data;
    const temp = getTemperature(current_weather.temperature_celsius);
    const feelsLike = getTemperature(current_weather.feels_like_celsius);
    
    return `
        <!-- Location Card -->
        <div class="weather-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 24px;">
                <div>
                    <h2 style="font-size: 2rem; font-weight: 800; color: var(--text-1); margin-bottom: 4px;">
                        ${location.city}
                    </h2>
                    <p style="color: var(--text-3); font-size: 1rem;">
                        ${location.locality} • ${location.country}
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 3.5rem; font-weight: 900; color: var(--primary); line-height: 1;">
                        ${temp}
                    </div>
                    <p style="color: var(--text-3); margin-top: 4px;">
                        Feels like ${feelsLike}
                    </p>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; gap: 16px; padding: 20px; background: var(--bg-2); border-radius: var(--radius); margin-bottom: 20px;">
                <i class="fas ${getWeatherIcon(current_weather.condition)} fa-3x" style="color: var(--primary);"></i>
                <div>
                    <h3 style="font-size: 1.5rem; font-weight: 700; color: var(--text-1);">
                        ${current_weather.condition}
                    </h3>
                    <p style="color: var(--text-2);">
                        ${current_weather.description}
                    </p>
                </div>
            </div>
            
            <!-- Weather Metrics Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px;">
                ${renderMetricCard('💧', 'Humidity', `${current_weather.humidity_percent}%`)}
                ${renderMetricCard('💨', 'Wind', `${current_weather.wind_speed_kmh} km/h`)}
                ${renderMetricCard('🌡️', 'Pressure', `${current_weather.pressure_mb} mb`)}
                ${renderMetricCard('👁️', 'Visibility', `${current_weather.visibility_km} km`)}
                ${renderMetricCard('☀️', 'UV Index', current_weather.uv_index)}
                ${renderMetricCard('☁️', 'Cloud Cover', `${current_weather.cloud_cover_percent}%`)}
            </div>
        </div>
        
        <!-- Weather Tips -->
        <div class="weather-card">
            <h3 style="font-size: 1.3rem; font-weight: 700; color: var(--text-1); margin-bottom: 16px;">
                <i class="fas fa-lightbulb"></i> Weather Tips
            </h3>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                ${weather_tips.map(tip => `
                    <div style="padding: 12px 16px; background: var(--bg-2); border-radius: var(--radius); border-left: 4px solid var(--primary);">
                        ${tip}
                    </div>
                `).join('')}
            </div>
        </div>
        
        <!-- 3-Day Forecast Preview -->
        <div class="weather-card">
            <h3 style="font-size: 1.3rem; font-weight: 700; color: var(--text-1); margin-bottom: 16px;">
                <i class="fas fa-calendar-days"></i> 3-Day Outlook
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                ${renderForecastCard('Today', forecast.today, 'fa-sun')}
                ${renderForecastCard('Tomorrow', forecast.tomorrow, 'fa-cloud-sun')}
                ${renderForecastCard('Day After', forecast.day_after, 'fa-cloud')}
            </div>
        </div>
    `;
}

// Hourly Tab
function renderHourlyTab(data) {
    return `
        <div class="weather-card">
            <h3 style="font-size: 1.3rem; font-weight: 700; color: var(--text-1); margin-bottom: 20px;">
                <i class="fas fa-clock"></i> 24-Hour Forecast
            </h3>
            <div id="hourlyContent">
                <div class="loader-container">
                    <div class="spinner"></div>
                    <p class="loader-text">Loading hourly forecast...</p>
                </div>
            </div>
        </div>
    `;
}

async function loadHourlyForecast(lat, lon) {
    try {
        const response = await fetch('/api/hourly', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: lat, longitude: lon })
        });
        
        const data = await response.json();
        const hourlyContent = document.getElementById('hourlyContent');
        
        hourlyContent.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 16px;">
                ${data.hourly_forecast.slice(0, 12).map(hour => `
                    <div style="padding: 16px; background: var(--bg-2); border-radius: var(--radius); text-align: center;">
                        <div style="font-weight: 600; color: var(--text-1); margin-bottom: 8px;">
                            ${hour.hour}
                        </div>
                        <i class="fas ${getWeatherIcon(hour.condition)} fa-2x" style="color: var(--primary); margin: 8px 0;"></i>
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary); margin: 8px 0;">
                            ${getTemperature(hour.temperature_celsius)}
                        </div>
                        <div style="color: var(--text-3); font-size: 0.875rem;">
                            💧 ${hour.precipitation_chance}%
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Hourly forecast error:', error);
        document.getElementById('hourlyContent').innerHTML = `
            <p style="text-align: center; color: var(--text-3);">
                Failed to load hourly forecast
            </p>
        `;
    }
}

// Forecast Tab
function renderForecastTab(data) {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const icons = ['fa-sun', 'fa-cloud-sun', 'fa-cloud', 'fa-cloud-rain', 'fa-cloud-sun', 'fa-sun', 'fa-cloud'];
    
    return `
        <div class="weather-card">
            <h3 style="font-size: 1.3rem; font-weight: 700; color: var(--text-1); margin-bottom: 20px;">
                <i class="fas fa-calendar-week"></i> 7-Day Forecast
            </h3>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                ${days.map((day, i) => {
                    const temp = 20 + Math.random() * 10;
                    return `
                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 16px; background: var(--bg-2); border-radius: var(--radius);">
                            <div style="display: flex; align-items: center; gap: 16px; flex: 1;">
                                <i class="fas ${icons[i]} fa-2x" style="color: var(--primary); width: 40px;"></i>
                                <div>
                                    <div style="font-weight: 600; color: var(--text-1);">${day}</div>
                                    <div style="color: var(--text-3); font-size: 0.875rem;">Partly Cloudy</div>
                                </div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 16px;">
                                <div style="color: var(--text-3);">💧 ${Math.floor(Math.random() * 40)}%</div>
                                <div style="font-size: 1.3rem; font-weight: 700; color: var(--primary);">
                                    ${getTemperature(temp)}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        </div>
    `;
}

// Details Tab
function renderDetailsTab(data) {
    const { current_weather, sun_times } = data;
    
    return `
        <div class="weather-card">
            <h3 style="font-size: 1.3rem; font-weight: 700; color: var(--text-1); margin-bottom: 20px;">
                <i class="fas fa-chart-line"></i> Detailed Metrics
            </h3>
            
            <div style="display: grid; gap: 24px;">
                <!-- Temperature Details -->
                <div>
                    <h4 style="font-weight: 600; color: var(--text-1); margin-bottom: 12px;">🌡️ Temperature</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                        ${renderDetailItem('Current', getTemperature(current_weather.temperature_celsius))}
                        ${renderDetailItem('Feels Like', getTemperature(current_weather.feels_like_celsius))}
                        ${renderDetailItem('Fahrenheit', `${current_weather.temperature_fahrenheit}°F`)}
                    </div>
                </div>
                
                <!-- Wind Details -->
                <div>
                    <h4 style="font-weight: 600; color: var(--text-1); margin-bottom: 12px;">💨 Wind</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                        ${renderDetailItem('Speed', `${current_weather.wind_speed_kmh} km/h`)}
                        ${renderDetailItem('Direction', current_weather.wind_direction)}
                    </div>
                </div>
                
                <!-- Atmospheric -->
                <div>
                    <h4 style="font-weight: 600; color: var(--text-1); margin-bottom: 12px;">🌍 Atmospheric</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                        ${renderDetailItem('Pressure', `${current_weather.pressure_mb} mb`)}
                        ${renderDetailItem('Humidity', `${current_weather.humidity_percent}%`)}
                        ${renderDetailItem('Visibility', `${current_weather.visibility_km} km`)}
                        ${renderDetailItem('Cloud Cover', `${current_weather.cloud_cover_percent}%`)}
                    </div>
                </div>
                
                <!-- Sun & Moon -->
                <div>
                    <h4 style="font-weight: 600; color: var(--text-1); margin-bottom: 12px;">☀️ Sun & Moon</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                        ${renderDetailItem('Sunrise', sun_times.sunrise)}
                        ${renderDetailItem('Sunset', sun_times.sunset)}
                        ${renderDetailItem('Moon Phase', sun_times.moon_phase)}
                        ${renderDetailItem('UV Index', current_weather.uv_index)}
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Helper Render Functions
function renderMetricCard(icon, label, value) {
    return `
        <div style="padding: 16px; background: var(--bg-2); border-radius: var(--radius); text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 8px;">${icon}</div>
            <div style="color: var(--text-3); font-size: 0.875rem; margin-bottom: 4px;">${label}</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: var(--text-1);">${value}</div>
        </div>
    `;
}

function renderForecastCard(day, description, icon) {
    return `
        <div style="padding: 20px; background: var(--bg-2); border-radius: var(--radius); text-align: center;">
            <i class="fas ${icon} fa-3x" style="color: var(--primary); margin-bottom: 12px;"></i>
            <div style="font-weight: 600; color: var(--text-1); margin-bottom: 8px;">${day}</div>
            <div style="color: var(--text-2); font-size: 0.875rem;">${description}</div>
        </div>
    `;
}

function renderDetailItem(label, value) {
    return `
        <div style="padding: 12px; background: var(--bg-2); border-radius: var(--radius);">
            <div style="color: var(--text-3); font-size: 0.875rem; margin-bottom: 4px;">${label}</div>
            <div style="font-weight: 600; color: var(--text-1);">${value}</div>
        </div>
    `;
}

// Utility Functions
function getTemperature(celsius) {
    if (temperatureUnit === 'F') {
        const fahrenheit = Math.round((celsius * 9/5) + 32);
        return `${fahrenheit}°F`;
    }
    return `${Math.round(celsius)}°C`;
}

function getWeatherIcon(condition) {
    if (!condition) return 'fa-cloud';
    const c = condition.toLowerCase();
    if (c.includes('clear') || c.includes('sunny')) return 'fa-sun';
    if (c.includes('rain')) return 'fa-cloud-rain';
    if (c.includes('snow')) return 'fa-snowflake';
    if (c.includes('cloud')) return 'fa-cloud';
    if (c.includes('storm') || c.includes('thunder')) return 'fa-bolt';
    if (c.includes('fog') || c.includes('mist')) return 'fa-smog';
    if (c.includes('wind')) return 'fa-wind';
    return 'fa-cloud';
}

function showLoader(message = 'Loading...') {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="loader-container">
            <div class="spinner"></div>
            <p class="loader-text">${message}</p>
        </div>
    `;
}

function showError(message) {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="weather-card" style="text-align: center; padding: 60px 20px;">
            <i class="fas fa-exclamation-triangle fa-4x" style="color: var(--danger); margin-bottom: 20px;"></i>
            <h3 style="color: var(--text-1); margin-bottom: 12px;">Oops!</h3>
            <p style="color: var(--text-2); margin-bottom: 24px;">${message}</p>
            <button onclick="loadWeather()" style="padding: 12px 24px; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border: none; border-radius: var(--radius); cursor: pointer; font-weight: 600;">
                Try Again
            </button>
        </div>
    `;
}

// Chat Functions
function toggleChat() {
    const panel = document.getElementById('chatPanel');
    panel.classList.toggle('active');
}

async function sendChat() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message || !currentWeatherData) return;
    
    // Add user message
    addChatMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator
    const typingId = addChatMessage('Thinking...', 'bot', true);
    
    try {
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                weather_data: currentWeatherData
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        document.getElementById(typingId)?.remove();
        
        // Add bot response
        addChatMessage(data.response, 'bot');
        
    } catch (error) {
        document.getElementById(typingId)?.remove();
        addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

function addChatMessage(text, sender, isTyping = false) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageId = `msg-${Date.now()}`;
    
    const avatar = sender === 'bot' ? 
        '<div class="chat-avatar bot-avatar"><i class="fas fa-robot"></i></div>' :
        '<div class="chat-avatar user-avatar"><i class="fas fa-user"></i></div>';
    
    const messageHtml = `
        <div class="chat-msg ${sender}" id="${messageId}">
            ${avatar}
            <div class="chat-bubble">${text}</div>
        </div>
    `;
    
    messagesDiv.insertAdjacentHTML('beforeend', messageHtml);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    return messageId;
}

// Clear Cache
async function clearCache() {
    try {
        await fetch('/api/cache-clear', { method: 'POST' });
        alert('Cache cleared successfully!');
    } catch (error) {
        alert('Failed to clear cache');
    }
}

// Auto-resize chat input
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });
    }
});

console.log('✅ FlintWeatherAI Frontend Loaded');

// Load 7-day forecast
async function load7DayForecast(lat, lon) {
    try {
        const response = await fetch('/api/forecast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: lat, longitude: lon })
        });
        
        const data = await response.json();
        const forecastContent = document.getElementById('forecastContent');
        
        if (data.forecast && data.forecast.length > 0) {
            forecastContent.innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    ${data.forecast.map(day => `
                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 16px; background: var(--bg-2); border-radius: var(--radius);">
                            <div style="display: flex; align-items: center; gap: 16px; flex: 1;">
                                <i class="fas ${getWeatherIcon(day.condition)} fa-2x" style="color: var(--primary); width: 40px;"></i>
                                <div>
                                    <div style="font-weight: 600; color: var(--text-1);">${day.day}</div>
                                    <div style="color: var(--text-3); font-size: 0.875rem;">${day.condition}</div>
                                </div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 16px;">
                                <div style="color: var(--text-3);">💧 ${day.rain_chance}%</div>
                                <div style="font-size: 1.1rem; color: var(--text-2);">${getTemperature(day.min_temp_c)}</div>
                                <div style="font-size: 1.3rem; font-weight: 700; color: var(--primary);">${getTemperature(day.max_temp_c)}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <div style="margin-top: 24px; padding: 20px; background: var(--bg-2); border-radius: var(--radius);">
                    <h4 style="font-weight: 600; color: var(--text-1); margin-bottom: 12px;">
                        <i class="fas fa-wind"></i> Air Quality Index
                    </h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;">
                        <div style="padding: 12px; background: var(--bg-3); border-radius: var(--radius); text-align: center;">
                            <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">${data.air_quality.us_epa_index || 1}</div>
                            <div style="color: var(--text-3); font-size: 0.875rem;">US EPA Index</div>
                        </div>
                        <div style="padding: 12px; background: var(--bg-3); border-radius: var(--radius); text-align: center;">
                            <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">${data.air_quality.pm2_5 || 0}</div>
                            <div style="color: var(--text-3); font-size: 0.875rem;">PM2.5</div>
                        </div>
                        <div style="padding: 12px; background: var(--bg-3); border-radius: var(--radius); text-align: center;">
                            <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">${data.air_quality.pm10 || 0}</div>
                            <div style="color: var(--text-3); font-size: 0.875rem;">PM10</div>
                        </div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('7-day forecast error:', error);
        document.getElementById('forecastContent').innerHTML = '<p style="text-align: center; color: var(--text-3);">Failed to load forecast</p>';
    }
}

// Update switchTab to load forecast
const originalSwitchTab = switchTab;
switchTab = function(tabName) {
    originalSwitchTab(tabName);
    if (tabName === 'forecast' && currentWeatherData) {
        load7DayForecast(currentWeatherData.location.latitude, currentWeatherData.location.longitude);
    }
};
