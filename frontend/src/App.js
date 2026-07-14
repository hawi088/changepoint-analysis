import React, { useState, useEffect } from 'react';
import PriceChart from './components/PriceChart';
import EventList from './components/EventList';
import MetricsCard from './components/MetricsCard';
import FilterControls from './components/FilterControls';
import { api } from './services/api';
import './App.css';

function App() {
  const [priceData, setPriceData] = useState([]);
  const [events, setEvents] = useState([]);
  const [changePoints, setChangePoints] = useState([]);
  const [eventImpacts, setEventImpacts] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [startDate, setStartDate] = useState('1987-05-20');
  const [endDate, setEndDate] = useState('2022-11-14');
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Loading data...');
      
      const [pricesRes, eventsRes, impactsRes, summaryRes] = await Promise.all([
        api.getPrices(startDate, endDate),
        api.getEvents(),
        api.getEventImpacts(),
        api.getSummary()
      ]);

      console.log('Price data received:', pricesRes.data?.length || 0, 'points');
      console.log('Events received:', eventsRes.data?.length || 0);
      
      // Set the data directly from the response
      const priceArray = Array.isArray(pricesRes.data) ? pricesRes.data : [];
      const eventsArray = Array.isArray(eventsRes.data) ? eventsRes.data : [];
      const impactsArray = Array.isArray(impactsRes.data) ? impactsRes.data : [];
      
      console.log('Price array length:', priceArray.length);
      console.log('Events array length:', eventsArray.length);
      
      setPriceData(priceArray);
      setEvents(eventsArray);
      setEventImpacts(impactsArray);
      setSummary(summaryRes.data || {});
      
    } catch (error) {
      console.error('Error loading data:', error);
      setError('Failed to load data. Please check if the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterApply = (newStartDate, newEndDate) => {
    setStartDate(newStartDate);
    setEndDate(newEndDate);
    loadData();
  };

  const handleEventHighlight = (event) => {
    setSelectedEvent(event);
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error Loading Dashboard</h2>
        <p>{error}</p>
        <button onClick={loadData}>Retry</button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Brent Oil Price Analysis Dashboard</h1>
        <p>Interactive visualization of oil price trends and events</p>
      </header>

      <FilterControls 
        onApply={handleFilterApply} 
        startDate={startDate}
        endDate={endDate}
      />

      <div className="metrics-grid">
        <MetricsCard 
          title="Total Days" 
          value={summary?.total_days || 0} 
          icon=""
        />
        <MetricsCard 
          title="Price Range" 
          value={`$${summary?.price_min || 0} - $${summary?.price_max || 0}`}
          icon=""
        />
        <MetricsCard 
          title="Average Price" 
          value={`$${summary?.price_mean || 0}`}
          icon=""
        />
        <MetricsCard 
          title="Events Recorded" 
          value={summary?.total_events || 0}
          icon=""
        />
      </div>

      <div className="chart-container">
        <h3>Price Chart</h3>
        <p style={{ fontSize: '12px', color: '#999', marginBottom: '10px' }}>
          Data points loaded: {priceData.length}
        </p>
        <PriceChart 
          data={priceData}
          events={events}
          changePoints={changePoints}
          highlightedEvent={selectedEvent}
        />
      </div>

      <div className="dashboard-bottom">
        <div className="events-section">
          <EventList 
            events={events}
            eventImpacts={eventImpacts}
            onEventSelect={handleEventHighlight}
          />
        </div>
        <div className="details-section">
          <h3>Event Impact Summary</h3>
          {eventImpacts.length === 0 ? (
            <p>No impact data available</p>
          ) : (
            <table className="impact-table">
              <thead>
                <tr>
                  <th>Event</th>
                  <th>Date</th>
                  <th>Category</th>
                  <th>Impact %</th>
                </tr>
              </thead>
              <tbody>
                {eventImpacts.slice(0, 10).map((event, idx) => (
                  <tr key={idx} onClick={() => handleEventHighlight(event)}>
                    <td>{event.event}</td>
                    <td>{event.date}</td>
                    <td>
                      <span className={`category-badge ${event.category}`}>
                        {event.category}
                      </span>
                    </td>
                    <td className={event.impact_pct > 0 ? 'positive' : 'negative'}>
                      {event.impact_pct > 0 ? '+' : ''}{event.impact_pct}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;