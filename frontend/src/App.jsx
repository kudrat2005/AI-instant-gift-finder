import { useState } from "react";
import GiftForm from "./components/GiftForm";
import GiftResults from "./components/GiftResults";
import axios from "axios";
import styles from "./App.module.css";

const INITIAL_FORM = {
  occasion: "",
  relationship: "",
  budget: "",
  preferred_platform: "Amazon",
  instagram_id: "",
  twitter_id: "",
  description: "",
};

export default function App() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResults(null);

    if (
      !form.occasion.trim() ||
      !form.budget.trim() ||
      !form.description.trim()
    ) {
      setError("Please fill in Occasion, Budget, and Description.");
      return;
    }

    setLoading(true);
    try {
      const { data } = await axios.post("/api/generate-gifts", form);
      setResults(data);
    } catch (err) {
      const msg =
        err.response?.data?.detail || "Something went wrong. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError("");
  };

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <header className={styles.header}>
          <div className={styles.headerIcon}>🎁</div>
          <div>
            <h1 className={styles.title}>AI Gift Finder</h1>
            <p className={styles.subtitle}>
              Describe the person — get personalized gift ideas instantly
            </p>
          </div>
        </header>

        {!results ? (
          <GiftForm
            form={form}
            onChange={handleChange}
            onSubmit={handleSubmit}
            loading={loading}
            error={error}
          />
        ) : (
          <GiftResults results={results} onReset={handleReset} />
        )}
      </div>
    </div>
  );
}
