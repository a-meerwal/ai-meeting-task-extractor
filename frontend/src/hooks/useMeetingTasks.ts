import { useState, useEffect } from 'react'
import axios from 'axios'

export default function useMeetingTasks(meetingId: number | null) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!meetingId) return

    let intervalId: ReturnType<typeof setInterval>
    
    const fetchTasks = async () => {
      try {
        setError(null)
        setLoading(true)
        const res = await axios.get(`/api/tasks/${meetingId}`)
        
        if (res.data.status === 'completed') {
          setData(res.data)
          setLoading(false)
          clearInterval(intervalId)
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message)
        setLoading(false)
        clearInterval(intervalId)
      }
    }

    // Initial fetch
    fetchTasks()
    
    // Poll every 3 seconds if not completed
    intervalId = setInterval(fetchTasks, 3000)

    return () => clearInterval(intervalId)
  }, [meetingId])

  const completeTask = async (taskId: number) => {
    try {
      await axios.patch(`/api/tasks/${taskId}/complete`)
      setData((prev: any) => ({
        ...prev,
        tasks: prev.tasks.map((t: any) => t.id === taskId ? { ...t, is_completed: true } : t)
      }))
    } catch (err: any) {
      alert("Failed to complete task")
    }
  }

  const deleteTask = async (taskId: number) => {
    try {
      await axios.delete(`/api/tasks/${taskId}`)
      setData((prev: any) => ({
        ...prev,
        tasks: prev.tasks.filter((t: any) => t.id !== taskId)
      }))
    } catch (err: any) {
      alert("Failed to delete task")
    }
  }

  return { data, loading, error, completeTask, deleteTask }
}
