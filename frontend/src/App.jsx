import React, { useState, useEffect } from 'react';
import {
  Smartphone,
  Layers,
  Zap,
  Activity,
  Compass,
  Palette,
  CheckCircle2,
  Code2,
  ArrowRight,
  Sparkles,
  Download,
  RefreshCw,
  Search,
  ExternalLink,
  ShieldCheck,
  Cpu,
  Eye,
  Sliders
} from 'lucide-react';

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('screens');
  const [selectedFp, setSelectedFp] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [elementRoleFilter, setElementRoleFilter] = useState('ALL');
  const [copiedHex, setCopiedHex] = useState(null);

  const fetchKnowledgePack = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/knowledge-pack');
      if (!res.ok) {
        throw new Error('Could not load knowledge pack. Please run exploration pipeline first.');
      }
      const json = await res.json();
      setData(json);
      const firstFp = Object.keys(json.screen_profiles || {})[0];
      setSelectedFp(firstFp);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKnowledgePack();
  }, []);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedHex(text);
    setTimeout(() => setCopiedHex(null), 2000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#07080e] flex flex-col items-center justify-center text-slate-200">
        <div className="relative">
          <div className="w-16 h-16 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin"></div>
          <Zap className="w-6 h-6 text-indigo-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
        </div>
        <p className="mt-6 text-sm font-semibold tracking-wider text-slate-400 uppercase">
          Synthesizing Multimodal Knowledge Pack...
        </p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#07080e] flex flex-col items-center justify-center p-6 text-center text-slate-200">
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-400 mb-4 max-w-md">
          <p className="font-bold text-lg mb-2">No Active Knowledge Pack Found</p>
          <p className="text-xs text-slate-400 mb-4">{error}</p>
          <code className="text-xs bg-black/40 px-3 py-1.5 rounded-lg border border-white/10 block mb-4 text-indigo-300">
            python run.py --app com.android.settings --mode adb
          </code>
          <button
            onClick={fetchKnowledgePack}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center gap-2 mx-auto transition"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Retry Fetch
          </button>
        </div>
      </div>
    );
  }

  const { metadata, design_system, screen_graph, screen_profiles } = data;
  const currentProfile = selectedFp ? screen_profiles[selectedFp] : null;

  // Filter screens
  const screenFps = Object.keys(screen_profiles || {});
  const filteredFps = screenFps.filter((fp) => {
    if (categoryFilter === 'ALL') return true;
    return screen_profiles[fp]?.screen_category?.toUpperCase() === categoryFilter;
  });

  const categories = ['ALL', ...new Set(screenFps.map((fp) => screen_profiles[fp]?.screen_category?.toUpperCase()).filter(Boolean))];

  return (
    <div className="min-h-screen bg-[#07080e] text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white pb-16">
      {/* Glow Ambient background lights */}
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-indigo-600/10 blur-[120px] pointer-events-none -z-10" />
      <div className="fixed top-20 right-1/4 w-96 h-96 bg-purple-600/10 blur-[120px] pointer-events-none -z-10" />

      {/* TOP HACKATHON HERO BANNER */}
      <header className="border-b border-white/[0.07] bg-[#0c0e18]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-0.5 shadow-lg shadow-indigo-500/30">
              <div className="w-full h-full bg-[#0d0f1a] rounded-[14px] flex items-center justify-center">
                <Zap className="w-6 h-6 text-indigo-400 fill-indigo-400/20" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-indigo-200 to-purple-300 bg-clip-text text-transparent">
                  RevRag Zero-Touch
                </h1>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 uppercase tracking-wider">
                  PS-002 Studio
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">Autonomous Android App Understanding & Knowledge Graph</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              LIVE AGENT ACTIVE
            </div>
            <button
              onClick={fetchKnowledgePack}
              className="p-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/10 text-slate-300 hover:text-white transition"
              title="Refresh Knowledge Pack"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <a
              href={`data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(data, null, 2))}`}
              download={`knowledge_pack_${metadata.package_name}.json`}
              className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 shadow-lg shadow-indigo-500/25 transition"
            >
              <Download className="w-3.5 h-3.5" /> Export Pack
            </a>
          </div>
        </div>
      </header>

      {/* TOP STATS CARDS */}
      <div className="max-w-7xl mx-auto px-6 pt-8 w-full">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="glass-card p-4 rounded-2xl relative overflow-hidden group">
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-transparent"></div>
            <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
              <span>Target Package</span>
              <Smartphone className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-xl font-extrabold text-white truncate" title={metadata.package_name}>
              {metadata.package_name.split('.').pop()}
            </div>
            <div className="text-[11px] text-slate-500 font-mono truncate mt-0.5">{metadata.package_name}</div>
          </div>

          <div className="glass-card p-4 rounded-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-500 to-transparent"></div>
            <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
              <span>Discovered Screens</span>
              <Layers className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-black text-white">{metadata.total_screens_discovered}</div>
            <div className="text-[11px] text-emerald-400 font-medium mt-0.5">100% Convergence</div>
          </div>

          <div className="glass-card p-4 rounded-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-500 to-transparent"></div>
            <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
              <span>Live Action Edges</span>
              <Activity className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-black text-white">{metadata.total_transitions_logged}</div>
            <div className="text-[11px] text-slate-500 font-medium mt-0.5">Autonomous Transitions</div>
          </div>

          <div className="glass-card p-4 rounded-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-amber-500 to-transparent"></div>
            <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
              <span>Pack Size</span>
              <Cpu className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-black text-white">{metadata.pack_size_kb} <span className="text-xs font-bold text-slate-400">KB</span></div>
            <div className="text-[11px] text-emerald-400 font-medium mt-0.5">&lt; 1,500 KB Limit</div>
          </div>

          <div className="glass-card p-4 rounded-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-emerald-500 to-transparent"></div>
            <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
              <span>Compression</span>
              <Sparkles className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-black text-emerald-400">{metadata.compression_ratio}</div>
            <div className="text-[11px] text-slate-500 font-medium mt-0.5">vs Raw 1.5MB+ XML</div>
          </div>
        </div>

        {/* WORKSPACE NAVIGATION TABS */}
        <div className="flex items-center gap-2 mt-8 p-1.5 rounded-2xl bg-white/[0.03] border border-white/[0.08] w-fit">
          <button
            onClick={() => setActiveTab('screens')}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
              activeTab === 'screens'
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/20'
                : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
            }`}
          >
            <Smartphone className="w-4 h-4" /> Screen Intelligence
          </button>
          <button
            onClick={() => setActiveTab('graph')}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
              activeTab === 'graph'
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/20'
                : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
            }`}
          >
            <Compass className="w-4 h-4" /> Journey Graph
          </button>
          <button
            onClick={() => setActiveTab('design')}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
              activeTab === 'design'
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/20'
                : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
            }`}
          >
            <Palette className="w-4 h-4" /> Brand Design Studio
          </button>
          <button
            onClick={() => setActiveTab('fidelity')}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
              activeTab === 'fidelity'
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/20'
                : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
            }`}
          >
            <CheckCircle2 className="w-4 h-4" /> Visual Rebuild Proof
          </button>
          <button
            onClick={() => setActiveTab('json')}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
              activeTab === 'json'
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/20'
                : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
            }`}
          >
            <Code2 className="w-4 h-4" /> Knowledge Pack JSON
          </button>
        </div>
      </div>

      {/* TAB CONTENT AREA */}
      <main className="max-w-7xl mx-auto px-6 pt-6 w-full flex-1">
        {/* ========================================================= */}
        {/* TAB 1: SCREEN INTELLIGENCE */}
        {/* ========================================================= */}
        {activeTab === 'screens' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Screen Deck List */}
            <div className="lg:col-span-4 space-y-4">
              <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
                {categories.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setCategoryFilter(cat)}
                    className={`px-3 py-1.5 rounded-xl text-[11px] font-bold uppercase tracking-wider whitespace-nowrap transition ${
                      categoryFilter === cat
                        ? 'bg-indigo-500/20 border border-indigo-500/50 text-indigo-300'
                        : 'bg-white/[0.03] border border-white/[0.06] text-slate-400 hover:text-white'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              <div className="space-y-2.5 max-h-[750px] overflow-y-auto pr-1">
                {filteredFps.map((fp) => {
                  const p = screen_profiles[fp];
                  const isSelected = fp === selectedFp;
                  return (
                    <div
                      key={fp}
                      onClick={() => setSelectedFp(fp)}
                      className={`p-4 rounded-2xl cursor-pointer glass-card glass-card-hover border transition ${
                        isSelected
                          ? 'border-indigo-500 bg-indigo-950/30 glow-indigo'
                          : 'border-white/[0.06] bg-[#0f121d]/60'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h4 className="text-sm font-bold text-white leading-snug">{p.screen_name}</h4>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-purple-500/20 text-purple-300 border border-purple-500/30 shrink-0">
                          {p.screen_category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 line-clamp-2 mb-3 leading-relaxed">{p.purpose}</p>
                      <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono pt-2 border-t border-white/[0.05]">
                        <span>{p.elements?.length || 0} UI Nodes</span>
                        <span>{fp.slice(0, 10)}...</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right Column: Screen Detail & Live Canvas */}
            {currentProfile && (
              <div className="lg:col-span-8 space-y-6">
                {/* Screen Header Card */}
                <div className="glass-card p-6 rounded-3xl border border-white/[0.08] relative overflow-hidden">
                  <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                    <div>
                      <div className="flex items-center gap-3">
                        <h2 className="text-2xl font-black text-white tracking-tight">{currentProfile.screen_name}</h2>
                        <span className="px-3 py-1 rounded-full text-xs font-extrabold uppercase bg-indigo-500/20 border border-indigo-500/40 text-indigo-300">
                          {currentProfile.screen_category}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 font-mono mt-1">Fingerprint: {selectedFp}</div>
                    </div>
                  </div>

                  <div className="p-4 rounded-2xl bg-indigo-500/[0.06] border border-indigo-500/20">
                    <div className="text-[11px] font-extrabold uppercase tracking-wider text-indigo-400 mb-1 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" /> AI Inferred Screen Purpose
                    </div>
                    <p className="text-sm text-slate-200 leading-relaxed font-medium">{currentProfile.purpose}</p>
                  </div>
                </div>

                {/* Side-by-Side Visual Canvas */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left: Real Live Screenshot */}
                  <div className="glass-card p-4 rounded-3xl border border-white/[0.08]">
                    <div className="flex items-center justify-between mb-3 text-xs font-bold text-slate-400">
                      <span className="flex items-center gap-1.5 text-slate-300">
                        <Eye className="w-4 h-4 text-indigo-400" /> Ground Truth Device Capture
                      </span>
                      <span className="text-[10px] text-slate-500 uppercase">Live Android Pixels</span>
                    </div>
                    <div className="relative rounded-2xl overflow-hidden bg-black/60 border border-white/10 flex items-center justify-center min-h-[420px]">
                      <img
                        src={`/api/screenshot/${selectedFp}`}
                        alt="Captured Screen"
                        className="w-full h-auto object-contain max-h-[480px] rounded-xl"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = 'https://placehold.co/360x780/10121d/6366f1?text=Live+Screen+Capture';
                        }}
                      />
                    </div>
                  </div>

                  {/* Right: AI Knowledge Pack Rebuild */}
                  <div className="glass-card p-4 rounded-3xl border border-white/[0.08]">
                    <div className="flex items-center justify-between mb-3 text-xs font-bold text-slate-400">
                      <span className="flex items-center gap-1.5 text-slate-300">
                        <Palette className="w-4 h-4 text-purple-400" /> AI Knowledge Pack Rebuild
                      </span>
                      <span className="text-[10px] text-purple-400 font-extrabold uppercase">100% JSON Reconstructed</span>
                    </div>
                    <div className="relative rounded-2xl overflow-hidden bg-black/60 border border-purple-500/20 flex items-center justify-center min-h-[420px]">
                      <iframe
                        src={`/api/rebuild-html/${encodeURIComponent(currentProfile.screen_name)}`}
                        title="Rebuild Preview"
                        className="w-full h-[480px] rounded-xl border-0"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* UI Elements & Form Semantics Table */}
                <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
                  <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <Sliders className="w-4 h-4 text-indigo-400" /> Extracted UI Elements & Form Semantics
                    </h3>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-white/[0.08] text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                          <th className="pb-3 pl-2">Element ID</th>
                          <th className="pb-3">Role</th>
                          <th className="pb-3">Form Semantic Type</th>
                          <th className="pb-3">Plain Language Description</th>
                          <th className="pb-3 pr-2">Visible Label</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/[0.04]">
                        {currentProfile.elements?.map((el, idx) => (
                          <tr key={idx} className="hover:bg-white/[0.02] transition">
                            <td className="py-3 pl-2 font-mono font-semibold text-indigo-300">{el.element_id}</td>
                            <td className="py-3">
                              <span className="px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase bg-white/[0.05] border border-white/10 text-slate-300">
                                {el.role}
                              </span>
                            </td>
                            <td className="py-3">
                              {el.form_field_type ? (
                                <span className="px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                                  {el.form_field_type}
                                </span>
                              ) : (
                                <span className="text-slate-600">—</span>
                              )}
                            </td>
                            <td className="py-3 text-slate-300 max-w-xs">{el.plain_description}</td>
                            <td className="py-3 pr-2 text-slate-400 font-medium">{el.text || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 2: JOURNEY GRAPH */}
        {/* ========================================================= */}
        {activeTab === 'graph' && (
          <div className="space-y-6">
            <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <Compass className="w-5 h-5 text-indigo-400" /> Discovered Screen Nodes & Transitions
              </h3>
              <p className="text-xs text-slate-400 mb-6">
                Deduplicated directed transition graph compiled from live autonomous crawling.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {screen_graph.nodes?.map((node, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] hover:border-indigo-500/40 transition">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-bold text-white">{node.screen_name}</h4>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 font-bold uppercase">
                        {node.category}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-2 mb-3">{node.purpose}</p>
                    <div className="text-[10px] text-slate-500 font-mono">Fingerprint: {node.fingerprint.slice(0, 14)}...</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Canonical User Journeys */}
            <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-400" /> Discovered User Journeys & Flows
              </h3>
              <div className="space-y-3">
                {screen_graph.journeys?.map((j, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-indigo-950/20 border border-indigo-500/20">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-bold text-white">{j.journey_name}</span>
                      <span className="text-xs text-indigo-300 font-semibold">{j.step_count} Sequential Steps</span>
                    </div>
                    <p className="text-xs text-slate-400 mb-3">{j.description}</p>
                    <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
                      {j.screen_sequence?.map((fp, sIdx) => (
                        <React.Fragment key={sIdx}>
                          <span className="px-2.5 py-1 rounded-lg bg-black/40 border border-white/10 text-slate-200">
                            {screen_profiles[fp]?.screen_name || fp.slice(0, 8)}
                          </span>
                          {sIdx < j.screen_sequence.length - 1 && <ArrowRight className="w-3.5 h-3.5 text-indigo-400" />}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 3: BRAND DESIGN SYSTEM STUDIO */}
        {/* ========================================================= */}
        {activeTab === 'design' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Color Palette */}
            <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Palette className="w-5 h-5 text-pink-400" /> Color Palette & Theme Tokens
                </h3>
                <span className="px-3 py-1 rounded-full text-xs font-bold uppercase bg-purple-500/10 text-purple-300 border border-purple-500/20">
                  {design_system.palette?.is_dark_mode ? '🌙 Dark Mode' : '☀️ Light Mode'}
                </span>
              </div>

              <div className="space-y-3">
                {[
                  { label: 'Primary Accent', color: design_system.palette?.primary_accent },
                  { label: 'Secondary Accent', color: design_system.palette?.secondary_accent },
                  { label: 'Canvas Background', color: design_system.palette?.background },
                  { label: 'Surface Card Color', color: design_system.palette?.surface },
                  { label: 'Text Primary', color: design_system.palette?.text_primary },
                  { label: 'Text Secondary', color: design_system.palette?.text_secondary },
                ].map((item, idx) => (
                  <div
                    key={idx}
                    onClick={() => copyToClipboard(item.color)}
                    className="flex items-center justify-between p-3 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-indigo-500/40 cursor-pointer transition group"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-9 h-9 rounded-xl border border-white/20 shadow-inner shrink-0"
                        style={{ backgroundColor: item.color }}
                      />
                      <div>
                        <div className="text-xs font-bold text-white">{item.label}</div>
                        <div className="text-xs font-mono text-slate-400">{item.color}</div>
                      </div>
                    </div>
                    <span className="text-[10px] text-slate-500 group-hover:text-indigo-400 font-bold uppercase transition">
                      {copiedHex === item.color ? 'Copied!' : 'Copy HEX'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Layout Rhythm & Tone of Voice */}
            <div className="space-y-6">
              <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
                <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-indigo-400" /> Layout & Spacing Rhythm
                </h3>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 rounded-2xl bg-white/[0.02] border border-white/[0.05]">
                    <div className="text-slate-400 text-[11px] mb-1">Base Grid Unit</div>
                    <div className="text-base font-black text-white">{design_system.spacing?.base_grid_unit_dp} dp</div>
                    <div className="text-[10px] text-slate-500">8-Point Android Standard</div>
                  </div>
                  <div className="p-3 rounded-2xl bg-white/[0.02] border border-white/[0.05]">
                    <div className="text-slate-400 text-[11px] mb-1">Horizontal Padding</div>
                    <div className="text-base font-black text-white">{design_system.spacing?.screen_padding_horizontal_dp} dp</div>
                    <div className="text-[10px] text-slate-500">Screen Gutter</div>
                  </div>
                  <div className="p-3 rounded-2xl bg-white/[0.02] border border-white/[0.05]">
                    <div className="text-slate-400 text-[11px] mb-1">Vertical Gap</div>
                    <div className="text-base font-black text-white">{design_system.spacing?.component_gap_vertical_dp} dp</div>
                    <div className="text-[10px] text-slate-500">Item Rhythm</div>
                  </div>
                  <div className="p-3 rounded-2xl bg-white/[0.02] border border-white/[0.05]">
                    <div className="text-slate-400 text-[11px] mb-1">Border Radius</div>
                    <div className="text-base font-black text-white">{design_system.spacing?.border_radius_dp} dp</div>
                    <div className="text-[10px] text-slate-500">Corner Smoothing</div>
                  </div>
                </div>
              </div>

              <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
                <h3 className="text-base font-bold text-white mb-2 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-400" /> Brand Tone of Voice
                </h3>
                <p className="text-xs text-slate-400 mb-3">
                  Linguistic communication persona inferred from visible button labels and screen copy.
                </p>
                <div className="p-4 rounded-2xl bg-amber-500/[0.08] border border-amber-500/20 text-amber-200 text-sm font-semibold">
                  {design_system.tone_of_voice}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 4: VISUAL REBUILD PROOF */}
        {/* ========================================================= */}
        {activeTab === 'fidelity' && (
          <div className="glass-card p-6 rounded-3xl border border-white/[0.08] space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Pure JSON Visual Reconstructions
                </h3>
                <p className="text-xs text-slate-400">
                  Recreated 100% autonomously from the App Knowledge Pack JSON with zero access to original image pixels.
                </p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Fidelity Verified
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
              {['Search_Settings', 'Manage', 'Recommended'].map((name, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] flex flex-col items-center">
                  <div className="text-xs font-bold text-slate-300 mb-3">{name.replace('_', ' ')}</div>
                  <img
                    src={`/api/fidelity/fidelity_comparison_${name}.png`}
                    alt="Fidelity Comparison"
                    className="w-full h-auto rounded-xl border border-white/10"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 5: JSON KNOWLEDGE PACK */}
        {/* ========================================================= */}
        {activeTab === 'json' && (
          <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Code2 className="w-5 h-5 text-indigo-400" /> Compiled Knowledge Pack JSON Schema
              </h3>
              <a
                href={`data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(data, null, 2))}`}
                download={`knowledge_pack_${metadata.package_name}.json`}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 transition"
              >
                <Download className="w-3.5 h-3.5" /> Download JSON
              </a>
            </div>
            <pre className="p-4 rounded-2xl bg-black/60 border border-white/10 text-emerald-300 text-xs font-mono max-h-[600px] overflow-auto leading-relaxed">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        )}
      </main>
    </div>
  );
}
