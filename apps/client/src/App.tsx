import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  const [count, setCount] = useState(0)

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
        <div className="container mx-auto px-4 py-8">
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-purple-600 mb-2">
              💇 Salon Flow
            </h1>
            <p className="text-gray-600">client Portal</p>
          </header>
          
          <main className="max-w-md mx-auto bg-white rounded-xl shadow-lg p-6">
            <div className="text-center">
              <p className="text-gray-500 mb-4">
                Welcome to Salon Flow client Portal
              </p>
              <button
                onClick={() => setCount(count => count + 1)}
                className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                Count: {count}
              </button>
            </div>
          </main>
          
          <footer className="text-center mt-8 text-gray-400 text-sm">
            <p>AI-powered Salon Management SaaS</p>
            <p className="mt-1">Environment: Development</p>
          </footer>
        </div>
      </div>
    </QueryClientProvider>
  )
}

export default App
