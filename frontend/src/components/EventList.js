import React, { useState } from 'react';

const EventList = ({ events, eventImpacts, onEventSelect }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  const categories = ['All', ...new Set(events.map(e => e.Category))];

  const filteredEvents = events.filter(e => {
    const matchesSearch = e.Event.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'All' || e.Category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const getImpact = (eventName) => {
    const impact = eventImpacts.find(e => e.event === eventName);
    return impact ? impact.impact_pct : null;
  };

  return (
    <div>
      <h3>Events</h3>
      <div style={{ marginBottom: '15px' }}>
        <input
          type="text"
          placeholder="Search events..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ padding: '8px', width: '60%', marginRight: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          style={{ padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {filteredEvents.map((event, idx) => {
          const impact = getImpact(event.Event);
          return (
            <div 
              key={idx}
              className="event-list-item"
              onClick={() => onEventSelect(event)}
              style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center',
                borderLeft: `3px solid ${event.Expected_Impact === 'High' ? '#e74c3c' : '#f39c12'}`
              }}
            >
              <div>
                <div style={{ fontWeight: 'bold' }}>{event.Event}</div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {event.Date} · {event.Category}
                </div>
              </div>
              {impact !== null && (
                <div style={{ 
                  fontWeight: 'bold', 
                  color: impact > 0 ? '#2ecc71' : '#e74c3c',
                  background: impact > 0 ? '#d5f5e3' : '#fadbd8',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  fontSize: '14px'
                }}>
                  {impact > 0 ? '+' : ''}{impact}%
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default EventList;