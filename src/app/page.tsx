'use client';
import React from 'react';
import logo from '../../public/company logo.png';
import { Search } from '@/components/Search/Search';

export default function Home() {
  return (
    <div className="flex justify-betweenitems-center h-full w-full">
      <Search />
    </div>

  )
}
