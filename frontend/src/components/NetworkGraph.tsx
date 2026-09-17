import React, { useState } from 'react';
import { VendorNetwork, GraphNode } from '../types';
import { Users, Building2, MapPin, Search, AlertTriangle, ShieldAlert, GitFork, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

interface NetworkGraphProps {
  network: VendorNetwork | null;
  onSelectNode?: (node: GraphNode) => void;
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({ network }) => {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filterType, setFilterType] = useState<string>('ALL');
  const [depth, setDepth] = useState<number>(2);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  // Curated default graph matching the reference board if network is null or for flagship demo
  const defaultNodes: GraphNode[] = [
    { id: 'v1', label: 'BuildRight Infra Pvt Ltd', type: 'PRIMARY_VENDOR', meta: { win_rate: 0.76, contracts: 14, evidence: 'Flagship contractor with 40% price anomaly and 110-day delay.' } },
    { id: 'd1', label: 'R. Kumar', type: 'DIRECTOR', meta: { evidence: 'Director in BuildRight Infra and Apex Constructions concurrently.' } },
    { id: 'd2', label: 'Sachin Gupta', type: 'DIRECTOR', meta: { evidence: 'Authorized signatory for BuildRight and sister entities.' } },
    { id: 'a1', label: 'Plot 42, Industrial Area, Solan', type: 'ADDRESS', meta: { evidence: 'Single registered physical premises shared by 3 competing bidding entities.' } },
    { id: 'v2', label: 'Apex Constructions Ltd', type: 'RELATED_VENDOR', meta: { win_rate: 0.22, contracts: 3, evidence: 'Submitted cover bids in 6 rural road tenders with BuildRight.' } },
    { id: 'v3', label: 'Shiva Infra JV', type: 'RELATED_VENDOR', meta: { win_rate: 0.15, contracts: 2, evidence: 'Co-bids from same IP subnet; shares registered GST premises.' } },
  ];

  const defaultEdges = [
    { source: 'v1', target: 'd1', type: 'DIRECTOR', label: 'Director' },
    { source: 'v2', target: 'd1', type: 'DIRECTOR', label: 'Director' },
    { source: 'v1', target: 'd2', type: 'DIRECTOR', label: 'Director' },
    { source: 'v1', target: 'a1', type: 'ADDRESS', label: 'Registered Address' },
    { source: 'v3', target: 'a1', type: 'ADDRESS', label: 'Registered Address' },
    { source: 'v1', target: 'v2', type: 'FREQUENT_CO_BIDDER', label: 'Frequent Co-Bidder (8x)' },
  ];

  const nodes = network && network.nodes && network.nodes.length > 0 ? network.nodes : defaultNodes;
  const edges = network && network.edges && network.edges.length > 0 ? network.edges : defaultEdges;

  // Layout node positions
  const width = 720;
  const height = 440;
  const centerX = width / 2;
  const centerY = height / 2 - 10;

  const nodePositions: Record<string, { x: number; y: number }> = {
    v1: { x: centerX, y: centerY },
    d1: { x: centerX - 190, y: centerY - 90 },
    d2: { x: centerX + 180, y: centerY - 90 },
    a1: { x: centerX, y: centerY + 130 },
    v2: { x: centerX - 220, y: centerY + 70 },
    v3: { x: centerX + 210, y: centerY + 70 },
  };

  // Fallback position generator for dynamic nodes
  nodes.forEach((n, idx) => {
    if (!nodePositions[n.id]) {
      if (n.type === 'PRIMARY_VENDOR') {
        nodePositions[n.id] = { x: centerX, y: centerY };
      } else {
        const angle = (idx / (nodes.length - 1)) * 2 * Math.PI;
        nodePositions[n.id] = {
          x: centerX + 170 * Math.cos(angle),
          y: centerY + 120 * Math.sin(angle),
        };
      }
    }
  });

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'PRIMARY_VENDOR':
        return { bg: '#0D9488', ring: '#14B8A6', text: '#FFFFFF', dot: '#0F766E' };
      case 'DIRECTOR':
        return { bg: '#F43F5E', ring: '#FDA4AF', text: '#FFFFFF', dot: '#BE123C' };
      case 'ADDRESS':
        return { bg: '#F59E0B', ring: '#FDE68A', text: '#FFFFFF', dot: '#B45309' };
      case 'RELATED_VENDOR':
        return { bg: '#0284C7', ring: '#BAE6FD', text: '#FFFFFF', dot: '#0369A1' };
      default:
        return { bg: '#8B5CF6', ring: '#DDD6FE', text: '#FFFFFF', dot: '#6D28D9' };
    }
  };

  const filteredNodes = nodes.filter((n) => {
    const matchesSearch = searchQuery === '' || n.label.toLowerCase().includes(searchQuery.toLowerCase());
    if (!matchesSearch) return false;
    if (filterType === 'ALL') return true;
    if (filterType === 'DIRECTORS' && (n.type === 'DIRECTOR' || n.type === 'PRIMARY_VENDOR')) return true;
    if (filterType === 'ADDRESSES' && (n.type === 'ADDRESS' || n.type === 'PRIMARY_VENDOR')) return true;
    if (filterType === 'VENDORS' && (n.type === 'RELATED_VENDOR' || n.type === 'PRIMARY_VENDOR')) return true;
    return true;
  });

  const activeNode = selectedNode || nodes[0];

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Top Controls Toolbar matching mockup */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200/80">
        <div className="flex items-center gap-2 flex-grow max-w-sm">
          <div className="relative w-full">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search vendors, directors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-teal-500"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Filter Dropdown */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:border-teal-500"
          >
            <option value="ALL">All Relationships</option>
            <option value="DIRECTORS">Shared Directors Only</option>
            <option value="ADDRESSES">Common Addresses Only</option>
            <option value="VENDORS">Co-Bidding Bidders Only</option>
          </select>

          {/* Depth Dropdown */}
          <select
            value={depth}
            onChange={(e) => setDepth(Number(e.target.value))}
            className="px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:border-teal-500"
          >
            <option value={1}>Depth: 1</option>
            <option value={2}>Depth: 2</option>
            <option value={3}>Depth: 3</option>
          </select>

          {/* Zoom controls */}
          <div className="flex items-center bg-white border border-slate-200 rounded-lg p-0.5">
            <button
              onClick={() => setZoomLevel((z) => Math.min(1.4, z + 0.1))}
              className="p-1 hover:bg-slate-100 rounded text-slate-600"
              title="Zoom in"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoomLevel((z) => Math.max(0.7, z - 0.1))}
              className="p-1 hover:bg-slate-100 rounded text-slate-600"
              title="Zoom out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => { setZoomLevel(1); setSelectedNode(null); setSearchQuery(''); }}
              className="p-1 hover:bg-slate-100 rounded text-slate-600"
              title="Reset"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Network Canvas Card */}
      <div className="relative rounded-2xl bg-white border border-slate-200/90 overflow-hidden shadow-sm">
        {/* Subtle grid pattern background */}
        <div 
          className="absolute inset-0 opacity-[0.03] pointer-events-none" 
          style={{ backgroundImage: 'radial-gradient(#0F172A 1px, transparent 1px)', backgroundSize: '16px 16px' }} 
        />

        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-80 sm:h-96 select-none transition-transform duration-200"
          style={{ transform: `scale(${zoomLevel})` }}
        >
          {/* Edges */}
          {edges.map((edge, idx) => {
            const start = nodePositions[edge.source];
            const end = nodePositions[edge.target];
            if (!start || !end) return null;

            const isCartel = edge.type === 'FREQUENT_CO_BIDDER';
            const isHighlighted =
              activeNode && (activeNode.id === edge.source || activeNode.id === edge.target);

            return (
              <g key={idx}>
                <line
                  x1={start.x}
                  y1={start.y}
                  x2={end.x}
                  y2={end.y}
                  stroke={isCartel ? '#EF4444' : isHighlighted ? '#0D9488' : '#CBD5E1'}
                  strokeWidth={isCartel ? '2.5' : isHighlighted ? '2' : '1.5'}
                  strokeDasharray={isCartel ? '5 4' : undefined}
                  className="transition-colors duration-200"
                />
                {/* Edge Midpoint Label */}
                <rect
                  x={(start.x + end.x) / 2 - 40}
                  y={(start.y + end.y) / 2 - 12}
                  width="80"
                  height="16"
                  rx="4"
                  fill="#FFFFFF"
                  stroke={isCartel ? '#FCA5A5' : '#E2E8F0'}
                  strokeWidth="1"
                />
                <text
                  x={(start.x + end.x) / 2}
                  y={(start.y + end.y) / 2}
                  fill={isCartel ? '#DC2626' : '#64748B'}
                  fontSize="9"
                  fontWeight="600"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="pointer-events-none font-sans"
                >
                  {edge.label}
                </text>
              </g>
            );
          })}

          {/* Nodes */}
          {filteredNodes.map((node) => {
            const pos = nodePositions[node.id];
            if (!pos) return null;
            const isSelected = activeNode?.id === node.id;
            const theme = getNodeColor(node.type);

            return (
              <g
                key={node.id}
                className="cursor-pointer group"
                onClick={() => setSelectedNode(node)}
              >
                {/* Pulse ring for primary or selected */}
                {isSelected && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r="28"
                    fill={theme.ring}
                    opacity="0.35"
                    className="animate-pulse"
                  />
                )}

                {/* Node Outer Circle */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={node.type === 'PRIMARY_VENDOR' ? '22' : '18'}
                  fill={theme.bg}
                  stroke="#FFFFFF"
                  strokeWidth="3"
                  className="shadow-md transition-all duration-200 group-hover:scale-110"
                />

                {/* Center Icon Indicator */}
                <circle cx={pos.x} cy={pos.y} r="6" fill="#FFFFFF" opacity="0.9" />

                {/* Label Box Under Node */}
                <rect
                  x={pos.x - 70}
                  y={pos.y + 26}
                  width="140"
                  height="22"
                  rx="6"
                  fill="#FFFFFF"
                  stroke={isSelected ? theme.bg : '#E2E8F0'}
                  strokeWidth={isSelected ? '1.5' : '1'}
                  className="shadow-xs"
                />
                <text
                  x={pos.x}
                  y={pos.y + 38}
                  fill="#0F172A"
                  fontSize="10"
                  fontWeight="700"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="pointer-events-none"
                >
                  {node.label.length > 20 ? node.label.substring(0, 18) + '...' : node.label}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Legend Bar at Bottom */}
        <div className="p-3 bg-slate-50/90 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 font-medium text-slate-700">
              <span className="w-2.5 h-2.5 rounded-full bg-teal-600 ring-2 ring-teal-200" />
              Primary Vendor
            </span>
            <span className="flex items-center gap-1.5 font-medium text-slate-700">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-2 ring-rose-200" />
              Director
            </span>
            <span className="flex items-center gap-1.5 font-medium text-slate-700">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 ring-2 ring-amber-200" />
              Address
            </span>
            <span className="flex items-center gap-1.5 font-medium text-slate-700">
              <span className="w-2.5 h-2.5 rounded-full bg-sky-600 ring-2 ring-sky-200" />
              Related Vendor
            </span>
          </div>
          <span className="text-[11px] text-slate-400">Click any entity to inspect corporate filing evidence</span>
        </div>
      </div>

      {/* Flagged Entity Detail Box */}
      {activeNode && (
        <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-200">
                {activeNode.type.replace('_', ' ')}
              </span>
              <h4 className="font-bold text-slate-900 text-sm">{activeNode.label}</h4>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              {activeNode.meta?.evidence || 'Entity cross-referenced with Ministry of Corporate Affairs (MCA) database.'}
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <div className="px-3 py-1.5 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs font-bold flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4" />
              <span>Cartel Risk: High</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

