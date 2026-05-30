def text_to_pdf(text: str, title: str = "Clinical Summary") -> bytes:
    """
    Lightweight, pure-Python PDF byte stream generator that renders
    markdown-styled text (headers, lists, normal paragraphs) with proper
    Helvetica word-wrapping and multi-page margins.
    
    No external dependencies or compiled binary requirements.
    """
    lines = text.split("\n")
    
    # Word wrap utility
    wrapped_lines = []
    max_chars_per_line = 85
    for line in lines:
        if len(line) <= max_chars_per_line:
            wrapped_lines.append(line)
        else:
            # Word wrap line
            words = line.split(" ")
            current_line = []
            for word in words:
                if len(" ".join(current_line + [word])) <= max_chars_per_line:
                    current_line.append(word)
                else:
                    wrapped_lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                wrapped_lines.append(" ".join(current_line))
                
    # Build list of page contents
    pages_streams = []
    current_page_lines = []
    current_y = 780 - 40 # Account for title
    
    # Initial page settings
    current_page_lines.append("/F1 11 Tf") # Regular font
    current_page_lines.append("14 TL")    # Line spacing
    
    for line in wrapped_lines:
        # Check for page break
        if current_y < 60:
            pages_streams.append("\n".join(current_page_lines))
            current_page_lines = ["/F1 11 Tf", "14 TL"]
            current_y = 780
            
        stripped_line = line.strip()
        escaped_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        
        # Headers formatting
        if stripped_line.startswith("###"):
            header_text = stripped_line.replace("###", "").strip()
            esc_header = header_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            current_page_lines.append("T* /F2 12 Tf") # Bold 12pt
            current_page_lines.append(f"({esc_header}) Tj")
            current_page_lines.append("/F1 11 Tf T*")
            current_y -= 28
        elif stripped_line.startswith("##"):
            header_text = stripped_line.replace("##", "").strip()
            esc_header = header_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            current_page_lines.append("T* /F2 14 Tf") # Bold 14pt
            current_page_lines.append(f"({esc_header}) Tj")
            current_page_lines.append("/F1 11 Tf T*")
            current_y -= 32
        elif stripped_line.startswith("#"):
            header_text = stripped_line.replace("#", "").strip()
            esc_header = header_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            current_page_lines.append("T* /F2 16 Tf") # Bold 16pt
            current_page_lines.append(f"({esc_header}) Tj")
            current_page_lines.append("/F1 11 Tf T*")
            current_y -= 36
        else:
            # Bullet lists
            if stripped_line.startswith("- ") or stripped_line.startswith("* "):
                bullet_content = stripped_line[2:].strip()
                esc_bullet = bullet_content.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
                # Render bullet point using bullet symbol or dash
                current_page_lines.append(f"(- {esc_bullet}) Tj T*")
            else:
                current_page_lines.append(f"({escaped_line}) Tj T*")
            current_y -= 14
            
    if current_page_lines:
        pages_streams.append("\n".join(current_page_lines))
        
    # PDF compilation
    pdf_bytes = bytearray()
    pdf_bytes.extend(b"%PDF-1.4\n")
    
    offsets = {}
    
    def write_object(obj_id: int, content_dict: dict, stream_bytes: bytes = None):
        offsets[obj_id] = len(pdf_bytes)
        pdf_bytes.extend(f"{obj_id} 0 obj\n".encode())
        
        dict_str = "<< "
        for k, v in content_dict.items():
            dict_str += f"{k} {v} "
        dict_str += ">>"
        
        if stream_bytes is not None:
            dict_str = dict_str[:-2] + f" /Length {len(stream_bytes)} >>"
            pdf_bytes.extend(dict_str.encode() + b"\nstream\n")
            pdf_bytes.extend(stream_bytes)
            pdf_bytes.extend(b"\nendstream\n")
        else:
            pdf_bytes.extend(dict_str.encode() + b"\n")
            
        pdf_bytes.extend(b"endobj\n")
        
    # Write catalogue & pages metadata
    write_object(1, {"/Type": "/Catalog", "/Pages": "2 0 R"})
    
    num_pages = len(pages_streams)
    page_obj_ids = []
    content_obj_ids = []
    
    next_obj_id = 5
    for i in range(num_pages):
        page_obj_ids.append(next_obj_id)
        content_obj_ids.append(next_obj_id + 1)
        next_obj_id += 2
        
    kids_str = "[" + " ".join([f"{pid} 0 R" for pid in page_obj_ids]) + "]"
    write_object(2, {"/Type": "/Pages", "/Kids": kids_str, "/Count": str(num_pages)})
    
    # Setup Font objects
    write_object(3, {"/Type": "/Font", "/Subtype": "/Type1", "/BaseFont": "/Helvetica"})
    write_object(4, {"/Type": "/Font", "/Subtype": "/Type1", "/BaseFont": "/Helvetica-Bold"})
    
    # Write pages and text content streams
    for i in range(num_pages):
        page_id = page_obj_ids[i]
        content_id = content_obj_ids[i]
        
        write_object(page_id, {
            "/Type": "/Page",
            "/Parent": "2 0 R",
            "/Resources": "<< /Font << /F1 3 0 R /F2 4 0 R >> >>",
            "/MediaBox": "[0 0 595.27 841.89]", # A4 Portrait
            "/Contents": f"{content_id} 0 R"
        })
        
        # Page body content builder
        page_header = f"BT\n50 780 Td\n/F2 16 Tf\n20 TL\n({title.replace('(', '\\(').replace(')', '\\)')}) Tj T*\n12 Td\n"
        page_footer = "\nET\n"
        
        page_stream_data = page_header.encode() + pages_streams[i].encode() + page_footer.encode()
        write_object(content_id, {}, page_stream_data)
        
    # Build cross-reference (xref) table
    xref_pos = len(pdf_bytes)
    pdf_bytes.extend(b"xref\n")
    total_objs = 5 + 2 * num_pages
    pdf_bytes.extend(f"0 {total_objs}\n".encode())
    pdf_bytes.extend(b"0000000000 65535 f \n")
    for obj_id in range(1, total_objs):
        offset = offsets.get(obj_id, 0)
        pdf_bytes.extend(f"{offset:010d} 00000 n \n".encode())
        
    # Write trailer metadata
    pdf_bytes.extend(b"trailer\n")
    pdf_bytes.extend(f"<< /Size {total_objs} /Root 1 0 R >>\n".encode())
    pdf_bytes.extend(b"startxref\n")
    pdf_bytes.extend(f"{xref_pos}\n".encode())
    pdf_bytes.extend(b"%%EOF\n")
    
    return bytes(pdf_bytes)
