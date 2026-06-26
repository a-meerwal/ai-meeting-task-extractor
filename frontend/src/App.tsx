import Dashboard from './components/Dashboard'

function App() {
  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
          AI Meeting Task Extractor
        </h1>
        <Dashboard />
      </div>
    </div>
  )
}

export default App
