import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SimulationList from './pages/SimulationList';
import Dashboard from './pages/Dashboard';
import RunHistory from './pages/RunHistory';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SimulationList />} />
        <Route path="/sim/:id" element={<Dashboard />} />
        <Route path="/history" element={<RunHistory />} />
      </Routes>
    </BrowserRouter>
  );
}
