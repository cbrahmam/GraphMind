import { useState, useEffect } from 'react'
import { Users, Layers, Shield } from 'lucide-react'
import { api } from '../api/client'

export default function SettingsPage() {
  const [tab, setTab] = useState('workspaces')
  const [workspaces, setWorkspaces] = useState([])
  const [users, setUsers] = useState([])
  const [newWsName, setNewWsName] = useState('')
  const [regForm, setRegForm] = useState({ username: '', password: '', role: 'viewer' })
  const [loginForm, setLoginForm] = useState({ username: '', password: '' })
  const [authToken, setAuthToken] = useState(null)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    api.getWorkspaces().then(setWorkspaces).catch(() => {})
  }, [])

  const createWs = async () => {
    if (!newWsName.trim()) return
    await api.createWorkspace(newWsName)
    setNewWsName('')
    api.getWorkspaces().then(setWorkspaces)
  }

  const switchWs = async (id) => {
    await api.setActiveWorkspace(id)
    setMessage(`Switched to workspace`)
  }

  const register = async () => {
    try {
      await api.register(regForm.username, regForm.password, regForm.role)
      setMessage('User created')
      setRegForm({ username: '', password: '', role: 'viewer' })
    } catch (e) {
      setMessage(`Error: ${e.message}`)
    }
  }

  const login = async () => {
    try {
      const result = await api.login(loginForm.username, loginForm.password)
      setAuthToken(result.token)
      setMessage(`Logged in as ${result.username} (${result.role})`)
    } catch (e) {
      setMessage(`Error: ${e.message}`)
    }
  }

  return (
    <div className="p-6 max-w-3xl space-y-6">
      <h2 className="text-2xl font-bold text-white">Settings</h2>

      <div className="flex gap-2">
        {[
          { key: 'workspaces', icon: Layers, label: 'Workspaces' },
          { key: 'auth', icon: Shield, label: 'Auth & Users' },
        ].map(({ key, icon: Icon, label }) => (
          <button key={key} onClick={() => setTab(key)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm ${tab === key ? 'bg-purple-500/10 text-purple-400' : 'text-gray-400'}`}>
            <Icon className="w-3.5 h-3.5" /> {label}
          </button>
        ))}
      </div>

      {message && <div className={`p-3 rounded-lg text-sm ${message.startsWith('Error') ? 'bg-red-500/10 text-red-400' : 'bg-green-500/10 text-green-400'}`}>{message}</div>}

      {tab === 'workspaces' && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <input value={newWsName} onChange={e => setNewWsName(e.target.value)} placeholder="New workspace name" className="flex-1 bg-[#161b22] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200 outline-none" />
            <button onClick={createWs} className="px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm">Create</button>
          </div>
          <div className="space-y-2">
            {workspaces.map(ws => (
              <div key={ws.id} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 flex items-center justify-between">
                <div>
                  <span className="text-sm text-gray-200">{ws.name}</span>
                  {ws.description && <span className="ml-2 text-xs text-gray-500">{ws.description}</span>}
                </div>
                <button onClick={() => switchWs(ws.id)} className="text-xs text-purple-400 hover:text-purple-300">Switch</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === 'auth' && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 space-y-3">
            <h3 className="text-sm font-medium text-gray-400">Register</h3>
            <input value={regForm.username} onChange={e => setRegForm(p => ({...p, username: e.target.value}))} placeholder="Username" className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200 outline-none" />
            <input type="password" value={regForm.password} onChange={e => setRegForm(p => ({...p, password: e.target.value}))} placeholder="Password" className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200 outline-none" />
            <select value={regForm.role} onChange={e => setRegForm(p => ({...p, role: e.target.value}))} className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200">
              <option value="viewer">Viewer</option>
              <option value="editor">Editor</option>
              <option value="admin">Admin</option>
            </select>
            <button onClick={register} className="w-full py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm">Register</button>
          </div>
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 space-y-3">
            <h3 className="text-sm font-medium text-gray-400">Login</h3>
            <input value={loginForm.username} onChange={e => setLoginForm(p => ({...p, username: e.target.value}))} placeholder="Username" className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200 outline-none" />
            <input type="password" value={loginForm.password} onChange={e => setLoginForm(p => ({...p, password: e.target.value}))} placeholder="Password" className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200 outline-none" />
            <button onClick={login} className="w-full py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm">Login</button>
            {authToken && <p className="text-xs text-green-400 truncate">Token: {authToken}</p>}
          </div>
        </div>
      )}
    </div>
  )
}
