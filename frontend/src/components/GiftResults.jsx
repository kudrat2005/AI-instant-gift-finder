import styles from "./GiftResults.module.css";

export default function GiftResults({ results, onReset }) {
  const { occasion, relationship, platform, gift_suggestions } = results;

  return (
    <div className={styles.wrapper}>
      <div className={styles.meta}>
        <div className={styles.metaLeft}>
          <h2 className={styles.heading}>Gift Ideas</h2>
          <div className={styles.tags}>
            {occasion && <span className={styles.tag}>🎉 {occasion}</span>}
            {relationship && (
              <span className={styles.tag}>👤 {relationship}</span>
            )}
            {platform && <span className={styles.tag}>🛍️ {platform}</span>}
          </div>
        </div>
        <button className={styles.resetBtn} onClick={onReset}>
          ← New Search
        </button>
      </div>

      <div className={styles.grid}>
        {gift_suggestions.map((gift, i) => (
          <GiftCard key={i} gift={gift} index={i} platform={platform} />
        ))}
      </div>
    </div>
  );
}

function GiftCard({ gift, index, platform }) {
  return (
    <div className={styles.card}>
      <div className={styles.cardIndex}>{index + 1}</div>
      <div className={styles.cardBody}>
        <h3 className={styles.cardTitle}>{gift.title}</h3>
        <p className={styles.cardReason}>{gift.reason}</p>
        <div className={styles.cardFooter}>
          <span className={styles.priceBadge}>{gift.price_range}</span>
          <a
            className={styles.shopLink}
            href={gift.link}
            target="_blank"
            rel="noopener noreferrer"
          >
            Shop on {platform} ↗
          </a>
        </div>
      </div>
    </div>
  );
}
