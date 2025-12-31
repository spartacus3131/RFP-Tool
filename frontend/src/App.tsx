import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import QuickScan from './pages/QuickScan'
import RFPList from './pages/RFPList'
import RFPDetail from './pages/RFPDetail'
import SubConsultants from './pages/SubConsultants'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/quick-scan" element={<QuickScan />} />
        <Route path="/rfps" element={<RFPList />} />
        <Route path="/rfps/:id" element={<RFPDetail />} />
        <Route path="/subconsultants" element={<SubConsultants />} />
      </Routes>
    </Layout>
  )
}

export default App
