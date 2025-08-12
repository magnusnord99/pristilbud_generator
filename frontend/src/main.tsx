import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import OfferPage from './pages/OfferPage.tsx'
import ProjectDescPage from './pages/ProjectDescPage.tsx'
import ImagesPage from './pages/ImagesPage.tsx'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <OfferPage /> },
      { path: 'project', element: <ProjectDescPage /> },
      { path: 'images', element: <ImagesPage /> },
    ],
  },
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
