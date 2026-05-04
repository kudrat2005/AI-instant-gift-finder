import styles from "./GiftForm.module.css";

const PLATFORMS = ["Amazon", "Flipkart", "Etsy", "Other"];

export default function GiftForm({ form, onChange, onSubmit, loading, error }) {
  return (
    <form className={styles.card} onSubmit={onSubmit} noValidate>
      <div className={styles.grid}>
        <div className={styles.group}>
          <label className={styles.label} htmlFor="occasion">
            Occasion *
          </label>
          <input
            id="occasion"
            name="occasion"
            className={styles.input}
            type="text"
            placeholder="e.g. Birthday, Anniversary"
            value={form.occasion}
            onChange={onChange}
            disabled={loading}
          />
        </div>

        <div className={styles.group}>
          <label className={styles.label} htmlFor="relationship">
            Relationship *
          </label>
          <input
            id="relationship"
            name="relationship"
            className={styles.input}
            type="text"
            placeholder="e.g. Best Friend, Partner"
            value={form.relationship}
            onChange={onChange}
            disabled={loading}
          />
        </div>

        <div className={styles.group}>
          <label className={styles.label} htmlFor="budget">
            Budget *
          </label>
          <input
            id="budget"
            name="budget"
            className={styles.input}
            type="text"
            placeholder="e.g. ₹500–₹2000"
            value={form.budget}
            onChange={onChange}
            disabled={loading}
          />
        </div>

        <div className={styles.group}>
          <label className={styles.label} htmlFor="preferred_platform">
            Platform
          </label>
          <select
            id="preferred_platform"
            name="preferred_platform"
            className={styles.select}
            value={form.preferred_platform}
            onChange={onChange}
            disabled={loading}
          >
            {PLATFORMS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.group}>
          <label className={styles.label} htmlFor="instagram_id">
            Instagram ID
          </label>
          <input
            id="instagram_id"
            name="instagram_id"
            className={styles.input}
            type="text"
            placeholder="e.g. Jaatdevta (optional)"
            value={form.instagram_id}
            onChange={onChange}
            disabled={loading}
          />
        </div>

        <div className={styles.group}>
          <label className={styles.label} htmlFor="twitter_id">
            Twitter / X ID
          </label>
          <input
            id="twitter_id"
            name="twitter_id"
            className={styles.input}
            type="text"
            placeholder="e.g. Aryan_tweets (optional)"
            value={form.twitter_id}
            onChange={onChange}
            disabled={loading}
          />
        </div>

        <div className={`${styles.group} ${styles.full}`}>
          <label className={styles.label} htmlFor="description">
            Describe the person *
          </label>
          <textarea
            id="description"
            name="description"
            className={styles.textarea}
            placeholder="Loves hiking, reads sci-fi, obsessed with coffee, has a minimalist aesthetic..."
            value={form.description}
            onChange={onChange}
            disabled={loading}
            rows={4}
          />
        </div>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <button type="submit" className={styles.submitBtn} disabled={loading}>
        {loading ? (
          <>
            <span className={styles.spinner} />
            Finding perfect gifts...
          </>
        ) : (
          "✦ Find Perfect Gifts"
        )}
      </button>
    </form>
  );
}
