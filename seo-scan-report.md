# סריקת SEO – vainzof.co.il

תאריך סריקה: 2026-04-07  
היקף: בדיקת SEO טכנית על קבצי HTML סטטיים בריפו (`*.html`) + בדיקת `robots.txt` ו-`sitemap.xml`.

## מתודולוגיה

הסריקה בוצעה באמצעות סקריפט Python מקומי (`scripts/seo_audit.py`) שבודק לכל עמוד:
- תגית `title`
- `meta description`
- `canonical`
- `og:image`
- קיום `h1` יחיד
- קיום Schema (`application/ld+json`)

## סיכום תוצאות

- נסרקו **74 עמודי HTML**.
- `title`: תקין ב-74 עמודים.
- `meta description`: תקין ב-74 עמודים.
- `canonical`: תקין ב-74 עמודים.
- `og:image`: תקין ב-69 עמודים.
- Schema (`ld+json`): תקין ב-68 עמודים.
- `h1`: תקין ב-74 עמודים.
- `sitemap.xml`: כולל 72 כתובות URL.
- `robots.txt`: קיים בריפו.

## ממצאים

### עמודים ללא `meta description`
אין ממצאים.

### עמודים ללא `canonical`
אין ממצאים.

### עמודים ללא `og:image`
1. `how-to-choose-insurance-agent/index.html`
2. `life-insurance-with-kids/index.html`
3. `long-term-care-insurance-israel/index.html`
4. `switch-insurance-company/index.html`
5. `when-to-update-insurance/index.html`

### עמודים ללא Schema (`ld+json`)
1. `essential-family-insurance/index.html`
2. `how-to-choose-insurance-agent/index.html`
3. `life-insurance-with-kids/index.html`
4. `long-term-care-insurance-israel/index.html`
5. `switch-insurance-company/index.html`
6. `when-to-update-insurance/index.html`

### עמודים עם חריגה בכמות `h1`
אין ממצאים.

## הערות

- זוהי בדיקת SEO טכנית בסיסית בלבד, ללא בדיקת ביצועים/Core Web Vitals.
- כברירת מחדל הסקריפט לא מתקן אוטומטית קבצים; הוא רק מדווח כדי למנוע שינויים לא בטוחים בתוכן.
- כדי לנתח אינדוקס בפועל והופעה בתוצאות חיפוש, יש להשלים בדיקה ב-Google Search Console.
