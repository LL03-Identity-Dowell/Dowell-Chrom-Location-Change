"use client";
import React from "react";
import { Search } from "@/components/Search/Search";

export default function Home() {
  return (
    <div className="flex justify-between items-center h-full w-full">
      <Search />
    </div>
  );
}
