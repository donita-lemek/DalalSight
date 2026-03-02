import { useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Info } from "lucide-react";
import "./index.css";

// Using standard fetch, no axios needed
const API_GATEWAY_URL = "http://localhost:3001/api/allocate";

type RiskCapacity = "Conservative" | "Moderate" | "Aggressive";

interface AllocationResult {
  risk_capacity: string;
  allocation: Record<string, number>;
  expected_portfolio_return: number;
}

const INDUSTRIES = [
  {
    id: "IT",
    name: "Information Technology",
    icon: "💻",
    desc: "TCS, Infosys",
    info: "Tech stocks generally provide high growth but can be volatile.",
  },
  {
    id: "Finance",
    name: "Financial Services",
    icon: "🏦",
    desc: "HDFC, ICICI",
    info: "Banks and NBFCs form the backbone of the economy, sensitive to interest rates.",
  },
  {
    id: "Energy",
    name: "Energy & Power",
    icon: "⚡",
    desc: "Reliance",
    info: "Traditional and renewable energy companies, often dividend-paying.",
  },
  {
    id: "Pharma",
    name: "Pharmaceuticals",
    icon: "💊",
    desc: "Sun Pharma",
    info: "Defensive sector, good during economic downturns.",
  },
  {
    id: "Manufacturing",
    name: "Manufacturing",
    icon: "🏭",
    desc: "Tata Steel",
    info: "Cyclical companies tied to economic expansion.",
  },
  {
    id: "FMCG",
    name: "FMCG",
    icon: "🛒",
    desc: "HUL",
    info: "Fast-Moving Consumer Goods. Very stable, defensive investments.",
  },
];

const RISKS = [
  {
    id: "Conservative",
    name: "Conservative",
    icon: "🛡️",
    desc: "Capital preservation, lower volatility",
    info: "Prioritizes not losing money over making high returns. Max 20% in any single stock.",
  },
  {
    id: "Moderate",
    name: "Moderate",
    icon: "⚖️",
    desc: "Balanced growth and risk",
    info: "A balanced approach aiming for steady growth. Max 40% in any single stock.",
  },
  {
    id: "Aggressive",
    name: "Aggressive",
    icon: "🚀",
    desc: "Maximized returns, higher volatility",
    info: "Willing to take big swings for outsized gains. Max 80% in any single stock.",
  },
];

// AMOLED Theme Colors for the pie chart
const COLORS = [
  "#00C49F",
  "#0088FE",
  "#FFBB28",
  "#FF8042",
  "#8884d8",
  "#ffc658",
  "#8dd1e1",
];

function App() {
  const [step, setStep] = useState<number>(1);
  const [risk, setRisk] = useState<RiskCapacity | null>(null);
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<AllocationResult | null>(null);
  const [showInfo, setShowInfo] = useState<string | null>(null);

  const toggleIndustry = (id: string) => {
    setSelectedIndustries((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id],
    );
  };

  const handleFetchAllocation = async () => {
    if (!risk || selectedIndustries.length === 0) return;

    setLoading(true);
    try {
      const res = await fetch(API_GATEWAY_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          risk_capacity: risk,
          selected_industries: selectedIndustries,
        }),
      });

      if (!res.ok) throw new Error("API Error");
      const data = await res.json();
      setResult(data);
      setStep(3);
    } catch (err) {
      console.error(err);
      alert(
        "Failed to fetch allocation. Ensure ML Engine and API Gateway are running.",
      );
    } finally {
      setLoading(false);
    }
  };

  const pieData = result
    ? Object.entries(result.allocation as Record<string, number>)
        .filter(([, weight]) => Number(weight) > 0.01)
        .map(([ticker, weight]) => ({
          name: ticker.replace(".NS", ""),
          value: parseFloat((Number(weight) * 100).toFixed(2)),
        }))
        .sort((a, b) => b.value - a.value)
    : [];

  const CustomTooltip = ({
    active,
    payload,
  }: {
    active?: boolean;
    payload?: { name: string; value: number }[];
  }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip glass-card" style={{ padding: "10px" }}>
          <p className="label">{`${payload[0].name} : ${payload[0].value}%`}</p>
        </div>
      );
    }
    return null;
  };
  return (
    <div className="auth-container">
      <header className="app-header">
        <div className="logo">
          <span className="eyes-icon">👀</span> DalalSight
        </div>
        <div className="educational-banner">AI-Powered Financial Optimizer</div>
      </header>

      <main className="container">
        {step === 1 && (
          <div className="hero glass-card">
            <h1>Discover Your Optimal Portfolio</h1>
            <p>
              DalalSight uses Modern Portfolio Theory and Machine Learning to
              recommend a data-driven Indian stock market asset division
              tailored for you.
            </p>

            <div className="educational-panel">
              <Info className="info-icon" size={24} />
              <div>
                <strong>How it works:</strong> We use historical data and AI
                forecasts to find the combination of stocks that maximizes your
                expected returns for a given level of risk (the Sharpe Ratio).
              </div>
            </div>

            <button className="btn" onClick={() => setStep(2)}>
              Start the Survey <span>→</span>
            </button>
          </div>
        )}

        {step === 2 && (
          <div
            className="glass-card"
            style={{ animation: "slideUp 0.5s ease" }}
          >
            <h2 style={{ marginBottom: "2rem", textAlign: "center" }}>
              Investment Profile
            </h2>

            <div className="survey-question">
              <div className="question-header">
                <h3>1. What is your risk capacity?</h3>
              </div>
              <div className="options-grid">
                {RISKS.map((r) => (
                  <div
                    key={r.id}
                    className={`option-card ${risk === r.id ? "selected pulse-primary" : ""}`}
                    onClick={() => setRisk(r.id as RiskCapacity)}
                    onMouseEnter={() => setShowInfo(r.id)}
                    onMouseLeave={() => setShowInfo(null)}
                  >
                    <div className="option-icon">{r.icon}</div>
                    <div className="option-title">{r.name}</div>
                    <div className="option-desc">{r.desc}</div>

                    {showInfo === r.id && (
                      <div className="edu-tooltip">{r.info}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="survey-question">
              <h3>
                2. Which industries interest you the most? (Select at least 1)
              </h3>
              <div className="options-grid">
                {INDUSTRIES.map((ind) => (
                  <div
                    key={ind.id}
                    className={`option-card ${selectedIndustries.includes(ind.id) ? "selected" : ""}`}
                    onClick={() => toggleIndustry(ind.id)}
                    onMouseEnter={() => setShowInfo(ind.id)}
                    onMouseLeave={() => setShowInfo(null)}
                  >
                    <div className="option-icon">{ind.icon}</div>
                    <div className="option-title">{ind.name}</div>
                    <div className="option-desc">{ind.desc}</div>

                    {showInfo === ind.id && (
                      <div className="edu-tooltip">{ind.info}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div style={{ textAlign: "center", marginTop: "3rem" }}>
              <button
                className="btn"
                disabled={!risk || selectedIndustries.length === 0 || loading}
                onClick={handleFetchAllocation}
              >
                {loading
                  ? "Analyzing Market Data..."
                  : "Generate Allocation 📊"}
              </button>
            </div>
          </div>
        )}

        {step === 3 && result && (
          <div
            className="glass-card allocation-results"
            style={{ animation: "slideUp 0.5s ease-out" }}
          >
            <h2 style={{ textAlign: "center", marginBottom: "1rem" }}>
              Your Recommended Portfolio
            </h2>
            <p style={{ textAlign: "center", color: "var(--text-secondary)" }}>
              Optimized for a{" "}
              <strong style={{ color: "var(--accent-primary)" }}>
                {result.risk_capacity}
              </strong>{" "}
              profile maximizing the Sharpe Ratio.
            </p>

            <div className="allocation-grid">
              <div className="stat-card">
                <div
                  className="option-title"
                  style={{ display: "flex", alignItems: "center", gap: "8px" }}
                >
                  Expected Annual Return
                  <div className="tooltip-container">
                    <Info size={16} color="var(--text-secondary)" />
                    <span className="tooltip-text">
                      Calculated using Level-2 Stacked Meta-Model predictions
                      multiplied by your optimal asset weights.
                    </span>
                  </div>
                </div>
                <div className="stat-value">
                  {(result.expected_portfolio_return * 100).toFixed(2)}%
                </div>

                <div style={{ marginTop: "2rem" }}>
                  <div className="option-title">Why this mix?</div>
                  <p
                    style={{
                      fontSize: "0.9rem",
                      color: "var(--text-secondary)",
                      marginTop: "0.5rem",
                    }}
                  >
                    Modern Portfolio Theory dictates that holding a mix of
                    non-correlated assets reduces overall risk. The AI found
                    these specific weights to give you the highest return per
                    unit of volatility.
                  </p>
                </div>
              </div>

              <div className="stat-card" style={{ minHeight: "350px" }}>
                <div
                  className="option-title"
                  style={{ textAlign: "center", marginBottom: "1rem" }}
                >
                  Asset Allocation Visualization
                </div>
                <div style={{ width: "100%", height: "300px" }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                        stroke="var(--bg-secondary)"
                        strokeWidth={2}
                        animationBegin={0}
                        animationDuration={1500}
                        animationEasing="ease-out"
                      >
                        {pieData.map((_, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <RechartsTooltip content={<CustomTooltip />} />
                      <Legend verticalAlign="bottom" height={36} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div style={{ textAlign: "center", marginTop: "3rem" }}>
              <button
                className="btn"
                onClick={() => setStep(1)}
                style={{
                  background: "transparent",
                  color: "var(--text-primary)",
                  border: "1px solid var(--card-border)",
                }}
              >
                Start Over
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
