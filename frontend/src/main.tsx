import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App.tsx'
import OfferPage from './pages/OfferPage.tsx'
import ProjectDescPage from './pages/ProjectDescPage.tsx'
import ImagesPage from './pages/ImagesPage.tsx'
import LoginPage from './pages/LoginPage.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<App />}>
          <Route index element={<OfferPage />} />
          <Route path="project" element={<ProjectDescPage />} />
          <Route path="images" element={<ImagesPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
