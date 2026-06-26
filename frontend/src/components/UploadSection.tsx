import { useState } from 'react'
import axios from 'axios'
import { UploadCloud, Loader2 } from 'lucide-react'

export default function UploadSection({ onUploadSuccess }: { onUploadSuccess: (id: number) => void }) {
  const [title, setTitle] = useState('')
  const [transcript, setTranscript] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleUpload = async () => {
    if (!title || !transcript) return
    
    setLoading(true)
    setError(null)
    try {
      const res = await axios.post('/api/upload-transcript', { title, transcript })
      onUploadSuccess(res.data.id)
      setTranscript('')
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="glass-panel rounded-2xl p-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <UploadCloud className="text-blue-400" />
        New Meeting
      </h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <input 
          type="text" 
          placeholder="Meeting Title (e.g. Q3 Planning)"
          className="w-full bg-slate-800/50 border border-slate-700 rounded-lg p-3 text-slate-200 outline-none focus:border-blue-500 transition-colors"
          value={title}
          onChange={e => setTitle(e.target.value)}
          disabled={loading}
        />
        
        <textarea 
          placeholder="Paste raw meeting transcript here..."
          rows={5}
          className="w-full bg-slate-800/50 border border-slate-700 rounded-lg p-3 text-slate-200 outline-none focus:border-blue-500 transition-colors resize-none"
          value={transcript}
          onChange={e => setTranscript(e.target.value)}
          disabled={loading}
        />
        
        <button 
          onClick={handleUpload}
          disabled={!title || !transcript || loading}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2"
        >
          {loading ? (
            <><Loader2 className="animate-spin" size={18} /> Processing in Background...</>
          ) : (
            'Extract Tasks'
          )}
        </button>
      </div>
    </div>
  )
}
