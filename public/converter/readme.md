# 🛠️ HTML to WordPress Migration Toolkit

This is your survival kit for migrating a static HTML site into WordPress with custom Zen Blocks. The workflow: **analyze → understand → import**.

---

## What's in Here

### 🐍 Python Scripts (The Scouts)

These are recon tools. Run them **first** to understand what you're dealing with before touching WordPress.

#### `html_section_cataloger_deluxe.py`

**What it does:** Crawls your HTML files and catalogs every unique `<section>` (and section-like divs) by their CSS classes. Builds a map of what sections exist, where they live, and what's inside them.

**Why you need it:** Before you can convert HTML → WordPress blocks, you need to know what sections exist and how consistent they are across pages. This script tells you "hey, you've got 12 pages using the 'product-benefit-section' class with different content" or "this custom-card only shows up once on the about page."

**Run it from the root of your SITE folder:**

```bash
python html_section_cataloger_deluxe.py . --text sections_report.md --similar
```

**Flags:**

- `--text` / `-t` → Save output to markdown (cleaner than console)
- `--output` / `-o` → Save to JSON for programmatic use
- `--details` / `-d` → Show every single occurrence with full attributes
- `--similar` / `-s` → Find sections with same classes but different content (useful for spotting variations)

**Output:**

- Groups sections by CSS classes
- Shows which files use each section
- Lists unique child elements
- Highlights sections that appear in multiple files but have different structures (good for catching edge cases)

**Nuance:** It ignores footer sections automatically. If you need to exclude more (like navbars), edit line 166 where it checks `if 'footer' in classes`.

---

#### `html_script_cataloger_deluxe.py` _(not shown but mentioned in old readme)_

**What it does:** Same idea but for `<script>` tags. Catalogs external/internal scripts, their attributes, locations, etc.

**Why you need it:** Before importing pages, you need to know what scripts are running where. Some scripts might break in WordPress, some might need to be enqueued properly, some might be inline junk that can be removed.

**Run it the same way:**

```bash
python html_script_cataloger_deluxe.py . --text scripts_report.md
```

This generates `scripts_report.md` showing every script across the site.

---

### 🔌 WordPress Plugin (The Builder)

#### `HTML-to-Zen-Blocks-Converter.php`

**What it does:** WordPress plugin that imports HTML files and converts sections into **Zen Blocks** (custom Gutenberg blocks). Drop in HTML, get WordPress pages with blocks.

**How to use:**

1. Install it like any plugin (upload to `wp-content/plugins/`)
2. Activate it
3. Go to **Tools → HTML Importer**
4. Upload an HTML file, give it a page slug & title
5. Plugin parses the HTML, detects sections, maps them to Zen Blocks, creates the page

**Supported block types:**

- **Product Benefits Section** → 3-column grid with icons, titles, descriptions
- **Custom Card** → Card-like sections with images, titles, content
- **Demo Components** → Generic component blocks

**Nuance:** The plugin uses **class-based detection**. It looks for:

- `.product-benefit-section` → Maps to `zen-blocks/product-benefits-section`
- `.custom-card` → Maps to `zen-blocks/custom-card`

If your HTML uses different class names, you'll need to edit the `parse_html_sections()` method (lines 258-280) to add new detectors.

**Gotchas:**

- It assumes Zen Blocks plugin is active and you've already created the blocks
- The `clean_text_content()` method (lines 392-411) strips weird encoding issues and zero-width spaces — if text looks funky in WordPress, check there
- Creates pages as **drafts** by default (you can change to "publish")

---

## The Workflow

1. **Run the catalogers** (Python scripts) to generate reports
2. **Read the reports** to understand your site structure
3. **Create Zen Blocks in WordPress** that match your HTML sections
4. **Use the plugin** to import HTML files one by one
5. **Review drafts** in WordPress and publish when ready

---

## What You'll Learn from the Catalogers

### From `sections_report.md`:

- How many unique section types exist
- Which sections are reused across multiple pages (good candidates for blocks)
- Which sections are one-offs (maybe just hardcode those)
- Variations of the same section (same classes, different content structure)

### From `scripts_report.md`:

- What external libraries are loaded (jQuery, analytics, etc.)
- What inline scripts exist (might need to move to theme functions)
- What scripts are page-specific vs global

---

## Important Things

### 1. **Class Names Matter**

The plugin uses CSS classes to detect section types. If your HTML has inconsistent class names, the plugin won't recognize sections. Check the cataloger output first.

### 2. **Content vs Structure**

The cataloger groups sections by **classes** and creates a **content hash** for structure. Two sections with the same classes but different HTML children will be flagged as "similar but different" — that's your cue to decide if they're variations or separate blocks.

### 3. **Footer/Header Exclusion**

The section cataloger skips anything with `class="footer"`. If you want to skip headers too, edit line 166:

```python
if 'footer' in classes or 'header' in classes:
    continue
```

### 4. **Text Encoding Issues**

The plugin has a `clean_text_content()` method that handles common encoding problems (curly quotes, em dashes, zero-width spaces). If imported text looks weird, check that method.

### 5. **Block Mapping is Manual**

You still need to create the Zen Blocks in WordPress first. The plugin just maps HTML sections to existing blocks — it doesn't create the blocks for you.

---

## Nuances

- The cataloger uses **BeautifulSoup** (Python HTML parser) — it's forgiving of messy HTML
- The plugin uses **DOMDocument** (PHP's XML parser) — it's stricter, so malformed HTML might break
- The plugin generates **Gutenberg block comments** (`<!-- wp:block-name -->`) — that's how WordPress knows what block to render
- If a section doesn't match any known block type, it's skipped (check WordPress error log)
- The cataloger can output to **JSON** if you want to build automated tooling on top of it

---

## Extending It

### Add a new section type to the plugin:

1. Edit `parse_html_sections()` (line 258)
2. Add a new XPath query to detect your section
3. Create a parser method like `parse_your_section_name()`
4. Map it to a Zen Block name

### Add a new filter to the cataloger:

1. Edit `parse_html_file()` around line 166
2. Add conditions to skip/include sections based on class names, attributes, etc.

---

## TL;DR

- **Python scripts** = reconnaissance (figure out what you have)
- **PHP plugin** = execution (import HTML into WordPress)
- Run the scripts, read the reports, then use the plugin
- Class names are your anchor — keep them consistent
- Check the cataloger output for section variations before importing
- Everything defaults to drafts, so you can review before publishing
