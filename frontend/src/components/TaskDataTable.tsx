import { CheckCircle, Trash2, Clock, User, CheckCircle2 } from 'lucide-react'

export default function TaskDataTable({ data, loading, error, onComplete, onDelete }: any) {
  if (error) {
    return (
      <div className="glass-panel rounded-2xl p-8 text-center text-red-300">
        <p>Something went wrong: {error}</p>
      </div>
    )
  }

  if (loading && !data) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center">
        <div className="flex justify-center mb-4">
          <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <p className="text-slate-400 animate-pulse">AI is currently analyzing transcript and extracting tasks...</p>
      </div>
    )
  }

  if (!data?.tasks?.length) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center">
        <p className="text-slate-400">No tasks extracted.</p>
      </div>
    )
  }

  return (
    <div className="glass-panel rounded-2xl overflow-hidden shadow-2xl">
      <div className="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
        <h2 className="text-xl font-semibold">{data.title} - Extracted Tasks</h2>
        <span className="bg-emerald-500/20 text-emerald-300 px-3 py-1 rounded-full text-sm font-medium">
          {data.tasks.length} Tasks
        </span>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-slate-800/50">
              <th className="p-4 font-medium text-slate-400 border-b border-white/10">Status</th>
              <th className="p-4 font-medium text-slate-400 border-b border-white/10 w-1/2">Task</th>
              <th className="p-4 font-medium text-slate-400 border-b border-white/10">Assignee</th>
              <th className="p-4 font-medium text-slate-400 border-b border-white/10">Deadline</th>
              <th className="p-4 font-medium text-slate-400 border-b border-white/10 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {data.tasks.map((task: any) => (
              <tr key={task.id} className="hover:bg-white/5 transition-colors">
                <td className="p-4">
                  {task.is_completed ? (
                    <CheckCircle2 className="text-emerald-400" size={20} />
                  ) : (
                    <div className="h-5 w-5 rounded-full border-2 border-slate-600"></div>
                  )}
                </td>
                <td className={`p-4 ${task.is_completed ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                  {task.task_description}
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2 text-slate-400 text-sm">
                    <User size={14} />
                    {task.assignee}
                  </div>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2 text-slate-400 text-sm">
                    <Clock size={14} />
                    {task.deadline}
                  </div>
                </td>
                <td className="p-4 text-right space-x-2">
                  {!task.is_completed && (
                    <button 
                      onClick={() => onComplete(task.id)}
                      className="p-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-lg transition-colors"
                      title="Mark Complete"
                    >
                      <CheckCircle size={16} />
                    </button>
                  )}
                  <button 
                    onClick={() => onDelete(task.id)}
                    className="p-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors"
                    title="Delete Task"
                  >
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
