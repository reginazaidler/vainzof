# סריקת SEO – vainzof.co.il

תאריך סריקה: 2026-03-15  
היקף: בדיקת SEO טכנית על קבצי HTML סטטיים בריפו (`*.html`) + בדיקת `robots.txt` ו-`sitemap.xml`.

## מתודולוגיה

הסריקה בוצעה באמצעות פקודות טרמינל וסקריפט Python מקומי שבדק לכל עמוד:
- תגית `title`
- `meta description`
- `canonical`
- תגיות Open Graph בסיסיות
- קיום `h1`
- קיום Schema (`application/ld+json`)
- תמונות ללא `alt`

## סיכום תוצאות

- נסרקו **23 עמודי HTML**.
- `title`: תקין בכל העמודים (0 חסרים).
- `meta description`: חסר בעמוד אחד.
- `canonical`: חסר בעמוד אחד.
- `h1`: קיים בדיוק פעם אחת בכל עמוד (ללא חריגות).
- `og:image`: חסר ב-4 עמודים.
- Schema (`ld+json`): חסר בעמוד אחד.
- תמונות ללא `alt`: לא נמצאו.
- `sitemap.xml`: כולל 22 כתובות URL.
- `robots.txt`: מוגדר נכון עם הפניה ל-sitemap.

## ממצאים לפי עמוד

### חסר `og:image`
1. `family-emergency-fund.html`
2. `freelancers-pension-mistakes.html`
3. `insurance-checklist-after-birth.html`
4. `thanks.html`

### חסרים מטא-דאטה בסיסיים
- `thanks.html`:
  - חסר `meta description`
  - חסר `canonical`
  - חסר Open Graph מלא
  - חסר Schema
  - כולל `meta name="robots" content="noindex"` (כנראה מכוון, ולכן בעדיפות נמוכה)

## פרשנות עסקית קצרה

- מצב SEO טכני כללי: **טוב מאוד**.
- רוב הליקויים מרוכזים בעמוד `thanks.html`, שמוגדר `noindex`, ולכן ההשפעה שלו על אורגני נמוכה.
- שלושת עמודי התוכן שחסרה בהם `og:image` כן יכולים להיפגע בעיקר בשיתופים חברתיים (CTR נמוך יותר בוואטסאפ/פייסבוק/לינקדאין).

## פעולות מומלצות (עדיפות)

1. **גבוהה** – להוסיף `og:image` ל-3 עמודי תוכן:
   - `family-emergency-fund.html`
   - `freelancers-pension-mistakes.html`
   - `insurance-checklist-after-birth.html`
2. **בינונית** – להחליט אם `thanks.html` צריך להישאר `noindex` (ברוב המקרים כן).
3. **נמוכה** – אם רוצים אחידות מלאה, ניתן להוסיף מטא-דאטה גם ל-`thanks.html`, למרות שאין לכך ערך SEO משמעותי כשיש `noindex`.

## הערות

- לא בוצעה כאן בדיקת ביצועים/Core Web Vitals (Lighthouse/PageSpeed) בזמן ריצה בדפדפן.
- לא בוצעה בדיקת אינדוקס בפועל מול Google Search Console.
