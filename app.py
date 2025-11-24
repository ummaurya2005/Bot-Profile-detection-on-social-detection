from flask import Flask, render_template, request
import regex as re
import emoji
import numpy as np

app = Flask(__name__)

# --------------------------------------
# Emoji / behavior extractor
# --------------------------------------
def extract_emoji_behavior(text):
    text = str(text)
    emojis_list = [c for c in text if c in emoji.EMOJI_DATA]

    emoji_count = len(emojis_list)
    unique_emoji_count = len(set(emojis_list))
    emoji_density = emoji_count / max(1, len(text))

    # Longest repeated emoji sequence
    longest_run = 1
    run = 1
    for i in range(1, len(emojis_list)):
        if emojis_list[i] == emojis_list[i - 1]:
            run += 1
        else:
            longest_run = max(longest_run, run)
            run = 1
    longest_run = max(longest_run, run)

    # Emoji only
    is_emoji_only = int(bool(re.fullmatch(r"[\p{Emoji}\p{Emoji_Presentation}\s]+", text)))

    return emoji_count, unique_emoji_count, emoji_density, longest_run, is_emoji_only


# --------------------------------------
# Main bot detection logic (RULE-BASED)
# --------------------------------------
def rule_based_detection(tweet, description, hashtags,
                         retweet_count, mention_count,
                         follower_count, following_count,
                         verified, account_age_days):

    # Combine text
    combined_text = f"{tweet} {description} {hashtags}".lower()

    # Extract emoji features
    emoji_count, unique_emoji_count, emoji_density, longest_run, is_emoji_only = \
        extract_emoji_behavior(combined_text)

    # --------------------------------------
    # RULE 1 — extremely young accounts = BOT
    # --------------------------------------
    if account_age_days < 3:
        return 1, "BOT (Account too new)"

    # --------------------------------------
    # RULE 2 — low follower, extremely high following = BOT
    # --------------------------------------
    if follower_count < 30 and following_count > 500:
        return 1, "BOT (Suspicious follow ratio)"

    # --------------------------------------
    # RULE 3 — engagement spam (many retweets but no followers)
    # --------------------------------------
    if retweet_count > 50 and follower_count < 20:
        return 1, "BOT (High spam retweets)"

    # --------------------------------------
    # RULE 4 — emoji spam pattern looks like bot
    # --------------------------------------
    if emoji_density > 0.25 and longest_run >= 3:
        return 1, "BOT (Excessive emoji pattern)"

    # --------------------------------------
    # RULE 5 — suspicious promotional keywords
    # --------------------------------------
    promo_words = ["free", "win", "offer", "discount", "deal", "click", "buy now"]
    if any(w in combined_text for w in promo_words):
        if follower_count < 100:
            return 1, "BOT (Promotion keyword with low trust)"

    # --------------------------------------
    # RULE 6 — verified users almost never bots
    # --------------------------------------
    if verified == 1 and follower_count > 1000:
        return 0, "HUMAN (Verified trusted)"

    # --------------------------------------
    # RULE 7 — regular humans
    # --------------------------------------
    return 0, "HUMAN (No bot patterns detected)"


# --------------------------------------
# Flask routes
# --------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":

        # SAFE extraction
        def safe(x, default=0):
            try:
                return float(x)
            except:
                return default

        tweet = request.form.get("tweet", "")
        description = request.form.get("description", "")
        hashtags = request.form.get("hashtags", "")

        retweet_count = safe(request.form.get("retweet_count"))
        mention_count = safe(request.form.get("mention_count"))
        follower_count = safe(request.form.get("follower_count"))
        following_count = safe(request.form.get("following_count"))
        account_age_days = safe(request.form.get("account_age_days"), 365)

        verified = 1 if request.form.get("verified") == "1" else 0

        label, reason = rule_based_detection(
            tweet, description, hashtags,
            retweet_count, mention_count,
            follower_count, following_count,
            verified, account_age_days
        )

        result = {
            "tweet": tweet,
            "description": description,
            "hashtags": hashtags,
            "retweet_count": retweet_count,
            "mention_count": mention_count,
            "follower_count": follower_count,
            "following_count": following_count,
            "verified": verified,
            "account_age_days": account_age_days,
            "pred_label": label,
            "pred_text": "BOT" if label == 1 else "HUMAN",
            "reason": reason
        }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    print("🚀 Running Rule-Based Bot Detector at http://127.0.0.1:5000")
    app.run(debug=True)
