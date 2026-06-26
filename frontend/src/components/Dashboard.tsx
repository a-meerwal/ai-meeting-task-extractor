import { useState } from 'react'
import UploadSection from './UploadSection'
import TaskDataTable from './TaskDataTable'
import useMeetingTasks from '../hooks/useMeetingTasks'

export default function Dashboard() {
  const [meetingId, setMeetingId] = useState<number | null>(null)
  
  const { data, loading, error, completeTask, deleteTask } = useMeetingTasks(meetingId)

  return (
    <div className="space-y-8">
      <UploadSection onUploadSuccess={(id) => setMeetingId(id)} />
      
      {(meetingId || loading || data) && (
        <TaskDataTable 
          data={data} 
          loading={loading} 
          error={error}
          onComplete={completeTask}
          onDelete={deleteTask}
        />
      )}
    </div>
  )
}
