import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { format } from 'date-fns';

const PriceChart = ({ data = [], events = [], changePoints = [], highlightedEvent = null }) => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    console.log('PriceChart received data:', data?.length || 0, 'points');
    console.log('PriceChart data type:', typeof data);
    console.log('Is data an array?', Array.isArray(data));
    console.log('Sample data:', data?.slice(0, 2));
    
    // Process data when it changes
    if (data && Array.isArray(data) && data.length > 0) {
      const formatted = data.map(d => ({
        ...d,
        Date: new Date(d.Date),
        formattedDate: format(new Date(d.Date), 'MMM yyyy')
      }));
      setChartData(formatted);
      console.log('Chart data loaded:', formatted.length, 'points');
    } else {
      console.log('No data received or data is not an array:', data);
      setChartData([]);
    }
  }, [data]);

  // Check if we have data to display
  if (!chartData || chartData.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: 400,
        color: '#666',
        fontSize: '16px'
      }}>
        <p>No price data available</p>
        <p style={{ fontSize: '12px', color: '#999' }}>
          {data && Array.isArray(data) ? `Received ${data.length} data points` : 'No data received'}
        </p>
      </div>
    );
  }

  // Events for reference lines
  const eventRefs = Array.isArray(events) ? events.map(e => ({
    date: new Date(e.Date),
    event: e.Event,
    category: e.Category
  })) : [];

  // Change points
  const cpRefs = Array.isArray(changePoints) ? changePoints.map(cp => ({
    date: new Date(cp.change_point_date),
    label: 'Change Point'
  })) : [];

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;
    
    return (
      <div style={{ 
        background: 'white', 
        padding: '10px', 
        border: '1px solid #ccc', 
        borderRadius: '4px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
      }}>
        <p style={{ fontWeight: 'bold', margin: 0 }}>
          {format(new Date(label), 'yyyy-MM-dd')}
        </p>
        <p style={{ margin: '5px 0', color: '#1a1a2e' }}>
          Price: ${payload[0]?.value?.toFixed(2) || 'N/A'}
        </p>
      </div>
    );
  };

  return (
    <div style={{ width: '100%', height: 400 }}>
      <ResponsiveContainer>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="Date" 
            tickFormatter={(date) => format(new Date(date), 'MMM yyyy')}
            domain={['auto', 'auto']}
            type="number"
            scale="time"
            tick={{ fontSize: 10 }}
          />
          <YAxis 
            label={{ value: 'Price (USD)', angle: -90, position: 'insideLeft', fontSize: 12 }}
            domain={['auto', 'auto']}
            tick={{ fontSize: 10 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          <Line
            type="monotone"
            dataKey="Price"
            stroke="#2d3436"
            strokeWidth={2}
            dot={false}
            name="Brent Oil Price"
          />
          
          {/* Event markers */}
          {eventRefs.map((evt, idx) => (
            <ReferenceLine
              key={`event-${idx}`}
              x={evt.date}
              stroke={evt.category === 'Conflict' ? '#ff6b6b' : '#feca57'}
              strokeDasharray="3 3"
              label={{
                position: 'top',
                value: evt.event.length > 15 ? evt.event.substring(0, 15) + '...' : evt.event,
                fill: evt.category === 'Conflict' ? '#ff6b6b' : '#feca57',
                fontSize: 8
              }}
            />
          ))}
          
          {/* Change points */}
          {cpRefs.map((cp, idx) => (
            <ReferenceLine
              key={`cp-${idx}`}
              x={cp.date}
              stroke="#e74c3c"
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{
                position: 'top',
                value: 'Change Point',
                fill: '#e74c3c',
                fontSize: 10,
                fontWeight: 'bold'
              }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PriceChart;