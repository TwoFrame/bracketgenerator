import React, { memo } from "react";
import { Handle, Position } from "@xyflow/react";

export default memo(({ data, isConnectable }: any) => {
  return (
    <div className="w-[160px] h-[30px] font-extrabold text-sm border-b border-gray-400 overflow-hidden whitespace-nowrap text-center">
      {data.roundLabel}
    </div>
  );
});
