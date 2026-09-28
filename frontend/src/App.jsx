import { useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import "./App.css";

/*
 * ============================================================
 * DHOKADETECT
 * Dark Web Intelligence Analyst Dashboard
 * Step 1 - Frontend Graph Prototype
 *
 * Backend integration:
 * The graph is currently powered by mock data.
 * Later this can be replaced with:
 *
 * GET /graph
 *
 * {
 *   "nodes": [...],
 *   "edges": [...]
 * }
 * ============================================================
 */

/* ------------------------------------------------------------
   MOCK INTELLIGENCE DATA
------------------------------------------------------------ */

const INITIAL_NODES = [
  {
    id: "actor-01",
    type: "intelligence",
    position: { x: 80, y: 180 },
    data: {
      label: "Shadow Broker",
      category: "Threat Actor",
      status: "Active",
      description:
        "Threat actor associated with multiple underground identities and infrastructure.",
      metadata: {
        "First Seen": "2026-08-12",
        "Last Seen": "2026-09-28",
        Confidence: "High",
        Sources: "7",
      },
    },
  },
  {
    id: "user-01",
    type: "intelligence",
    position: { x: 360, y: 80 },
    data: {
      label: "dark_user_47",
      category: "Username",
      status: "Observed",
      description:
        "Underground username linked to multiple intelligence records.",
      metadata: {
        Platform: "Forum",
        "First Seen": "2026-08-18",
        Activity: "Recent",
        Confidence: "Medium",
      },
    },
  },
  {
    id: "domain-01",
    type: "intelligence",
    position: { x: 650, y: 170 },
    data: {
      label: "shadowmarket.onion",
      category: "Domain",
      status: "Active",
      description:
        "Dark-web domain associated with the selected intelligence cluster.",
      metadata: {
        Network: "Tor",
        Status: "Online",
        "First Seen": "2026-08-21",
        Confidence: "High",
      },
    },
  },
  {
    id: "ip-01",
    type: "intelligence",
    position: { x: 950, y: 80 },
    data: {
      label: "185.XXX.42.19",
      category: "IP Address",
      status: "Observed",
      description:
        "Infrastructure indicator associated with the domain.",
      metadata: {
        Provider: "Unknown",
        Network: "Tor Exit",
        Country: "Unknown",
        Confidence: "Medium",
      },
    },
  },
  {
    id: "wallet-01",
    type: "intelligence",
    position: { x: 950, y: 300 },
    data: {
      label: "bc1q...7h4x",
      category: "Crypto Wallet",
      status: "Flagged",
      description:
        "Cryptocurrency wallet referenced by multiple underground records.",
      metadata: {
        Currency: "Bitcoin",
        Transactions: "24",
        "First Seen": "2026-08-27",
        Confidence: "High",
      },
    },
  },
  {
    id: "market-01",
    type: "intelligence",
    position: { x: 650, y: 430 },
    data: {
      label: "Night Market",
      category: "Marketplace",
      status: "Active",
      description:
        "Underground marketplace node connected to the intelligence cluster.",
      metadata: {
        Network: "Tor",
        Category: "Marketplace",
        Listings: "1,842",
        Confidence: "High",
      },
    },
  },
  {
    id: "email-01",
    type: "intelligence",
    position: { x: 350, y: 400 },
    data: {
      label: "contact@shadowmail",
      category: "Email",
      status: "Observed",
      description:
        "Email identifier found in several related intelligence records.",
      metadata: {
        "First Seen": "2026-09-01",
        Mentions: "12",
        Confidence: "Medium",
      },
    },
  },
];

const INITIAL_EDGES = [
  {
    id: "e-actor-user",
    source: "actor-01",
    target: "user-01",
    label: "USES",
    animated: true,
  },
  {
    id: "e-user-domain",
    source: "user-01",
    target: "domain-01",
    label: "LINKED TO",
    animated: true,
  },
  {
    id: "e-domain-ip",
    source: "domain-01",
    target: "ip-01",
    label: "RESOLVES TO",
  },
  {
    id: "e-domain-wallet",
    source: "domain-01",
    target: "wallet-01",
    label: "REFERENCES",
  },
  {
    id: "e-domain-market",
    source: "domain-01",
    target: "market-01",
    label: "OPERATES",
  },
  {
    id: "e-actor-email",
    source: "actor-01",
    target: "email-01",
    label: "ASSOCIATED",
  },
  {
    id: "e-email-market",
    source: "email-01",
    target: "market-01",
    label: "MENTIONED IN",
  },
];

/* ------------------------------------------------------------
   NODE ICONS
------------------------------------------------------------ */

const CATEGORY_SYMBOLS = {
  "Threat Actor": "TA",
  Username: "US",
  Domain: "DO",
  "IP Address": "IP",
  "Crypto Wallet": "CW",
  Marketplace: "MP",
  Email: "@",
};

/* ------------------------------------------------------------
   CUSTOM REACT FLOW NODE
------------------------------------------------------------ */

function IntelligenceNode({ data, selected }) {
  const symbol = CATEGORY_SYMBOLS[data.category] || "IN";

  return (
    <div className={`intel-node ${selected ? "selected" : ""}`}>
      <Handle type="target" position={Position.Left} />

      <div className="intel-node-symbol">{symbol}</div>

      <div className="intel-node-content">
        <div className="intel-node-category">{data.category}</div>
        <div className="intel-node-label">{data.label}</div>

        <div className="intel-node-status">
          <span className={`status-dot ${data.status?.toLowerCase()}`} />
          {data.status}
        </div>
      </div>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}

const nodeTypes = {
  intelligence: IntelligenceNode,
};

/* ------------------------------------------------------------
   MAIN APP
------------------------------------------------------------ */

function App() {
  const [nodes, setNodes] = useState(INITIAL_NODES);
  const [edges, setEdges] = useState(INITIAL_EDGES);

  const [selectedNode, setSelectedNode] = useState(null);
  const [search, setSearch] = useState("");
  const [activeView, setActiveView] = useState("Graph");

  /* ----------------------------------------------------------
     SEARCH
  ---------------------------------------------------------- */

  const filteredNodes = useMemo(() => {
    if (!search.trim()) {
      return nodes;
    }

    const query = search.toLowerCase();

    return nodes.filter((node) => {
      const label = node.data?.label?.toLowerCase() || "";
      const category = node.data?.category?.toLowerCase() || "";

      return label.includes(query) || category.includes(query);
    });
  }, [nodes, search]);

  /* ----------------------------------------------------------
     NODE CLICK
  ---------------------------------------------------------- */

  const handleNodeClick = (_, node) => {
    setSelectedNode(node);
  };

  /* ----------------------------------------------------------
     GRAPH EVENT
  ---------------------------------------------------------- */

  const handleNodesChange = (changes) => {
    setNodes((currentNodes) => {
      return currentNodes.map((node) => {
        const change = changes.find((item) => item.id === node.id);

        if (!change) {
          return node;
        }

        if (change.type === "position" && change.position) {
          return {
            ...node,
            position: change.position,
          };
        }

        if (change.type === "select") {
          return {
            ...node,
            selected: change.selected,
          };
        }

        return node;
      });
    });
  };

  /* ----------------------------------------------------------
     SIDEBAR NAVIGATION
  ---------------------------------------------------------- */

  const navigationItems = [
    {
      label: "Graph",
      description: "Relationship map",
    },
    {
      label: "Entities",
      description: "Tracked identities",
    },
    {
      label: "Indicators",
      description: "IOCs & infrastructure",
    },
    {
      label: "Sources",
      description: "Intelligence sources",
    },
  ];

  /* ----------------------------------------------------------
     STATISTICS
  ---------------------------------------------------------- */

  const statistics = [
    {
      label: "ENTITIES",
      value: nodes.length,
    },
    {
      label: "RELATIONSHIPS",
      value: edges.length,
    },
    {
      label: "ACTIVE",
      value: nodes.filter((node) => node.data.status === "Active").length,
    },
  ];

  return (
    <div className="dark-web-app">
      {/* ======================================================
          TOP HEADER
      ====================================================== */}

      <header className="intel-header">
        <div className="brand-area">
          <div className="brand-mark">
            D
          </div>

          <div>
            <div className="brand-name">DHOKADETECT</div>
            <div className="brand-subtitle">
              DARK WEB INTELLIGENCE
            </div>
          </div>
        </div>

        <div className="header-center">
          <span className="system-indicator" />
          INTELLIGENCE NETWORK
          <span className="header-divider" />
          LIVE
        </div>

        <div className="header-right">
          <div className="header-time">
            SYSTEM ONLINE
          </div>

          <button className="header-button">
            ANALYST MODE
          </button>
        </div>
      </header>

      {/* ======================================================
          MAIN LAYOUT
      ====================================================== */}

      <main className="intel-layout">

        {/* ====================================================
            LEFT SIDEBAR
        ==================================================== */}

        <aside className="intel-sidebar">

          <div className="sidebar-heading">
            INTELLIGENCE
          </div>

          <nav className="intel-navigation">
            {navigationItems.map((item) => (
              <button
                key={item.label}
                className={`nav-item ${
                  activeView === item.label ? "active" : ""
                }`}
                onClick={() => setActiveView(item.label)}
              >
                <span className="nav-indicator" />

                <div>
                  <div className="nav-label">
                    {item.label}
                  </div>

                  <div className="nav-description">
                    {item.description}
                  </div>
                </div>
              </button>
            ))}
          </nav>

          <div className="sidebar-section">
            <div className="sidebar-heading">
              NETWORK STATUS
            </div>

            <div className="network-status">
              <div className="network-status-row">
                <span>TOR NETWORK</span>
                <span className="status-online">
                  ONLINE
                </span>
              </div>

              <div className="network-status-row">
                <span>COLLECTORS</span>
                <span className="status-online">
                  08
                </span>
              </div>

              <div className="network-status-row">
                <span>LAST SYNC</span>
                <span>
                  02m
                </span>
              </div>
            </div>
          </div>

          <div className="sidebar-bottom">
            <div className="analyst-label">
              ANALYST
            </div>

            <div className="analyst-name">
              DHOKA OPS
            </div>

            <div className="analyst-status">
              SESSION ACTIVE
            </div>
          </div>
        </aside>

        {/* ====================================================
            GRAPH AREA
        ==================================================== */}

        <section className="graph-section">

          <div className="graph-toolbar">

            <div>
              <div className="page-eyebrow">
                DARK WEB INTELLIGENCE
              </div>

              <h1>
                Relationship Graph
              </h1>

              <p>
                Explore connected entities, infrastructure,
                identities and underground activity.
              </p>
            </div>

            <div className="graph-actions">

              <div className="graph-search">
                <span>
                  /
                </span>

                <input
                  value={search}
                  onChange={(event) =>
                    setSearch(event.target.value)
                  }
                  placeholder="Search entities..."
                />
              </div>

              <button
                className="refresh-button"
                onClick={() => {
                  setSearch("");
                  setSelectedNode(null);
                }}
              >
                RESET
              </button>

            </div>
          </div>

          {/* --------------------------------------------------
              GRAPH
          -------------------------------------------------- */}

          <div className="graph-container">

            <div className="graph-top-stats">
              {statistics.map((stat) => (
                <div
                  className="graph-stat"
                  key={stat.label}
                >
                  <span>
                    {stat.label}
                  </span>

                  <strong>
                    {stat.value}
                  </strong>
                </div>
              ))}
            </div>

            <ReactFlow
              nodes={filteredNodes}
              edges={edges}
              nodeTypes={nodeTypes}
              onNodeClick={handleNodeClick}
              onNodesChange={handleNodesChange}
              fitView
              fitViewOptions={{
                padding: 0.2,
              }}
              minZoom={0.25}
              maxZoom={2}
              attributionPosition="bottom-left"
            >
              <Background
                gap={32}
                size={1}
              />

              <Controls
                showInteractive={false}
              />

              <MiniMap
                pannable
                zoomable
              />
            </ReactFlow>

            <div className="graph-overlay">
              <span className="pulse-dot" />
              GRAPH ENGINE
              <span>
                {filteredNodes.length} NODES
              </span>
            </div>

          </div>
        </section>

        {/* ====================================================
            RIGHT EVIDENCE PANEL
        ==================================================== */}

        <aside className="evidence-panel">

          <div className="evidence-header">

            <div>
              <div className="panel-eyebrow">
                INTELLIGENCE
              </div>

              <h2>
                Evidence
              </h2>
            </div>

            <div className="evidence-count">
              {selectedNode ? "01" : "00"}
            </div>

          </div>

          {!selectedNode ? (
            <div className="empty-evidence">

              <div className="empty-crosshair">
                +
              </div>

              <h3>
                No entity selected
              </h3>

              <p>
                Select a node from the intelligence
                graph to inspect its evidence,
                attributes and relationships.
              </p>

            </div>
          ) : (
            <div className="selected-evidence">

              {/* Entity heading */}

              <div className="entity-header">

                <div className="entity-symbol">
                  {CATEGORY_SYMBOLS[
                    selectedNode.data.category
                  ] || "IN"}
                </div>

                <div>
                  <div className="entity-category">
                    {selectedNode.data.category}
                  </div>

                  <div className="entity-name">
                    {selectedNode.data.label}
                  </div>

                  <div className="entity-status">
                    <span
                      className={`status-dot ${selectedNode.data.status?.toLowerCase()}`}
                    />

                    {selectedNode.data.status}
                  </div>
                </div>

              </div>

              {/* Description */}

              <div className="evidence-section">

                <div className="evidence-section-title">
                  DESCRIPTION
                </div>

                <p className="entity-description">
                  {selectedNode.data.description}
                </p>

              </div>

              {/* Metadata */}

              <div className="evidence-section">

                <div className="evidence-section-title">
                  ATTRIBUTES
                </div>

                <div className="metadata-list">

                  {Object.entries(
                    selectedNode.data.metadata || {}
                  ).map(([key, value]) => (
                    <div
                      className="metadata-row"
                      key={key}
                    >
                      <span>
                        {key}
                      </span>

                      <strong>
                        {value}
                      </strong>
                    </div>
                  ))}

                </div>

              </div>

              {/* Relationships */}

              <div className="evidence-section">

                <div className="evidence-section-title">
                  RELATIONSHIPS
                </div>

                <div className="relationship-list">

                  {edges
                    .filter(
                      (edge) =>
                        edge.source === selectedNode.id ||
                        edge.target === selectedNode.id
                    )
                    .map((edge) => {

                      const relatedId =
                        edge.source === selectedNode.id
                          ? edge.target
                          : edge.source;

                      const relatedNode =
                        nodes.find(
                          (node) =>
                            node.id === relatedId
                        );

                      return (
                        <div
                          className="relationship-item"
                          key={edge.id}
                        >
                          <div>
                            <span>
                              {edge.label}
                            </span>

                            <strong>
                              {relatedNode?.data.label}
                            </strong>
                          </div>

                          <span className="relationship-arrow">
                            →
                          </span>
                        </div>
                      );
                    })}

                </div>

              </div>

              {/* Evidence footer */}

              <div className="evidence-footer">

                <div className="evidence-footer-label">
                  EVIDENCE STATUS
                </div>

                <div className="evidence-confidence">
                  VERIFIED / CORRELATED
                </div>

              </div>

            </div>
          )}

        </aside>

      </main>
    </div>
  );
}

export default App;