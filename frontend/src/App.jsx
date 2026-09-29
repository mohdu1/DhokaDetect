import { useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import "./App.css";

/*
 * ============================================================
 * DHOKADETECT
 * Dark Web Intelligence Analyst Dashboard
 * Graph data is loaded from GET /api/v1/graph.
 * ============================================================
 */

/* ------------------------------------------------------------
   NODE ICONS
------------------------------------------------------------ */

const CATEGORY_SYMBOLS = {
  "Threat Actor": "TA",
  Cryptocurrency: "₿",
  Infrastructure: "IN",
  Communication: "COM",
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
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [selectedNode, setSelectedNode] = useState(null);
  const [search, setSearch] = useState("");
  const [activeView, setActiveView] = useState("Graph");
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadGraph() {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/v1/graph",
          { signal: controller.signal },
        );

        if (!response.ok) {
          throw new Error(`Graph request failed (${response.status}).`);
        }

        const graph = await response.json();
        if (!Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) {
          throw new Error("Graph API returned an invalid response.");
        }

        setNodes(graph.nodes);
        setEdges(graph.edges);
      } catch (error) {
        if (!controller.signal.aborted) {
          setLoadError(
            error instanceof Error ? error.message : "Unable to load graph data.",
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadGraph();
    return () => controller.abort();
  }, []);

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

  if (isLoading) {
    return (
      <div
        className="dark-web-app"
        style={{ display: "grid", minHeight: "100vh", placeItems: "center" }}
      >
        Initializing Intelligence Matrix...
      </div>
    );
  }

  if (loadError) {
    return (
      <div
        className="dark-web-app"
        style={{ display: "grid", minHeight: "100vh", placeItems: "center" }}
      >
        <div role="alert">Unable to load intelligence graph: {loadError}</div>
      </div>
    );
  }

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