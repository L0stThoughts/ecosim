import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8080',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

client.interceptors.response.use(
  (res) => res,
  (error) => {
    const message = error.response?.data?.error?.message || error.message || 'Request failed';
    return Promise.reject(new Error(message));
  }
);

export default client;
