"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Sparkles,
  BookOpen,
  ArrowRight,
  Zap,
  TrendingUp,
  Globe,
} from "lucide-react";

export default function HomePage() {
  const router = useRouter();

  // Redirect to reels page immediately
  useEffect(() => {
    router.push("/reels");
  }, [router]);

  // Loading screen while redirecting
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-black to-blue-900 flex items-center justify-center">
      <div className="text-center space-y-6 animate-pulse">
        <div className="flex items-center justify-center space-x-3">
          <Sparkles className="h-12 w-12 text-purple-400 animate-spin" />
          <h1 className="text-4xl font-bold text-white">
            Research<span className="text-purple-400">Now</span>
          </h1>
        </div>
        <p className="text-gray-300 text-lg">
          Loading your personalized feed...
        </p>
      </div>
    </div>
  );
}
