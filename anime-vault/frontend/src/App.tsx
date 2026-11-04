import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import AnimePage from './pages/AnimePage'
import SearchPage from './pages/SearchPage'
import CollectionPage from './pages/CollectionPage'
import ChatPage from './pages/ChatPage'
import LoginPage from './pages/LoginPage'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="anime/:id" element={<AnimePage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="collection" element={<CollectionPage />} />
        <Route path="chat" element={<ChatPage />} />
      </Route>
    </Routes>
  )
}

export default App
