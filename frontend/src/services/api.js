import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export const api = {
  getPrices: async (startDate, endDate) => {
    try {
      let url = `${API_BASE}/prices`;
      if (startDate && endDate) {
        url += `?start_date=${startDate}&end_date=${endDate}`;
      }
      const response = await axios.get(url);
      console.log('Prices response status:', response.status);
      console.log('Prices data type:', typeof response.data);
      console.log('Prices data length:', response.data?.length);
      return response;
    } catch (error) {
      console.error('Error fetching prices:', error);
      return { data: [] };
    }
  },

  getEvents: async () => {
    try {
      const response = await axios.get(`${API_BASE}/events`);
      console.log('Events response status:', response.status);
      console.log('Events data type:', typeof response.data);
      console.log('Events data length:', response.data?.length);
      return response;
    } catch (error) {
      console.error('Error fetching events:', error);
      return { data: [] };
    }
  },

  getEventImpacts: async () => {
    try {
      const response = await axios.get(`${API_BASE}/event-impacts`);
      return response;
    } catch (error) {
      console.error('Error fetching event impacts:', error);
      return { data: [] };
    }
  },

  getSummary: async () => {
    try {
      const response = await axios.get(`${API_BASE}/summary`);
      return response;
    } catch (error) {
      console.error('Error fetching summary:', error);
      return { data: {} };
    }
  }
};