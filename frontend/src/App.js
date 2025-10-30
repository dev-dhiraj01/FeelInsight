import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import "./App.css";

// Import shadcn components
import { Button } from "./components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";
import {
  Brain,
  Heart,
  TrendingUp,
  Users,
  ChevronRight,
  Sparkles,
  BarChart3,
  History,
  LogOut,
} from "lucide-react";


//   process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const BACKEND_URL = "http://localhost:8000";
const API = `${BACKEND_URL}/api`;

// Enhanced Auth Context with better error handling
const AuthContext = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get token from localStorage on component mount
    const storedToken = localStorage.getItem("token");
    if (storedToken) {
      setToken(storedToken);
      axios.defaults.headers.common["Authorization"] = `Bearer ${storedToken}`;
      fetchCurrentUser(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async (authToken = token) => {
    try {
      console.log(
        "Fetching current user with token:",
        authToken ? "Token present" : "No token"
      );
      const response = await axios.get(`${API}/auth/me`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
      setUser(response.data);
      console.log("User fetched successfully:", response.data);
    } catch (error) {
      console.error(
        "Error fetching user:",
        error.response?.data || error.message
      );
      // Only logout if it's an authentication error
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.log("Authentication error, logging out...");
        logout();
      } else {
        // For other errors, just show a warning but don't logout
        console.warn("Failed to fetch user, but keeping session");
      }
    } finally {
      setLoading(false);
    }
  };

  const login = (newToken, userData) => {
    console.log("Logging in user:", userData);
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setUser(userData);
    axios.defaults.headers.common["Authorization"] = `Bearer ${newToken}`;
  };

  const logout = () => {
    console.log("Logging out user");
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common["Authorization"];
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return children({ user, login, logout });
};

// Landing Page Component (unchanged)
const LandingPage = ({ onGetStarted }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="container mx-auto px-6 py-8">
        <nav className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-slate-800">
              FeelInsight
            </span>
          </div>
          <Button
            onClick={onGetStarted}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Get Started
          </Button>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold text-slate-800 mb-6 leading-tight">
            Understand Your
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
              {" "}
              Emotions
            </span>
          </h1>
          <p className="text-xl text-slate-600 mb-8 leading-relaxed">
            Advanced AI-powered sentiment analysis that transforms your thoughts
            into meaningful insights. Discover patterns, track emotions, and get
            personalized visual recommendations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              onClick={onGetStarted}
              size="lg"
              className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <Sparkles className="mr-2 h-5 w-5" />
              Start Analysis
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="text-lg px-8 py-4 rounded-full border-2 border-blue-200 hover:border-blue-300"
            >
              Learn More
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-slate-800 mb-4">
            Powerful Features
          </h2>
          <p className="text-xl text-slate-600">
            Everything you need to understand and track your emotional
            well-being
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <Card className="text-center p-8 bg-white/70 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <Brain className="h-8 w-8 text-blue-600" />
              </div>
              <CardTitle className="text-xl text-slate-800">
                AI Sentiment Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-600">
                Advanced AI models analyze your text to detect emotions, tone,
                and sentiment with incredible accuracy.
              </p>
            </CardContent>
          </Card>

          <Card className="text-center p-8 bg-white/70 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <Heart className="h-8 w-8 text-green-600" />
              </div>
              <CardTitle className="text-xl text-slate-800">
                Image Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-600">
                Get personalized image suggestions based on your emotional state
                to enhance your mood and well-being.
              </p>
            </CardContent>
          </Card>

          <Card className="text-center p-8 bg-white/70 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <div className="mx-auto w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                <TrendingUp className="h-8 w-8 text-purple-600" />
              </div>
              <CardTitle className="text-xl text-slate-800">
                Analytics & Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-600">
                Track your emotional patterns over time with detailed analytics
                and actionable insights.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-20">
        <Card className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white border-0 shadow-2xl">
          <CardContent className="text-center p-12">
            <h3 className="text-3xl font-bold mb-4">
              Ready to Explore Your Emotions?
            </h3>
            <p className="text-blue-100 text-lg mb-8">
              Join thousands of users who have gained valuable insights into
              their emotional well-being.
            </p>
            <Button
              onClick={onGetStarted}
              size="lg"
              variant="secondary"
              className="text-lg px-8 py-4 rounded-full bg-white text-blue-600 hover:bg-blue-50"
            >
              Get Started Now <ChevronRight className="ml-2 h-5 w-5" />
            </Button>
          </CardContent>
        </Card>
      </section>
    </div>
  );
};

// Enhanced Auth Component with better validation and error handling
const AuthPage = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
  });
  const [loading, setLoading] = useState(false);

  const validateForm = () => {
    if (!formData.email.trim()) {
      toast.error("Email is required");
      return false;
    }

    if (!formData.password.trim()) {
      toast.error("Password is required");
      return false;
    }

    if (formData.password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return false;
    }

    if (!isLogin && !formData.name.trim()) {
      toast.error("Name is required for registration");
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      toast.error("Please enter a valid email address");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const endpoint = isLogin ? "/auth/login" : "/auth/register";
      const payload = isLogin
        ? { email: formData.email.trim(), password: formData.password }
        : {
            email: formData.email.trim(),
            password: formData.password,
            name: formData.name.trim(),
          };

      console.log(
        `Making ${isLogin ? "login" : "registration"} request to:`,
        `${API}${endpoint}`
      );
      console.log("Payload:", { ...payload, password: "[REDACTED]" });

      const response = await axios.post(`${API}${endpoint}`, payload, {
        headers: {
          "Content-Type": "application/json",
        },
        timeout: 10000, // 10 second timeout
      });

      console.log("Authentication successful:", response.data);

      // Check if response has the expected structure
      if (!response.data.access_token) {
        throw new Error("No access token received from server");
      }

      onLogin(response.data.access_token, response.data.user);
      toast.success(
        isLogin ? "Welcome back!" : "Account created successfully!"
      );
    } catch (error) {
      console.error("Authentication error:", error);

      let errorMessage = "Authentication failed";

      if (error.code === "ECONNREFUSED" || error.code === "ERR_NETWORK") {
        errorMessage =
        error.code+
          "Cannot connect to server. Please check if the backend is running.";
      } else if (error.timeout) {
        errorMessage = "Request timed out. Please try again.";
      } else if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const data = error.response.data;

        console.log("Error response:", { status, data });

        if (status === 400) {
          errorMessage = data?.detail || data?.message || "Invalid input data";
        } else if (status === 401) {
          errorMessage = "Invalid email or password";
        } else if (status === 409) {
          errorMessage = "Email already exists. Please try logging in instead.";
        } else if (status === 422) {
          errorMessage = data?.detail?.[0]?.msg || "Validation error";
        } else if (status >= 500) {
          errorMessage = "Server error. Please try again later.";
        } else {
          errorMessage =
            data?.detail || data?.message || `Server error (${status})`;
        }
      }

      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <Card className="w-full max-w-md bg-white/90 backdrop-blur-sm shadow-2xl border-0">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <Brain className="h-8 w-8 text-blue-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-slate-800">
            {isLogin ? "Welcome Back" : "Create Account"}
          </CardTitle>
          <CardDescription>
            {isLogin
              ? "Sign in to your account"
              : "Start your emotional journey"}
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="Your full name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  required={!isLogin}
                  className="mt-1"
                />
              </div>
            )}

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                required
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                required
                minLength={6}
                className="mt-1"
              />
            </div>

            <Button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700"
              disabled={loading}
            >
              {loading
                ? "Please wait..."
                : isLogin
                ? "Sign In"
                : "Create Account"}
            </Button>
          </form>
        </CardContent>

        <CardFooter className="text-center">
          <p className="text-sm text-slate-600">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setFormData({ email: "", password: "", name: "" }); // Clear form when switching
              }}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              {isLogin ? "Sign up" : "Sign in"}
            </button>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
};

// Dashboard Component with enhanced error handling
const Dashboard = ({ user, logout }) => {
  const [activeTab, setActiveTab] = useState("analyze");
  const [analysisText, setAnalysisText] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistory();
    fetchStats();
  }, []);

  const handleApiError = (error, defaultMessage) => {
    console.error("API Error:", error);

    if (error.response?.status === 401) {
      toast.error("Session expired. Please log in again.");
      logout();
      return;
    }

    const errorMessage =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      defaultMessage;
    toast.error(errorMessage);
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API}/sentiment/history`);
      setHistory(response.data || []);
    } catch (error) {
      handleApiError(error, "Failed to load history");
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/sentiment/stats`);
      setStats(response.data);
    } catch (error) {
      handleApiError(error, "Failed to load statistics");
    }
  };

  const handleAnalyze = async () => {
    if (!analysisText.trim()) {
      toast.error("Please enter some text to analyze");
      return;
    }

    if (analysisText.trim().length < 10) {
      toast.error("Please enter at least 10 characters for better analysis");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/sentiment/analyze`, {
        text: analysisText.trim(),
        include_emotions: true,
      });

      setAnalysisResult(response.data.analysis);
      setAnalysisText("");
      toast.success("Analysis completed!");

      // Refresh history and stats
      fetchHistory();
      fetchStats();
    } catch (error) {
      handleApiError(error, "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (score) => {
    if (score > 0.2) return "text-green-600 bg-green-50";
    if (score < -0.2) return "text-red-600 bg-red-50";
    return "text-yellow-600 bg-yellow-50";
  };

  const getSentimentEmoji = (label) => {
    switch (label) {
      case "positive":
        return "😊";
      case "negative":
        return "😔";
      default:
        return "😐";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-blue-600" />
              <span className="text-2xl font-bold text-slate-800">
                FeelInsight
              </span>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-slate-600">
                Welcome, {user?.name || "User"}!
              </span>
              <Button variant="outline" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="space-y-6"
        >
          <TabsList className="grid w-full grid-cols-3 bg-white/70 backdrop-blur-sm">
            <TabsTrigger
              value="analyze"
              className="flex items-center space-x-2"
            >
              <Sparkles className="h-4 w-4" />
              <span>Analyze</span>
            </TabsTrigger>
            <TabsTrigger
              value="history"
              className="flex items-center space-x-2"
            >
              <History className="h-4 w-4" />
              <span>History</span>
            </TabsTrigger>
            <TabsTrigger value="stats" className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>Analytics</span>
            </TabsTrigger>
          </TabsList>

          {/* Analyze Tab */}
          <TabsContent value="analyze" className="space-y-6">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-blue-600" />
                  <span>Emotion Analysis</span>
                </CardTitle>
                <CardDescription>
                  Share your thoughts and let AI analyze the emotions and
                  sentiment
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="analysis-text">What's on your mind?</Label>
                  <Textarea
                    id="analysis-text"
                    placeholder="Type your thoughts, feelings, or any text you'd like to analyze... (minimum 10 characters)"
                    value={analysisText}
                    onChange={(e) => setAnalysisText(e.target.value)}
                    className="mt-2 min-h-[120px]"
                  />
                  <p className="text-sm text-slate-500 mt-1">
                    {analysisText.length}/1000 characters
                  </p>
                </div>

                <Button
                  onClick={handleAnalyze}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  disabled={loading || analysisText.trim().length < 10}
                >
                  {loading ? "Analyzing..." : "Analyze Sentiment"}
                </Button>
              </CardContent>
            </Card>

            {/* Analysis Results */}
            {analysisResult && (
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Heart className="h-5 w-5 text-red-500" />
                    <span>Analysis Results</span>
                  </CardTitle>
                </CardHeader>

                <CardContent className="space-y-6">
                  {/* Sentiment Overview */}
                  <div className="text-center space-y-2">
                    <div className="text-6xl">
                      {getSentimentEmoji(analysisResult.sentiment_label)}
                    </div>
                    <Badge
                      className={`text-lg px-4 py-2 ${getSentimentColor(
                        analysisResult.sentiment_score
                      )}`}
                    >
                      {analysisResult.sentiment_label?.toUpperCase() ||
                        "NEUTRAL"}
                    </Badge>
                    <p className="text-2xl font-bold text-slate-800">
                      Score:{" "}
                      {((analysisResult.sentiment_score || 0) * 100).toFixed(1)}
                      %
                    </p>
                  </div>

                  {/* Emotion Breakdown */}
                  {analysisResult.emotions && (
                    <div>
                      <h4 className="font-semibold text-slate-800 mb-4">
                        Emotion Breakdown
                      </h4>
                      <div className="grid grid-cols-2 gap-4">
                        {Object.entries(analysisResult.emotions).map(
                          ([emotion, score]) => (
                            <div key={emotion} className="space-y-2">
                              <div className="flex justify-between text-sm">
                                <span className="capitalize text-slate-600">
                                  {emotion}
                                </span>
                                <span className="font-medium">
                                  {((score || 0) * 100).toFixed(0)}%
                                </span>
                              </div>
                              <Progress
                                value={(score || 0) * 100}
                                className="h-2"
                              />
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}

                  {/* Keywords */}
                  {analysisResult.keywords &&
                    analysisResult.keywords.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-slate-800 mb-3">
                          Suggested Image Keywords
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {analysisResult.keywords.map((keyword, index) => (
                            <Badge
                              key={index}
                              variant="outline"
                              className="text-sm"
                            >
                              {keyword}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <History className="h-5 w-5 text-blue-600" />
                  <span>Analysis History</span>
                </CardTitle>
                <CardDescription>
                  Your recent sentiment analyses
                </CardDescription>
              </CardHeader>

              <CardContent>
                {history.length === 0 ? (
                  <div className="text-center py-8 text-slate-500">
                    <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No analyses yet. Start by analyzing some text!</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {history.map((item) => (
                      <Card
                        key={item.analysis_id || Math.random()}
                        className="bg-slate-50"
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-2">
                            <Badge
                              className={getSentimentColor(
                                item.sentiment_score || 0
                              )}
                            >
                              {item.sentiment_label || "neutral"}
                            </Badge>
                            <span className="text-sm text-slate-500">
                              {new Date(item.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <p className="text-sm text-slate-600 mb-2">
                            {item.text}
                          </p>
                          {item.keywords && item.keywords.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {item.keywords.map((keyword, idx) => (
                                <Badge
                                  key={idx}
                                  variant="outline"
                                  className="text-xs"
                                >
                                  {keyword}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Stats Tab */}
          <TabsContent value="stats">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                  <span>Your Analytics</span>
                </CardTitle>
                <CardDescription>
                  Overview of your emotional patterns
                </CardDescription>
              </CardHeader>

              <CardContent>
                {!stats ? (
                  <div className="text-center py-8 text-slate-500">
                    <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Loading your analytics...</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600 mb-2">
                        {stats.total_analyses || 0}
                      </div>
                      <p className="text-slate-600">Total Analyses</p>
                    </div>

                    {stats.sentiment_distribution && (
                      <div>
                        <h4 className="font-semibold text-slate-800 mb-4">
                          Sentiment Distribution
                        </h4>
                        <div className="space-y-3">
                          {Object.entries(stats.sentiment_distribution).map(
                            ([sentiment, data]) => (
                              <div key={sentiment} className="space-y-2">
                                <div className="flex justify-between items-center">
                                  <span className="capitalize text-slate-600">
                                    {sentiment}
                                  </span>
                                  <div className="text-sm">
                                    <span className="font-medium">
                                      {data.count || 0}
                                    </span>
                                    <span className="text-slate-500 ml-2">
                                      (Avg: {data.average_score > 0 ? "+" : ""}
                                      {(data.average_score || 0).toFixed(2)})
                                    </span>
                                  </div>
                                </div>
                                <Progress
                                  value={
                                    stats.total_analyses > 0
                                      ? ((data.count || 0) /
                                          stats.total_analyses) *
                                        100
                                      : 0
                                  }
                                  className="h-3"
                                />
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <AuthContext>
        {({ user, login, logout }) => (
          <BrowserRouter>
            <Routes>
              <Route
                path="/"
                element={
                  user ? (
                    <Navigate to="/dashboard" replace />
                  ) : (
                    <LandingPage
                      onGetStarted={() => (window.location.href = "/auth")}
                    />
                  )
                }
              />
              <Route
                path="/auth"
                element={
                  user ? (
                    <Navigate to="/dashboard" replace />
                  ) : (
                    <AuthPage onLogin={login} />
                  )
                }
              />
              <Route
                path="/dashboard"
                element={
                  user ? (
                    <Dashboard user={user} logout={logout} />
                  ) : (
                    <Navigate to="/auth" replace />
                  )
                }
              />
            </Routes>
            <Toaster position="top-center" />
          </BrowserRouter>
        )}
      </AuthContext>
    </div>
  );
}

export default App;
