"use client";

import { useState, useEffect, useRef } from "react";
import {
  ChevronUp,
  ChevronDown,
  Heart,
  Bookmark,
  Share2,
  ExternalLink,
  Users,
  Calendar,
  TrendingUp,
  Sparkles,
  X,
} from "lucide-react";

interface Paper {
  id: number;
  title: string;
  abstract: string;
  authors: string[];
  publication_year: number;
  publication_date: string;
  journal: string;
  fields_of_study: string[];
  citation_count: number;
  is_open_access: boolean;
  pdf_url: string;
  arxiv_id: string;
  doi: string;
  ai_summary?: {
    key_findings: string[];
    methodology: string;
    impact: string;
    conclusion: string;
  };
}

export default function ReelsPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [liked, setLiked] = useState<Set<number>>(new Set());
  const [bookmarked, setBookmarked] = useState<Set<number>>(new Set());
  const [showSummary, setShowSummary] = useState(true);
  const [selectedField, setSelectedField] = useState<string>("");
  const containerRef = useRef<HTMLDivElement>(null);
  const touchStartY = useRef<number>(0);

  const fields = [
    "All Fields",
    "Computer Science",
    "Physics",
    "Mathematics",
    "Biology",
    "Medicine",
    "Engineering",
    "Chemistry",
    "Psychology",
    "Economics",
    "Environmental Science",
  ];

  useEffect(() => {
    fetchPapers();
  }, [selectedField]);

  const fetchPapers = async () => {
    try {
      setLoading(true);
      const fieldParam =
        selectedField && selectedField !== "All Fields"
          ? `&field=${encodeURIComponent(selectedField)}`
          : "";
      const response = await fetch(
        `http://localhost:8000/api/v1/papers/random/?count=20${fieldParam}`,
      );
      const data = await response.json();
      setPapers(data);
      setCurrentIndex(0);
    } catch (error) {
      console.error("Error fetching papers:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (currentIndex < papers.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowSummary(true);
    } else {
      fetchPapers();
      setCurrentIndex(0);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setShowSummary(true);
    }
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    const touchEndY = e.changedTouches[0].clientY;
    const diff = touchStartY.current - touchEndY;

    if (Math.abs(diff) > 50) {
      if (diff > 0) {
        handleNext();
      } else {
        handlePrevious();
      }
    }
  };

  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.key === "ArrowDown") handleNext();
    if (e.key === "ArrowUp") handlePrevious();
  };

  useEffect(() => {
    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [currentIndex, papers.length]);

  const toggleLike = () => {
    const newLiked = new Set(liked);
    if (liked.has(papers[currentIndex]?.id)) {
      newLiked.delete(papers[currentIndex]?.id);
    } else {
      newLiked.add(papers[currentIndex]?.id);
    }
    setLiked(newLiked);
  };

  const toggleBookmark = () => {
    const newBookmarked = new Set(bookmarked);
    if (bookmarked.has(papers[currentIndex]?.id)) {
      newBookmarked.delete(papers[currentIndex]?.id);
    } else {
      newBookmarked.add(papers[currentIndex]?.id);
    }
    setBookmarked(newBookmarked);
  };

  const handleShare = async () => {
    const paper = papers[currentIndex];
    if (navigator.share) {
      try {
        await navigator.share({
          title: paper.title,
          text: `Check out this research paper: ${paper.title}`,
          url: window.location.href,
        });
      } catch (error) {
        console.log("Error sharing:", error);
      }
    }
  };

  if (loading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-black">
        <div className="text-white text-center">
          <div className="relative">
            <Sparkles className="h-12 w-12 animate-pulse mx-auto mb-4 text-purple-400" />
            <div className="absolute inset-0 h-12 w-12 mx-auto animate-ping">
              <Sparkles className="h-12 w-12 text-purple-400 opacity-75" />
            </div>
          </div>
          <p className="text-xl font-semibold mb-2">Loading Research Papers</p>
          <p className="text-sm text-gray-400">
            Finding papers with 100+ citations...
          </p>
        </div>
      </div>
    );
  }

  if (papers.length === 0) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-black text-white">
        <p>No papers available</p>
      </div>
    );
  }

  const currentPaper = papers[currentIndex];

  return (
    <div
      ref={containerRef}
      className="h-screen w-screen bg-black overflow-hidden relative"
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-black to-blue-900/20" />

      {/* Main content area */}
      <div className="relative h-full flex items-center justify-center p-4 md:p-8">
        <div className="max-w-4xl w-full h-full flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between mb-4 text-white z-10">
            <div className="flex items-center space-x-3">
              <Sparkles className="h-6 w-6 text-purple-400" />
              <span className="font-bold text-xl tracking-tight">
                Research Reels
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedField}
                onChange={(e) => setSelectedField(e.target.value)}
                className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {fields.map((field) => (
                  <option
                    key={field}
                    value={field === "All Fields" ? "" : field}
                  >
                    {field}
                  </option>
                ))}
              </select>
              <div className="text-sm text-gray-400">
                {currentIndex + 1} / {papers.length}
              </div>
            </div>
          </div>

          {/* Paper card */}
          <div className="flex-1 bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl shadow-2xl overflow-hidden relative border border-gray-700">
            {/* Field tag */}
            <div className="absolute top-4 left-4 z-20">
              <span className="px-4 py-2 bg-purple-600/90 backdrop-blur-sm text-white rounded-full text-sm font-semibold shadow-lg">
                {currentPaper.fields_of_study[0]}
              </span>
            </div>

            {/* Open Access badge */}
            {currentPaper.is_open_access && (
              <div className="absolute top-4 right-4 z-20">
                <span className="px-3 py-1.5 bg-green-600/90 backdrop-blur-sm text-white rounded-full text-xs font-semibold shadow-lg uppercase tracking-wider">
                  Open Access
                </span>
              </div>
            )}

            {/* Content */}
            <div className="h-full overflow-y-auto p-6 md:p-10 pb-32">
              {/* Title */}
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-6 leading-tight tracking-tight">
                {currentPaper.title}
              </h1>

              {/* Meta information */}
              <div className="flex flex-wrap gap-4 mb-6 text-gray-300 text-sm">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-gray-400" />
                  <span className="font-medium">
                    {currentPaper.authors.slice(0, 3).join(", ")}
                  </span>
                  {currentPaper.authors.length > 3 && (
                    <span className="text-gray-400">
                      +{currentPaper.authors.length - 3}
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-gray-400" />
                  <span className="font-medium">
                    {currentPaper.publication_year}
                  </span>
                </div>
                <div className="flex items-center space-x-2 px-3 py-1.5 bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-lg border border-purple-500/30">
                  <TrendingUp className="h-4 w-4 text-purple-400" />
                  <span className="font-semibold text-purple-300">
                    {currentPaper.citation_count.toLocaleString()} citations
                  </span>
                  <span className="text-xs text-gray-400 ml-1">
                    (Highly cited)
                  </span>
                </div>
              </div>

              {/* Journal */}
              <div className="mb-6">
                <span className="px-3 py-1.5 bg-gray-800 text-gray-300 rounded-lg text-sm border border-gray-700 font-medium">
                  {currentPaper.journal}
                </span>
              </div>

              {/* Abstract */}
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-white mb-3 uppercase tracking-wider text-sm">
                  Abstract
                </h2>
                <p className="text-gray-300 leading-relaxed text-base">
                  {currentPaper.abstract}
                </p>
              </div>

              {/* AI Summary section */}
              <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 rounded-xl p-6 border border-purple-500/20 mb-6">
                <div className="flex items-center space-x-3 mb-5">
                  <Sparkles className="h-5 w-5 text-purple-400" />
                  <h2 className="text-lg font-semibold text-white uppercase tracking-wider">
                    AI-Generated Summary
                  </h2>
                </div>

                <div className="space-y-5 text-gray-300">
                  <div>
                    <h3 className="font-semibold text-purple-400 mb-3 uppercase tracking-wide text-sm">
                      Key Findings
                    </h3>
                    {currentPaper.ai_summary?.key_findings &&
                    currentPaper.ai_summary.key_findings.length > 0 ? (
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        {currentPaper.ai_summary.key_findings.map(
                          (finding, idx) => (
                            <li key={idx}>{finding}</li>
                          ),
                        )}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-400">
                        Key findings analysis in progress...
                      </p>
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-blue-400 mb-3 uppercase tracking-wide text-sm">
                      Methodology
                    </h3>
                    <p className="text-sm">
                      {currentPaper.ai_summary?.methodology ||
                        "Methodology analysis in progress..."}
                    </p>
                  </div>
                  <div>
                    <h3 className="font-semibold text-green-400 mb-3 uppercase tracking-wide text-sm">
                      Impact
                    </h3>
                    <p className="text-sm">
                      {currentPaper.ai_summary?.impact ||
                        "Impact analysis in progress..."}
                    </p>
                  </div>
                  <div>
                    <h3 className="font-semibold text-yellow-400 mb-3 uppercase tracking-wide text-sm">
                      Conclusion
                    </h3>
                    <p className="text-sm">
                      {currentPaper.ai_summary?.conclusion ||
                        "Conclusion analysis in progress..."}
                    </p>
                  </div>
                </div>
              </div>

              {/* Links */}
              <div className="flex flex-wrap gap-3 mt-8">
                {currentPaper.pdf_url && (
                  <a
                    href={currentPaper.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all font-medium"
                  >
                    <ExternalLink className="h-4 w-4" />
                    <span>Read PDF</span>
                  </a>
                )}
                {currentPaper.html_url && (
                  <a
                    href={currentPaper.html_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all font-medium"
                  >
                    <ExternalLink className="h-4 w-4" />
                    <span>View Paper</span>
                  </a>
                )}
                {currentPaper.doi && (
                  <a
                    href={`https://doi.org/${currentPaper.doi}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 px-5 py-2.5 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all font-medium"
                  >
                    <ExternalLink className="h-4 w-4" />
                    <span>DOI</span>
                  </a>
                )}
                {currentPaper.arxiv_id && (
                  <a
                    href={`https://arxiv.org/abs/${currentPaper.arxiv_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 px-5 py-2.5 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all font-medium"
                  >
                    <ExternalLink className="h-4 w-4" />
                    <span>arXiv</span>
                  </a>
                )}
              </div>
            </div>
          </div>

          {/* Navigation hints */}
          <div className="flex items-center justify-center mt-4 text-gray-400 text-xs space-x-6">
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-gray-800/50 rounded-lg">
              <ChevronUp className="h-3 w-3" />
              <span className="uppercase tracking-wider">Previous</span>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-gray-800/50 rounded-lg">
              <ChevronDown className="h-3 w-3" />
              <span className="uppercase tracking-wider">Next</span>
            </div>
            <div className="text-gray-500">or use arrow keys</div>
          </div>
        </div>
      </div>

      {/* Action buttons (right side) */}
      <div className="absolute right-4 md:right-8 top-1/2 -translate-y-1/2 flex flex-col space-y-6 z-30">
        <button
          onClick={toggleLike}
          className={`flex flex-col items-center space-y-1 transition ${
            liked.has(currentPaper?.id)
              ? "text-red-500"
              : "text-white hover:text-red-400"
          }`}
        >
          <div className="p-3 bg-gray-900/80 backdrop-blur-sm rounded-full hover:scale-110 transition">
            <Heart
              className="h-6 w-6"
              fill={liked.has(currentPaper?.id) ? "currentColor" : "none"}
            />
          </div>
          <span className="text-xs font-medium">Like</span>
        </button>

        <button
          onClick={toggleBookmark}
          className={`flex flex-col items-center space-y-1 transition ${
            bookmarked.has(currentPaper?.id)
              ? "text-yellow-500"
              : "text-white hover:text-yellow-400"
          }`}
        >
          <div className="p-3 bg-gray-900/80 backdrop-blur-sm rounded-full hover:scale-110 transition">
            <Bookmark
              className="h-6 w-6"
              fill={bookmarked.has(currentPaper?.id) ? "currentColor" : "none"}
            />
          </div>
          <span className="text-xs font-medium">Save</span>
        </button>

        <button
          onClick={handleShare}
          className="flex flex-col items-center space-y-1 text-white hover:text-blue-400 transition"
        >
          <div className="p-3 bg-gray-900/80 backdrop-blur-sm rounded-full hover:scale-110 transition">
            <Share2 className="h-6 w-6" />
          </div>
          <span className="text-xs font-medium">Share</span>
        </button>
      </div>

      {/* Navigation buttons */}
      <button
        onClick={handlePrevious}
        disabled={currentIndex === 0}
        className={`absolute top-1/2 left-4 -translate-y-1/2 p-3 bg-gray-900/80 backdrop-blur-sm rounded-full z-20 transition ${
          currentIndex === 0
            ? "opacity-30 cursor-not-allowed"
            : "hover:bg-gray-800 hover:scale-110"
        }`}
      >
        <ChevronUp className="h-6 w-6 text-white" />
      </button>

      <button
        onClick={handleNext}
        className="absolute bottom-20 left-1/2 -translate-x-1/2 p-4 bg-purple-600 hover:bg-purple-700 rounded-full z-20 transition hover:scale-110 shadow-lg"
      >
        <ChevronDown className="h-7 w-7 text-white" />
      </button>
    </div>
  );
}
