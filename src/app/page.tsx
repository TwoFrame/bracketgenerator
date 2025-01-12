"use client";
import { useState, useCallback } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  BackgroundVariant,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
// import { init } from 'next/dist/compiled/webpack/webpack';


import RoundLabelNode from "./RoundLabelNode";
import BracketNode from "./BracketNode";

import FinalSerializedBrackets from "./WIPSerializedBrackets.json";

const nodeTypes = {
  roundLabelNode: RoundLabelNode,
  bracketNode: BracketNode,
};

const Brackets: any = FinalSerializedBrackets;


export default function Landing() {
  
  const [bracketKey, setBracketKey] = useState("2");

  const [nodes, setNodes, onNodesChange] = useNodesState(
    Brackets[bracketKey].nodes || [],
  );
  const [edges, setEdges, onEdgesChange] = useEdgesState(
    Brackets[bracketKey].edges || [],
  );

  function handleEntrantChange(e: any) {
    const newKey = e.target.value
    if (newKey in Brackets) {
      setBracketKey(newKey);
      setNodes(Brackets[newKey].nodes);
      setEdges(Brackets[newKey].edges);
    }
  }
  
  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );
  return (
    <div style={{ width: "100vw", height: "80vh" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        nodesDraggable={true}
        edgesReconnectable={true}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        panOnScroll={true}
      >
        <Controls />
        <MiniMap />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
      <div style={{ padding: "10px", backgroundColor: "#f0f0f0" }}>
        <label>
          Incoming Winners:{" "}
          <input
            type="text"
            onChange={handleEntrantChange}
            style={{ marginLeft: "5px", padding: "5px" }}
          />
        </label>
      </div>
    </div>
  );
}
