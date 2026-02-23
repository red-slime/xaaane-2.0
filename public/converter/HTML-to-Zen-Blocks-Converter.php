<?php
/**
 * Plugin Name: HTML to Zen Blocks Importer
 * Description: Import HTML sections and automatically create pages with Zen Blocks
 * Version: 1.0.0
 * Author: XAAANE
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class HTMLToZenBlocksImporter {
    
    public function __construct() {
        // Hook into WordPress admin menu system
        add_action('admin_menu', array($this, 'add_admin_menu'));
        // Handle form submission for import
        add_action('admin_post_html_zen_import', array($this, 'handle_import'));
        // Load media uploader scripts on our admin page
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_scripts'));
    }
    
    public function add_admin_menu() {
        // Add submenu under Tools in WordPress admin
        add_submenu_page(
            'tools.php',                      // Parent: Tools menu
            'HTML to Zen Blocks Importer',    // Page title
            'HTML Importer',                  // Menu title
            'manage_options',                 // Required capability
            'html-zen-importer',              // Menu slug
            array($this, 'admin_page')        // Callback function
        );
    }
    
    public function enqueue_admin_scripts($hook) {
        // Only load scripts on our specific admin page
        if ($hook !== 'tools_page_html-zen-importer') {
            return;
        }
        
        // Load WordPress media uploader (for future image handling)
        wp_enqueue_media();
        wp_enqueue_script('jquery');
    }
    
    public function admin_page() {
        ?>
        <div class="wrap">
            <h1>HTML to Zen Blocks Importer</h1>
            
            <?php if (isset($_GET['import_result'])): ?>
                <?php if ($_GET['import_result'] === 'success'): ?>
                    <div class="notice notice-success"><p>Import completed successfully!</p></div>
                <?php else: ?>
                    <div class="notice notice-error"><p>Import failed. Check error log for details.</p></div>
                <?php endif; ?>
            <?php endif; ?>
            
            <form method="post" action="<?php echo admin_url('admin-post.php'); ?>" enctype="multipart/form-data">
                <?php wp_nonce_field('html_zen_import', 'html_zen_nonce'); ?>
                <input type="hidden" name="action" value="html_zen_import">
                
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label for="page_slug">Page Slug</label>
                        </th>
                        <td>
                            <input type="text" id="page_slug" name="page_slug" class="regular-text" 
                                   placeholder="solutions" required>
                            <p class="description">Enter the page slug (without leading slash). Example: "solutions"</p>
                        </td>
                    </tr>
                    
                    <tr>
                        <th scope="row">
                            <label for="page_title">Page Title</label>
                        </th>
                        <td>
                            <input type="text" id="page_title" name="page_title" class="regular-text" 
                                   placeholder="Solutions" required>
                            <p class="description">The title for the new page</p>
                        </td>
                    </tr>
                    
                    <tr>
                        <th scope="row">
                            <label for="html_file">HTML File</label>
                        </th>
                        <td>
                            <input type="file" id="html_file" name="html_file" accept=".html,.htm" required>
                            <p class="description">Upload an HTML file containing sections to import</p>
                        </td>
                    </tr>
                    
                    <tr>
                        <th scope="row">
                            <label for="page_status">Page Status</label>
                        </th>
                        <td>
                            <select id="page_status" name="page_status">
                                <option value="draft">Draft</option>
                                <option value="publish">Published</option>
                            </select>
                            <p class="description">Choose whether to publish the page immediately or save as draft</p>
                        </td>
                    </tr>
                </table>
                
                <h3>Block Mapping Settings</h3>
                <table class="form-table">
                    <tr>
                        <th scope="row">Available Zen Blocks</th>
                        <td>
                            <div id="available-blocks">
                                <?php $this->display_available_blocks(); ?>
                            </div>
                        </td>
                    </tr>
                </table>
                
                <?php submit_button('Import HTML and Create Page', 'primary', 'submit'); ?>
            </form>
            
            <hr>
            
            <h3>Instructions</h3>
            <ol>
                <li>Enter a unique page slug (the URL path for your page)</li>
                <li>Upload an HTML file containing the sections you want to import</li>
                <li>The plugin will automatically detect HTML sections and match them to available Zen Blocks</li>
                <li>A new page will be created with the imported content as Zen Blocks</li>
            </ol>
            
            <h3>Supported Block Types</h3>
            <ul>
                <li><strong>Product Benefits Section:</strong> Detects 3-column benefit grids with icons, titles, and descriptions</li>
                <li><strong>Custom Card:</strong> Detects card-like sections with images, titles, and content</li>
                <li><strong>Demo Components:</strong> Detects various component demonstrations</li>
            </ul>
        </div>
        
        <style>
        .block-info {
            background: #f1f1f1;
            padding: 10px;
            margin: 5px 0;
            border-left: 4px solid #0073aa;
        }
        .block-info h4 {
            margin: 0 0 5px 0;
        }
        </style>
        <?php
    }
    
    private function display_available_blocks() {
        // Get available Zen Blocks
        $available_blocks = $this->get_available_zen_blocks();
        
        if (empty($available_blocks)) {
            echo '<p>No Zen Blocks found. Make sure the Zen Blocks plugin is active and you have created some blocks.</p>';
            return;
        }
        
        foreach ($available_blocks as $block_name => $block_info) {
            echo '<div class="block-info">';
            echo '<h4>' . esc_html($block_info['title']) . '</h4>';
            echo '<p><strong>Block:</strong> ' . esc_html($block_name) . '</p>';
            echo '<p>' . esc_html($block_info['description']) . '</p>';
            echo '</div>';
        }
    }
    
    private function get_available_zen_blocks() {
        $blocks = array();
        
        // Safety check: Ensure Zen Blocks plugin is active
        if (!function_exists('zenb_get_blocks')) {
            return $blocks;
        }
        
        // Query WordPress block registry for all registered blocks
        $registry = WP_Block_Type_Registry::get_instance();
        $all_blocks = $registry->get_all_registered();
        
        // Filter to only Zen Blocks (namespace: "zen-blocks/")
        foreach ($all_blocks as $block_name => $block_type) {
            if (strpos($block_name, 'zen-blocks/') === 0) {
                $blocks[$block_name] = array(
                    'title' => isset($block_type->title) ? $block_type->title : $block_name,
                    'description' => isset($block_type->description) ? $block_type->description : 'No description available'
                );
            }
        }
        
        return $blocks;
    }
    
    public function handle_import() {
        // Security: Verify nonce token to prevent CSRF attacks
        if (!wp_verify_nonce($_POST['html_zen_nonce'], 'html_zen_import')) {
            wp_die('Security check failed');
        }
        
        // Security: Check user has admin permissions
        if (!current_user_can('manage_options')) {
            wp_die('Insufficient permissions');
        }
        
        // Sanitize form inputs to prevent XSS
        $page_slug = sanitize_title($_POST['page_slug']);
        $page_title = sanitize_text_field($_POST['page_title']);
        $page_status = sanitize_text_field($_POST['page_status']);
        
        // Validate file upload
        if (!isset($_FILES['html_file']) || $_FILES['html_file']['error'] !== UPLOAD_ERR_OK) {
            $this->redirect_with_error('File upload failed');
            return;
        }
        
        // Read uploaded HTML file from temp location
        $uploaded_file = $_FILES['html_file'];
        $html_content = file_get_contents($uploaded_file['tmp_name']);
        
        if ($html_content === false) {
            $this->redirect_with_error('Could not read HTML file');
            return;
        }
        
        try {
            // Main import logic: parse HTML and create WordPress page
            $result = $this->process_import($page_slug, $page_title, $page_status, $html_content);
            
            if ($result['success']) {
                $this->redirect_with_success($result['page_id']);
            } else {
                $this->redirect_with_error($result['error']);
            }
        } catch (Exception $e) {
            error_log('HTML Import Error: ' . $e->getMessage());
            $this->redirect_with_error('Import failed: ' . $e->getMessage());
        }
    }
    
    private function process_import($page_slug, $page_title, $page_status, $html_content) {
        // Prevent duplicate pages - check if slug already exists
        $existing_page = get_page_by_path($page_slug);
        if ($existing_page) {
            return array('success' => false, 'error' => 'Page with this slug already exists');
        }
        
        // Step 1: Parse HTML and detect sections using DOMDocument
        $sections = $this->parse_html_sections($html_content);
        
        if (empty($sections)) {
            return array('success' => false, 'error' => 'No recognizable sections found in HTML');
        }
        
        // Step 2: Convert sections array into Gutenberg block markup
        $block_content = $this->create_block_content($sections);
        
        // Step 3: Create WordPress page with block content
        $page_data = array(
            'post_title'   => $page_title,
            'post_name'    => $page_slug,
            'post_content' => $block_content,  // Gutenberg blocks as HTML comments
            'post_status'  => $page_status,    // 'draft' or 'publish'
            'post_type'    => 'page',
            'post_author'  => get_current_user_id()
        );
        
        $page_id = wp_insert_post($page_data);
        
        if (is_wp_error($page_id)) {
            return array('success' => false, 'error' => $page_id->get_error_message());
        }
        
        return array(
            'success' => true, 
            'page_id' => $page_id,
            'sections_found' => count($sections)
        );
    }
    
    private function parse_html_sections($html_content) {
        // Initialize DOMDocument for HTML parsing
        $dom = new DOMDocument();
        libxml_use_internal_errors(true);  // Suppress HTML parsing warnings
        $dom->loadHTML($html_content, LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD);
        libxml_clear_errors();
        
        // Use XPath for CSS class-based section detection
        $xpath = new DOMXPath($dom);
        $sections = array();
        
        // Detect Product Benefits Section (3-column grid with icons)
        // XPath: Find <section> tags with class containing "product-benefit-section"
        $benefit_sections = $xpath->query("//section[contains(@class, 'product-benefit-section')]");
        foreach ($benefit_sections as $section) {
            $sections[] = $this->parse_product_benefits_section($section, $xpath);
        }
        
        // Detect Custom Card Sections (card-like layouts)
        // XPath: Find <div> tags with class containing "custom-card"
        $card_sections = $xpath->query("//div[contains(@class, 'custom-card')]");
        foreach ($card_sections as $section) {
            $sections[] = $this->parse_custom_card_section($section, $xpath);
        }
        
        // TO EXTEND: Add more section detectors here
        // Pattern: $xpath->query("//element[contains(@class, 'your-class')]")
        
        return array_filter($sections); // Remove any null/empty sections
    }
    
    private function parse_product_benefits_section($section, $xpath) {
        // Build data structure for Zen Block attributes
        $data = array(
            'type' => 'zen-blocks/product-benefits-section',  // Target block name in WordPress
            'attributes' => array()
        );
        
        // Extract titles from <h3> elements (up to 3 columns)
        $titles = $xpath->query(".//h3[contains(@class, 'product-benefit-grid-header')]", $section);
        for ($i = 0; $i < min($titles->length, 3); $i++) {
            $title_text = $this->clean_text_content($titles->item($i)->textContent);
            $data['attributes']['benefit_' . ($i + 1) . '_title'] = $title_text;
        }
        
        // Extract descriptions from <p> elements (up to 3 columns)
        $descriptions = $xpath->query(".//p[contains(@class, 'product-benefit-grid-para')]", $section);
        for ($i = 0; $i < min($descriptions->length, 3); $i++) {
            $desc_text = $this->clean_text_content($descriptions->item($i)->textContent);
            $data['attributes']['benefit_' . ($i + 1) . '_description'] = $desc_text;
        }
        
        // Extract icon image URLs (up to 3 columns)
        $icons = $xpath->query(".//img[contains(@class, 'product-benefit-grid-img')]", $section);
        for ($i = 0; $i < min($icons->length, 3); $i++) {
            $icon_src = $icons->item($i)->getAttribute('src');
            if ($icon_src) {
                $data['attributes']['benefit_' . ($i + 1) . '_icon'] = $icon_src;
            }
        }
        
        return $data;
    }
    
    private function parse_custom_card_section($section, $xpath) {
        $data = array(
            'type' => 'zen-blocks/custom-card',
            'attributes' => array()
        );
        
        // Extract title
        $title = $xpath->query(".//h2 | .//h3", $section)->item(0);
        if ($title) {
            $data['attributes']['title'] = $this->clean_text_content($title->textContent);
        }
        
        // Extract content
        $content = $xpath->query(".//p", $section)->item(0);
        if ($content) {
            $data['attributes']['content'] = $this->clean_text_content($content->textContent);
        }
        
        // Extract image
        $image = $xpath->query(".//img", $section)->item(0);
        if ($image) {
            $data['attributes']['image'] = $image->getAttribute('src');
        }
        
        return $data;
    }
    
    /**
     * Clean text content by removing unwanted characters and normalizing whitespace
     * This fixes encoding issues from static HTML exports (curly quotes, em dashes, etc.)
     */
    private function clean_text_content($text) {
        // Step 1: Strip any remaining HTML tags
        $text = strip_tags($text);
        
        // Step 2: Normalize line breaks to single spaces
        $text = str_replace(array("\r\n", "\r", "\n"), ' ', $text);
        
        // Step 3: Remove invisible control characters (zero-width spaces, etc.)
        $text = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', '', $text);
        
        // Step 4: Collapse multiple spaces into single space
        $text = preg_replace('/\s+/', ' ', $text);
        
        // Step 5: Trim leading/trailing whitespace
        $text = trim($text);
        
        // Step 6: Fix common UTF-8 encoding issues (WordPress curly quotes, etc.)
        // These appear when HTML was saved with wrong encoding
        $text = str_replace(array('â€™', 'â€œ', 'â€?', 'â€"', 'â€"'), array("'", '"', '"', '–', '—'), $text);
        
        return $text;
    }
    
    private function create_block_content($sections) {
        $block_content = '';
        
        // Convert each section into Gutenberg block comment syntax
        foreach ($sections as $section) {
            // JSON-encode attributes if they exist (block data like titles, images, etc.)
            $attributes = !empty($section['attributes']) ? ' ' . json_encode($section['attributes']) : '';
            
            // Create opening block comment: <!-- wp:block-name {"attribute":"value"} -->
            $block_content .= '<!-- wp:' . $section['type'] . $attributes . ' -->' . "\n";
            
            // Create closing block comment: <!-- /wp:block-name -->
            $block_content .= '<!-- /wp:' . $section['type'] . ' -->' . "\n\n";
        }
        
        // WordPress parses these comments to render the actual blocks
        return $block_content;
    }
    
    private function redirect_with_success($page_id) {
        $redirect_url = add_query_arg(array(
            'page' => 'html-zen-importer',
            'import_result' => 'success',
            'page_id' => $page_id
        ), admin_url('tools.php'));
        
        wp_redirect($redirect_url);
        exit;
    }
    
    private function redirect_with_error($error_message) {
        error_log('HTML Import Error: ' . $error_message);
        
        $redirect_url = add_query_arg(array(
            'page' => 'html-zen-importer',
            'import_result' => 'error'
        ), admin_url('tools.php'));
        
        wp_redirect($redirect_url);
        exit;
    }
}

// Initialize the plugin
new HTMLToZenBlocksImporter();
?>