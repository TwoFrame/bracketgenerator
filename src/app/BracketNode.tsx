import React, { memo } from "react";
import { Handle, Position, useNodeId } from "@xyflow/react";

export default memo(({ data, isConnectable }: any) => {
  const nodeId = useNodeId();
  
  let TopText = "";
  let BottomText = "";
  if (data.bracketNodeType == "start") {
    // winners round 1 filled node
    if (data.highSeed && data.lowSeed) {
      TopText = `Seed ${data.highSeed}`;
      BottomText = `Seed ${data.lowSeed}`;
    }
    //winners round 1 bye node
    else if (data.highSeed && !data.lowSeed){
      TopText = `BYE`;
      BottomText = `Seed ${data.highSeed}`;
    }
  }

  if (data.winnerSourceTop) {
    TopText = `Loser of ${data.winnerSourceTop}`;
  }
  if (data.winnerSourceBottom) {
    BottomText = `Loser of ${data.winnerSourceBottom}`;
  }
  
  return (
    <div className="relative">
      <div className="absolute top-[-12px] bg-gray-300 text-black text-[10px] px-[0.5px] rounded">
        {nodeId}
      </div>
      
      <div className="bg-white w-[160px] h-[57px] table-fixed rounded-md p-0 text-xs">
        <table className="table-fixed w-full h-full border-collapse">
        <tbody>
            <tr className="border-b border-black w-[160px]">
              <td className="border-r border-black text-gray-400 px-1 text-ellipsis overflow-hidden whitespace-nowrap w-[130px]">
                {TopText}
              </td>
              <td className="w-[30px] text-center">0</td>
            </tr>

            <tr className="w-[160px]">
              <td className="border-r border-black text-gray-400 px-1 text-ellipsis overflow-hidden whitespace-nowrap w-[110px]">
                {BottomText}
              </td>
              <td className="w-[30px] text-center">0</td>
            </tr>
          </tbody>
        </table>
        {data.bracketNodeType === "intermediate" && (
          <Handle
          type="source"
          position={Position.Right}
          onConnect={(params) => console.log("handle onConnect", params)}
          isConnectable={isConnectable}
  
        />)}
        {data.bracketNodeType === "intermediate" && (
          <Handle
          type="target"
          position={Position.Left}
          onConnect={(params) => console.log("handle onConnect", params)}
          isConnectable={isConnectable}
  
        />)}

{(data.bracketNodeType === "start") && (
          <div>
          <Handle
          type="source"
          position={Position.Right}
          onConnect={(params) => console.log("handle onConnect", params)}
          isConnectable={isConnectable}
        />
        </div>
)}

{data.bracketNodeType === "end" && (
          <div>
        <Handle
          type="target"
          position={Position.Left}
          onConnect={(params) => console.log("handle onConnect", params)}
          isConnectable={isConnectable}
        />
        </div>
)}
      </div>
    </div>
  );
});
