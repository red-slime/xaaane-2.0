#!/usr/bin/env python3
"""
HTML Section Cataloger
Recursively searches .html files and catalogs unique <section> elements by their classes and IDs,
including analysis of unique elements within each section.
"""

import os
import json
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
import argparse
import hashlib

def get_element_signature(element):
    """Create a signature for an element based on its tag and classes only."""
    tag = element.name
    classes = element.get('class', [])
    
    # Only include non-content structural attributes (excluding src and id)
    key_attrs = {}
    for attr in ['type', 'role', 'loading']:
        if element.get(attr):
            key_attrs[attr] = element.get(attr)
    
    signature = {
        'tag': tag,
        'classes': classes if isinstance(classes, list) else [classes],
        'key_attributes': key_attrs
    }
    
    return signature

def analyze_section_content(section):
    """Analyze the content structure of a section."""
    # Get all child elements (not just direct children)
    all_elements = section.find_all()
    
    element_signatures = []
    element_counts = Counter()
    unique_children = set()
    
    for element in all_elements:
        signature = get_element_signature(element)
        element_signatures.append(signature)
        
        # Create a simple key for counting (classes only)
        classes_str = ' '.join(sorted(signature['classes']))
        attrs_str = ' '.join([f"{k}:{v}" for k, v in sorted(signature['key_attributes'].items())])
        element_key = f"{signature['tag']}.{classes_str}|{attrs_str}"
        element_counts[element_key] += 1
        
        # Create unique children display format (classes only)
        if signature['classes']:
            class_attr = f' class="{" ".join(signature["classes"])}"'
        else:
            class_attr = ''
        
        # Add key attributes to display
        key_attrs = ''
        for attr, value in signature['key_attributes'].items():
            key_attrs += f' {attr}="{value}"'
        
        unique_child = f"<{signature['tag']}{class_attr}{key_attrs}>"
        unique_children.add(unique_child)
    
    return {
        'element_signatures': element_signatures,
        'element_counts': dict(element_counts),
        'unique_children': sorted(list(unique_children)),
        'total_elements': len(all_elements),
        'unique_elements': len(element_counts)
    }

def create_content_hash(content_analysis):
    """Create a hash of the section's content structure for comparison."""
    # Create a string representation of the element structure
    element_keys = []
    for sig in content_analysis['element_signatures']:
        classes_str = ' '.join(sorted(sig['classes']))
        attrs_str = ' '.join([f"{k}:{v}" for k, v in sorted(sig['key_attributes'].items())])
        key = f"{sig['tag']}.{classes_str}|{attrs_str}"
        element_keys.append(key)
    
    content_string = '|'.join(element_keys)
    return hashlib.md5(content_string.encode()).hexdigest()[:8]

def parse_html_file(file_path):
    """Parse an HTML file and extract section elements and section-like divs with their attributes and content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all sections
        sections = soup.find_all('section')
        
        # Find div elements that are siblings of sections and have "section" in their class names
        section_like_divs = []
        for div in soup.find_all('div'):
            classes = div.get('class', [])
            # Check if any class contains "section"
            if any('section' in cls.lower() for cls in classes):
                # Check if it's a sibling of sections (same parent level)
                parent = div.parent
                if parent and parent.find_all('section'):
                    section_like_divs.append(div)
        
        # Combine sections and section-like divs
        all_sections = sections + section_like_divs
        
        section_data = []
        for section in all_sections:
            # Extract classes
            classes = section.get('class', [])
            
            # Skip sections with 'footer' class
            if 'footer' in classes:
                continue
            
            # Analyze the content structure
            content_analysis = analyze_section_content(section)
            content_hash = create_content_hash(content_analysis)
            
            # Create a unique identifier for this section (classes only, no ID)
            section_info = {
                'classes': classes if isinstance(classes, list) else [classes],
                'file': str(file_path),
                'attributes': dict(section.attrs),
                'content_analysis': content_analysis,
                'content_hash': content_hash,
                'tag': section.name  # Track whether it's a section or div
            }
            section_data.append(section_info)
        
        return section_data
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def create_unique_key(section_info):
    """Create a unique key for a section based on its classes and content structure (no ID)."""
    classes_str = ' '.join(sorted(section_info['classes']))
    content_hash = section_info['content_hash']
    return f"classes:{classes_str}|content:{content_hash}"

def catalog_sections(root_directory):
    """Recursively search for HTML files and catalog sections."""
    root_path = Path(root_directory)
    
    if not root_path.exists():
        print(f"Error: Directory '{root_directory}' does not exist.")
        return {}
    
    # Dictionary to store sections grouped by classes only
    sections_by_structure = defaultdict(list)
    file_count = 0
    total_sections = 0
    
    # Recursively find all HTML files
    for html_file in root_path.rglob('*.html'):
        file_count += 1
        print(f"Processing: {html_file}")
        
        sections = parse_html_file(html_file)
        total_sections += len(sections)
        
        for section in sections:
            # Skip sections with 'footer' class
            if 'footer' in section['classes']:
                continue
            # Group by classes only (no ID)
            classes_str = ' '.join(sorted(section['classes']))
            structure_key = f"classes:{classes_str}"
            
            sections_by_structure[structure_key].append(section)
    
    # Now process each group to find unique children across all instances
    unique_sections = {}
    
    for structure_key, sections_list in sections_by_structure.items():
        # Track which files contain each unique child
        children_to_files = defaultdict(set)
        all_files = []
        first_section = sections_list[0]
        
        for section in sections_list:
            file_name = Path(section['file']).name
            
            # Map each unique child to the files that contain it
            for child in section['content_analysis']['unique_children']:
                children_to_files[child].add(file_name)
            
            all_files.append({
                'file': section['file'],
                'all_attributes': section['attributes']
            })
        
        # Create the final entry with file mapping
        unique_sections[structure_key] = {
            'classes': first_section['classes'],
            'tag': first_section['tag'],  # Include tag info
            'unique_children': sorted(list(children_to_files.keys())),
            'children_to_files': {child: sorted(list(files)) for child, files in children_to_files.items()},
            'first_seen_in': first_section['file'],
            'occurrences': all_files
        }
    
    print(f"\nProcessed {file_count} HTML files")
    print(f"Found {total_sections} total sections")
    print(f"Found {len(unique_sections)} unique section structures")
    
    return unique_sections

def display_results(unique_sections, show_details=False, show_content=False, output_file=None):
    """Display the cataloged sections in a readable format."""
    output_lines = []
    is_markdown = output_file and output_file.endswith('.md')
    
    if is_markdown:
        output_lines.append("# 🏗️ Section Catalog")
        output_lines.append("")
        output_lines.append(f"**Total unique sections:** {len(unique_sections)}")
        output_lines.append("")
    else:
        output_lines.append("="*60)
        output_lines.append("UNIQUE SECTION CATALOG")
        output_lines.append("="*60)
    
    for i, (key, section_data) in enumerate(unique_sections.items(), 1):
        classes_display = ', '.join(section_data['classes']) if section_data['classes'] else 'None'
        
        # Get the file name from the first occurrence
        first_file = section_data['first_seen_in']
        file_name = Path(first_file).name
        
        if is_markdown:
            output_lines.append(f"## {i}. Section Signature")
            output_lines.append("")
            output_lines.append(f"**Classes:** `{classes_display}`")
            output_lines.append(f"**Tag:** `{section_data['tag']}`")
            output_lines.append(f"**Found in:** {len(section_data['occurrences'])} file(s)")
            output_lines.append("")
        else:
            output_lines.append(f"\n{i}. Section Signature:")
            output_lines.append(f"   Classes: {classes_display}")
            output_lines.append(f"   Tag: {section_data['tag']}")
            output_lines.append(f"   Found in {len(section_data['occurrences'])} file(s)")
        
        # Show all files if found in more than 1 file
        if len(section_data['occurrences']) > 1:
            all_files = [Path(occ['file']).name for occ in section_data['occurrences']]
            if is_markdown:
                if len(all_files) <= 5:
                    files_display = ', '.join(f'`{f}`' for f in all_files)
                    output_lines.append(f"**Files:** {files_display}")
                else:
                    files_display = ', '.join(f'`{f}`' for f in all_files[:3])
                    output_lines.append(f"**Files:** {files_display}... and {len(all_files) - 3} more")
                    output_lines.append("")
                    output_lines.append("<details>")
                    output_lines.append("<summary>View all files</summary>")
                    output_lines.append("")
                    for file in all_files:
                        output_lines.append(f"- `{file}`")
                    output_lines.append("")
                    output_lines.append("</details>")
                output_lines.append("")
            else:
                files_display = ', '.join(f'"{f}"' for f in all_files)
                output_lines.append(f"   Files: {files_display}")
        else:
            if is_markdown:
                output_lines.append(f"**File:** `{file_name}`")
                output_lines.append("")
            else:
                output_lines.append(f"   File: \"{file_name}\"")
        
        # Only show unique children if they appear in different files
        if section_data['unique_children'] and len(section_data['occurrences']) > 1:
            # Filter to only show children that don't appear in all files
            all_files_set = set(Path(occ['file']).name for occ in section_data['occurrences'])
            different_children = []
            
            for child in section_data['unique_children']:
                files_with_child = set(section_data['children_to_files'][child])
                # Only include if this child doesn't appear in all files
                if files_with_child != all_files_set:
                    different_children.append(child)
            
            if different_children:
                if is_markdown:
                    output_lines.append("### Unique Children (varying across files)")
                    output_lines.append("")
                else:
                    output_lines.append(f"   Unique Children (varying across files):")
                    
                for child in different_children:
                    files_with_child = section_data['children_to_files'][child]
                    if is_markdown:
                        files_display = ', '.join(f'`{f}`' for f in files_with_child)
                        output_lines.append(f"**Element:** `{child}`")
                        output_lines.append(f"**Found in:** {files_display}")
                        output_lines.append("")
                    else:
                        files_display = ', '.join(f'"{f}"' for f in files_with_child)
                        output_lines.append(f"     - {child}")
                        output_lines.append(f"       Found in: {files_display}")
            else:
                if is_markdown:
                    output_lines.append("### Unique Children")
                    output_lines.append("")
                    output_lines.append("✅ All children consistent across files")
                    output_lines.append("")
                else:
                    output_lines.append(f"   Unique Children: All children consistent across files")
        elif section_data['unique_children'] and len(section_data['occurrences']) == 1:
            # For single files, don't show unique children unless specifically requested
            if is_markdown:
                output_lines.append("### Unique Children")
                output_lines.append("")
                output_lines.append(f"📄 {len(section_data['unique_children'])} elements (single file)")
                output_lines.append("")
            else:
                output_lines.append(f"   Unique Children: {len(section_data['unique_children'])} elements (single file)")
        else:
            if is_markdown:
                output_lines.append("### Unique Children")
                output_lines.append("")
                output_lines.append("❌ None")
                output_lines.append("")
            else:
                output_lines.append(f"   Unique Children: None")
        
        if show_details:
            if is_markdown:
                output_lines.append("### All Section Occurrences")
                output_lines.append("")
            else:
                output_lines.append(f"   All section occurrences:")
                
            for occurrence in section_data['occurrences']:
                occurrence_file = Path(occurrence['file']).name
                if is_markdown:
                    output_lines.append(f"**File:** `{occurrence_file}`")
                    if occurrence['all_attributes']:
                        attrs = ', '.join([f"`{k}='{v}'`" for k, v in occurrence['all_attributes'].items()])
                        output_lines.append(f"**Attributes:** {attrs}")
                    output_lines.append("")
                else:
                    output_lines.append(f"     - {occurrence_file}")
                    if occurrence['all_attributes']:
                        attrs = ', '.join([f"{k}='{v}'" for k, v in occurrence['all_attributes'].items()])
                        output_lines.append(f"       Attributes: {attrs}")
        
        if is_markdown:
            output_lines.append("---")
            output_lines.append("")
    
    # Join all lines with newlines
    output_text = '\n'.join(output_lines)
    
    # Add summary section for markdown
    if is_markdown:
        summary_lines = create_summary_section(unique_sections, is_markdown)
        summary_text = '\n'.join(summary_lines)
        output_text = summary_text + output_text
    
    # Print to console
    print(output_text)
    
    # Write to file if specified
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"\nOutput saved to: {output_file}")
        except Exception as e:
            print(f"\nError writing to file: {e}")

def create_summary_section(unique_sections, is_markdown=False):
    """Create a summary section for the catalog."""
    output_lines = []
    
    # Calculate statistics
    total_sections = len(unique_sections)
    single_file_sections = sum(1 for s in unique_sections.values() if len(s['occurrences']) == 1)
    multi_file_sections = total_sections - single_file_sections
    
    # Count by tag type
    section_tags = sum(1 for s in unique_sections.values() if s['tag'] == 'section')
    div_tags = sum(1 for s in unique_sections.values() if s['tag'] == 'div')
    
    # Find most common classes
    class_counts = Counter()
    for section_data in unique_sections.values():
        for class_name in section_data['classes']:
            class_counts[class_name] += 1
    
    if is_markdown:
        output_lines.append("## 📊 Summary")
        output_lines.append("")
        output_lines.append(f"- **Total unique sections:** {total_sections}")
        output_lines.append(f"- **Single file sections:** {single_file_sections}")
        output_lines.append(f"- **Multi-file sections:** {multi_file_sections}")
        output_lines.append(f"- **`<section>` elements:** {section_tags}")
        output_lines.append(f"- **`<div>` elements:** {div_tags}")
        output_lines.append("")
        
        if class_counts:
            output_lines.append("### Most Common Classes")
            output_lines.append("")
            for class_name, count in class_counts.most_common(10):
                output_lines.append(f"- `{class_name}`: {count} sections")
            output_lines.append("")
    
    return output_lines

def find_similar_sections(unique_sections):
    """Find sections that have the same classes but different content."""
    sections_by_structure = defaultdict(list)
    
    for key, section_data in unique_sections.items():
        classes_str = ' '.join(sorted(section_data['classes']))
        structure_key = f"classes:{classes_str}"
        
        sections_by_structure[structure_key].append({
            'full_key': key,
            'content_hash': section_data['content_hash'],
            'data': section_data
        })
    
    similar_sections = {}
    for structure_key, sections in sections_by_structure.items():
        if len(sections) > 1:
            similar_sections[structure_key] = sections
    
    return similar_sections

def display_similar_sections(similar_sections, is_markdown=False):
    """Display sections that look similar but have different content."""
    if not similar_sections:
        if is_markdown:
            return []
        else:
            print("\nNo sections found with same classes but different content.")
            return
    
    output_lines = []
    
    if is_markdown:
        output_lines.append("## 🔄 Sections with Same Structure but Different Content")
        output_lines.append("")
    else:
        print("\n" + "="*60)
        print("SECTIONS WITH SAME STRUCTURE BUT DIFFERENT CONTENT")
        print("="*60)
    
    for structure_key, sections in similar_sections.items():
        if is_markdown:
            output_lines.append(f"### Structure: `{structure_key}`")
            output_lines.append("")
            output_lines.append(f"**Found {len(sections)} variants:**")
            output_lines.append("")
        else:
            print(f"\nStructure: {structure_key}")
            print(f"Found {len(sections)} variants:")
        
        for i, section in enumerate(sections, 1):
            data = section['data']
            content = data['content_analysis']
            
            if is_markdown:
                output_lines.append(f"**{i}. Variant {i}**")
                output_lines.append(f"- **Content Hash:** `{section['content_hash']}`")
                output_lines.append(f"- **Files:** {len(data['occurrences'])}")
                output_lines.append(f"- **First seen:** `{Path(data['first_seen_in']).name}`")
                output_lines.append(f"- **Elements:** {content['total_elements']} total, {content['unique_elements']} unique")
                output_lines.append("")
            else:
                print(f"  {i}. Content Hash: {section['content_hash']}")
                print(f"     Files: {len(data['occurrences'])}")
                print(f"     First seen: {data['first_seen_in']}")
                print(f"     Elements: {content['total_elements']} total, {content['unique_elements']} unique")
    
    return output_lines if is_markdown else None

def save_to_json(unique_sections, output_file):
    """Save the catalog to a JSON file."""
    json_data = []
    for key, section_data in unique_sections.items():
        json_data.append({
            'signature_key': key,
            'classes': section_data['classes'],
            'tag': section_data['tag'],
            'content_hash': section_data['content_hash'],
            'content_analysis': section_data['content_analysis'],
            'occurrence_count': len(section_data['occurrences']),
            'first_seen_in': section_data['first_seen_in'],
            'occurrences': section_data['occurrences']
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Catalog unique HTML sections by classes and content')
    parser.add_argument('directory', help='Root directory to search for HTML files')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--text', '-t', help='Output markdown file path (use .md extension)')
    parser.add_argument('--details', '-d', action='store_true', 
                       help='Show detailed information about each occurrence')
    parser.add_argument('--content', '-c', action='store_true',
                       help='Show content breakdown for each section')
    parser.add_argument('--similar', '-s', action='store_true',
                       help='Show sections with same structure but different content')
    
    args = parser.parse_args()
    
    # Catalog the sections
    unique_sections = catalog_sections(args.directory)
    
    if not unique_sections:
        print("No sections found!")
        return
    
    # Display results
    display_results(unique_sections, args.details, args.content, args.text)
    
    # Show similar sections if requested
    if args.similar:
        similar_sections = find_similar_sections(unique_sections)
        is_markdown = args.text and args.text.endswith('.md')
        
        if is_markdown:
            # Add similar sections to markdown file
            try:
                with open(args.text, 'a', encoding='utf-8') as f:
                    similar_lines = display_similar_sections(similar_sections, is_markdown)
                    if similar_lines:
                        f.write('\n'.join(similar_lines))
                        print(f"Similar sections analysis added to: {args.text}")
            except Exception as e:
                print(f"Error adding similar sections to file: {e}")
                # Fallback to console
                display_similar_sections(similar_sections, False)
        else:
            display_similar_sections(similar_sections, False)
    
    # Save to JSON if requested
    if args.output:
        save_to_json(unique_sections, args.output)

if __name__ == "__main__":
    main()