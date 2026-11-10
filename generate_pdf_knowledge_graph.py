# -*- coding: utf-8 -*-
r"""
Script tự động quét toàn bộ Kho Văn Bản Nghiệp Vụ (FILE PDF) tại:
E:\Tài liệu UBKT\14. Văn bản nghiệp vụ\FILE PDF (hoặc Google Drive)
và xuất bản Bản Đồ Tri Thức 3D Không Gian Tương Tác chuẩn Canvas JS thuần (Phong cách Minh Đỗ).
"""

import os
import re
import json
import math
import time
import sys
import urllib.parse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def classify_pdf(rel_path, fname):
    if 'hết hiệu lực' in rel_path.lower():
        return 'expired', 'CÁC VĂN BẢN ĐÃ HẾT HIỆU LỰC', 'Hết Hiệu Lực', '#64748B', 'Kho lưu trữ các quy định, quyết định đã được thay thế để phục vụ nghiên cứu và đối chiếu lịch sử.'
    
    f_lower = fname.lower()
    if any(k in f_lower for k in ['ubkttw', 'kiểm tra', 'giám sát', 'kỷ luật', 'tố cáo', 'khiếu nại', 'vi phạm']):
        return 'ktgs', 'KIỂM TRA, GIÁM SÁT & KỶ LUẬT ĐẢNG', 'Kiểm Tra Giám Sát', '#10B981', 'Quy định 225, 212; Quyết định 354 (quy trình KTGS), 2051 (55 biểu mẫu nghiệp vụ) và các văn bản chỉ đạo của UBKT Trung ương.'
    
    if any(k in f_lower for k in ['tài sản', 'thu nhập', 'kê khai', 'phòng, chống tham nhũng', 'pctn']):
        return 'tstn', 'KIỂM SOÁT TÀI SẢN & THU NHẬP', 'Kiểm Soát TSTN', '#EF4444', 'Nghị định 164/2026/NĐ-CP, Quyết định 56-QĐ/TW, hướng dẫn kê khai, xác minh và phối hợp kiểm soát tài sản thu nhập.'
    
    if any(k in f_lower for k in ['thể thức', 'vptw', 'văn phòng', 'lưu trữ', 'bí mật nhà nước', 'bảo vệ bí mật']):
        return 'vptw', 'THỂ THỨC & CÔNG TÁC VĂN PHÒNG', 'Thể Thức & VPTW', '#3B82F6', 'Quy định 399-QĐ/TW, Hướng dẫn 05-HD/VPTW về thể loại, thẩm quyền và kỹ thuật trình bày văn bản Đảng.'
    
    if any(k in f_lower for k in ['btctw', 'btctu', 'tổ chức', 'đảng viên', 'điều lệ', 'huy hiệu', 'kết nạp', 'chuyển sinh hoạt', 'chi bộ']):
        return 'tochuc', 'TỔ CHỨC, CÁN BỘ & ĐẢNG VIÊN', 'Tổ Chức Cán Bộ', '#8B5CF6', 'Thi hành Điều lệ Đảng, quản lý đảng viên, kết nạp, chuyển sinh hoạt đảng, tặng Huy hiệu Đảng và sắp xếp tổ chức cơ sở đảng.'
    
    if any(k in f_lower for k in ['nghị định', 'luật', 'thông tư', 'chính phủ', 'quốc hội', 'thủ tướng']):
        return 'nhanuoc', 'VĂN BẢN QUY PHẠM PHÁP LUẬT NHÀ NƯỚC', 'Pháp Luật Nhà Nước', '#06B6D4', 'Các luật, nghị định, thông tư của cơ quan nhà nước liên quan đến hành chính, công chức, viên chức và kiểm tra.'
    
    return 'tw', 'CHỦ TRƯƠNG, NGHỊ QUYẾT & QUY ĐỊNH TW', 'Quy Định TW', '#F59E0B', 'Các văn kiện, nghị quyết, chỉ thị, kết luận của Ban Chấp hành Trung ương, Bộ Chính trị và Ban Bí thư.'

def scan_pdf_folder(folder_path):
    nodes = []
    edges = []

    # 1. Hub trung tâm
    nodes.append({
        'id': 'hub-central',
        'label': 'KHO VĂN BẢN NGHIỆP VỤ',
        'type': 'hub',
        'cluster': 'hub',
        'color': '#FFFDF9',
        'glowColor': '#E6C37A',
        'radius': 22,
        'x': 0, 'y': 0, 'z': 0,
        'relPath': '',
        'desc': 'Trung tâm lưu trữ 180 văn bản quy phạm, cẩm nang và hướng dẫn nghiệp vụ chuẩn định dạng PDF.',
        'outLinks': [],
        'inLinks': []
    })

    # Cấu hình 7 Cụm chuyên đề
    cluster_definitions = [
        ('ktgs', '#10B981', 'KIỂM TRA, GIÁM SÁT & KỶ LUẬT ĐẢNG', 'Kiểm Tra Giám Sát', 'Quy định 225, 212; Quyết định 354, 2051 và các văn bản chỉ đạo của UBKTTW.'),
        ('tochuc', '#8B5CF6', 'TỔ CHỨC, CÁN BỘ & ĐẢNG VIÊN', 'Tổ Chức Cán Bộ', 'Thi hành Điều lệ Đảng, nghiệp vụ đảng viên, huy hiệu và tổ chức cơ sở đảng.'),
        ('tw', '#F59E0B', 'CHỦ TRƯƠNG, NGHỊ QUYẾT & QUY ĐỊNH TW', 'Quy Định TW', 'Nghị quyết, chỉ thị, kết luận của BCH Trung ương, Bộ Chính trị và Ban Bí thư.'),
        ('vptw', '#3B82F6', 'THỂ THỨC & CÔNG TÁC VĂN PHÒNG', 'Thể Thức & VPTW', 'Quy định 399-QĐ/TW, Hướng dẫn 05-HD/VPTW, bảo vệ bí mật nhà nước và công tác văn phòng.'),
        ('tstn', '#EF4444', 'KIỂM SOÁT TÀI SẢN & THU NHẬP', 'Kiểm Soát TSTN', 'Nghị định 164/2026/NĐ-CP, Quyết định 56-QĐ/TW và quy chế phối hợp kiểm soát tài sản thu nhập.'),
        ('nhanuoc', '#06B6D4', 'VĂN BẢN NHÀ NƯỚC & PHÁP LUẬT', 'Pháp Luật Nhà Nước', 'Luật, Nghị định, Thông tư quy phạm pháp luật liên quan.'),
        ('expired', '#64748B', 'CÁC VĂN BẢN ĐÃ HẾT HIỆU LỰC', 'Hết Hiệu Lực', 'Văn bản đã được thay thế để phục vụ nghiên cứu và đối chiếu lịch sử.')
    ]

    c_count = len(cluster_definitions)
    c_radius = 270.0
    cluster_centers = {}

    for idx, (ckey, ccolor, clabel, cshort, cdesc) in enumerate(cluster_definitions):
        phi = math.acos(1.0 - 2.0 * (idx + 0.5) / c_count)
        theta = math.pi * (1.0 + math.sqrt(5.0)) * idx
        cx = c_radius * math.sin(phi) * math.cos(theta)
        cy = c_radius * math.sin(phi) * math.sin(theta) * 0.78
        cz = c_radius * math.cos(phi)

        cluster_centers[ckey] = (cx, cy, cz)
        cid = f"cluster-{ckey}"

        nodes.append({
            'id': cid,
            'label': clabel,
            'short': cshort,
            'type': 'cluster',
            'cluster': ckey,
            'color': ccolor,
            'glowColor': ccolor,
            'radius': 14,
            'x': cx, 'y': cy, 'z': cz,
            'relPath': '',
            'desc': cdesc,
            'outLinks': [],
            'inLinks': []
        })

        # Nối Hub tới Cụm
        edges.append({
            'source': 'hub-central',
            'target': cid,
            'type': 'hub-link',
            'color': ccolor,
            'width': 2.2
        })

    # Nối vòng tròn các Cụm kề nhau (Mesh ring)
    for i in range(c_count):
        edges.append({
            'source': f"cluster-{cluster_definitions[i][0]}",
            'target': f"cluster-{cluster_definitions[(i + 1) % c_count][0]}",
            'type': 'cluster-ring',
            'color': '#334155',
            'width': 1.0
        })

    # 2. Quét tệp PDF
    cluster_buckets = {c[0]: [] for c in cluster_definitions}
    all_files_info = []

    doc_idx = 0
    for root, dirs, files in os.walk(folder_path):
        for fname in sorted(files):
            if not fname.lower().endswith('.pdf'):
                continue
            
            doc_idx += 1
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, folder_path).replace('\\', '/')
            base_name = os.path.splitext(fname)[0]

            size_bytes = os.path.getsize(full_path)
            size_str = f"{size_bytes / (1024*1024):.2f} MB" if size_bytes >= 1024*1024 else f"{size_bytes / 1024:.0f} KB"
            mtime_str = time.strftime('%d/%m/%Y', time.localtime(os.path.getmtime(full_path)))

            ckey, clabel, cshort, ccolor, cdesc = classify_pdf(rel_path, fname)

            # Tách số hiệu và trích yếu
            so_hieu = ''
            trich_yeu = base_name
            m = re.match(r'^(\d+[\s\-_]+[A-Za-z0-9\-_]+)[\s\-_]+(.+)$', base_name)
            if m:
                so_hieu = m.group(1).replace('_', '-').strip()
                trich_yeu = m.group(2).strip()

            # URL mở file nội bộ (Windows file URI)
            normalized_full_path = os.path.abspath(full_path).replace('\\', '/')
            file_uri = f"file:///{urllib.parse.quote(normalized_full_path)}"

            node_data = {
                'id': f"doc-{doc_idx}",
                'label': base_name,
                'fileName': fname,
                'baseName': base_name,
                'soHieu': so_hieu,
                'trichYeu': trich_yeu,
                'type': 'doc',
                'cluster': ckey,
                'color': ccolor,
                'glowColor': ccolor,
                'radius': 5.8,
                'relPath': rel_path,
                'fullPath': normalized_full_path,
                'fileUri': file_uri,
                'size': size_str,
                'mtime': mtime_str,
                'desc': f"{trich_yeu} (Số hiệu: {so_hieu or 'Không rõ'}). Cập nhật: {mtime_str}. Dung lượng: {size_str}.",
                'outLinks': [],
                'inLinks': []
            }
            cluster_buckets[ckey].append(node_data)
            all_files_info.append(node_data)

    # 3. Phân bổ tọa độ 3D quanh từng Cụm (Nebula Cloud)
    for ckey, (cx, cy, cz) in cluster_centers.items():
        items = cluster_buckets[ckey]
        count = len(items)
        cluster_node_id = f"cluster-{ckey}"

        for i, node in enumerate(items):
            u = (i + 0.5) / max(1, count)
            phi_sub = math.acos(1.0 - 2.0 * u)
            theta_sub = math.pi * (1.0 + math.sqrt(5.0)) * i
            
            sub_r = 30.0 + 80.0 * math.sqrt(u)
            
            nx = cx + sub_r * math.sin(phi_sub) * math.cos(theta_sub)
            ny = cy + sub_r * math.sin(phi_sub) * math.sin(theta_sub)
            nz = cz + sub_r * math.cos(phi_sub)

            node['x'] = nx
            node['y'] = ny
            node['z'] = nz
            nodes.append(node)

            # Cạnh nối từ Cụm đến File
            edges.append({
                'source': cluster_node_id,
                'target': node['id'],
                'type': 'cluster-item',
                'color': node['color'],
                'width': 0.7
            })

    # 4. Tạo liên kết chéo giữa các văn bản có mối liên hệ số hiệu (vd: 225 - 354, 399 - 05, 164 - 56, v.v.)
    related_pairs = [
        ('399', '05'), ('225', '354'), ('225', '2051'), ('225', '212'),
        ('354', '2051'), ('212', '03'), ('225', '2011'), ('2011', '354'),
        ('207', '02'), ('56', '164'), ('07', '06')
    ]
    cross_link_count = 0
    edge_set = set()

    for i in range(len(all_files_info)):
        for j in range(i + 1, len(all_files_info)):
            fa = all_files_info[i]
            fb = all_files_info[j]
            # Kiểm tra nếu tên file nhắc tới số hiệu của nhau
            has_relation = False
            for num1, num2 in related_pairs:
                if (num1 in fa['baseName'] and num2 in fb['baseName']) or (num2 in fa['baseName'] and num1 in fb['baseName']):
                    has_relation = True
                    break
            
            if has_relation:
                ek = tuple(sorted([fa['id'], fb['id']]))
                if ek not in edge_set:
                    edge_set.add(ek)
                    fa['outLinks'].append(fb['id'])
                    fb['inLinks'].append(fa['id'])
                    edges.append({
                        'source': fa['id'],
                        'target': fb['id'],
                        'type': 'relation',
                        'color': '#F59E0B',
                        'width': 1.4
                    })
                    cross_link_count += 1

    print(f"Tổng kết: {len(nodes)} Nút (1 Hub, {c_count} Cụm, {len(all_files_info)} Tệp PDF)")
    print(f"Tổng kết: {len(edges)} Cạnh liên kết ({cross_link_count} liên kết chéo nghiệp vụ)")

    return {
        'nodes': nodes,
        'edges': edges,
        'stats': {
            'totalNodes': len(nodes),
            'totalFiles': len(all_files_info),
            'totalClusters': c_count,
            'crossLinks': cross_link_count
        }
    }

def generate_html(graph_data, output_path):
    data_json = json.dumps(graph_data, ensure_ascii=False)

    html_template = f'''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
  <title>Bản Đồ Tri Thức 3D · Kho Văn Bản Nghiệp Vụ</title>
  <meta name="description" content="Bản đồ tri thức 3D không gian tương tác trực quan hóa kho văn bản nghiệp vụ xây dựng Đảng, kiểm tra, giám sát và thi hành kỷ luật." />
  <meta property="og:title" content="Bản Đồ Tri Thức 3D · Kho Văn Bản Nghiệp Vụ" />
  <meta property="og:description" content="Trực quan hóa không gian tri thức đa chiều các quy định, hướng dẫn và quy trình công tác Đảng và KTGS." />
  <meta property="og:type" content="website" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      /* Mặc định: GIAO DIỆN SÁNG (Nền trắng ngọc, chữ xanh Navy nổi bật) */
      --bg: #F8FAFC;
      --bg-gradient: radial-gradient(circle at 50% 50%, #FFFFFF 0%, #F1F5F9 55%, #E2E8F0 100%);
      --card-bg: rgba(255, 255, 255, 0.94);
      --card-border: rgba(37, 99, 235, 0.22);
      --card-shadow: 0 8px 30px rgba(15, 23, 42, 0.08);
      --text: #0F172A;
      --text-muted: #475569;
      --text-blue: #1D4ED8;
      --text-navy: #1E3A8A;
      --accent: #2563EB;
      --accent-glow: rgba(37, 99, 235, 0.35);
      
      --input-bg: #FFFFFF;
      --input-text: #0F172A;
      --input-border: #93C5FD;
      
      --btn-bg: #FFFFFF;
      --btn-text: #1E3A8A;
      --btn-border: #CBD5E1;
      --btn-hover-bg: #EFF6FF;
      --btn-active-bg: #DBEAFE;
      --btn-active-text: #1D4ED8;
      --btn-active-border: #2563EB;
      
      --drawer-bg: rgba(255, 255, 255, 0.98);
      --drawer-border: rgba(203, 213, 225, 0.85);
      --drawer-shadow: -10px 0 35px rgba(15, 23, 42, 0.12);
      --drawer-title: #1E3A8A;
      --drawer-badge-bg: #EFF6FF;
      --drawer-badge-border: #BFDBFE;
      --drawer-badge-text: #1D4ED8;
      --drawer-meta-bg: #F8FAFC;
      --drawer-meta-border: #E2E8F0;
      --drawer-meta-val: #0F172A;
      --drawer-path-bg: #F1F5F9;
      --drawer-path-text: #475569;
      --drawer-desc-text: #1E293B;
      
      --stat-bg: rgba(255, 255, 255, 0.95);
      --stat-border: rgba(37, 99, 235, 0.22);
      --stat-num: #1D4ED8;
      --stat-text: #475569;
    }}

    [data-theme="dark"] {{
      /* Chế độ ban đêm Dark Mode Cyberpunk */
      --bg: #090D16;
      --bg-gradient: radial-gradient(circle at 50% 50%, #0F172A 0%, #090D16 80%);
      --card-bg: rgba(15, 23, 42, 0.90);
      --card-border: rgba(148, 163, 184, 0.16);
      --card-shadow: 0 10px 35px rgba(0, 0, 0, 0.5);
      --text: #F8FAFC;
      --text-muted: #94A3B8;
      --text-blue: #60A5FA;
      --text-navy: #93C5FD;
      --accent: #EAB308;
      --accent-glow: rgba(234, 179, 8, 0.35);
      
      --input-bg: rgba(15, 23, 42, 0.90);
      --input-text: #FFFFFF;
      --input-border: rgba(148, 163, 184, 0.25);
      
      --btn-bg: rgba(15, 23, 42, 0.90);
      --btn-text: #F8FAFC;
      --btn-border: rgba(148, 163, 184, 0.2);
      --btn-hover-bg: rgba(30, 41, 59, 0.95);
      --btn-active-bg: rgba(30, 41, 59, 0.95);
      --btn-active-text: #EAB308;
      --btn-active-border: #EAB308;
      
      --drawer-bg: rgba(15, 23, 42, 0.94);
      --drawer-border: rgba(148, 163, 184, 0.16);
      --drawer-shadow: -10px 0 35px rgba(0, 0, 0, 0.6);
      --drawer-title: #FFFFFF;
      --drawer-badge-bg: rgba(255, 255, 255, 0.08);
      --drawer-badge-border: rgba(255, 255, 255, 0.12);
      --drawer-badge-text: #EAB308;
      --drawer-meta-bg: rgba(255, 255, 255, 0.06);
      --drawer-meta-border: rgba(255, 255, 255, 0.08);
      --drawer-meta-val: #F8FAFC;
      --drawer-path-bg: rgba(0, 0, 0, 0.3);
      --drawer-path-text: #64748B;
      --drawer-desc-text: #CBD5E1;
      
      --stat-bg: rgba(15, 23, 42, 0.90);
      --stat-border: rgba(148, 163, 184, 0.16);
      --stat-num: #FFFFFF;
      --stat-text: #94A3B8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      background-image: var(--bg-gradient);
      color: var(--text);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      user-select: none;
      transition: background 0.3s ease, color 0.3s ease;
    }}
    #stage {{
      position: relative;
      width: 100%;
      height: 100%;
    }}
    canvas {{
      display: block;
      width: 100%;
      height: 100%;
      cursor: grab;
      touch-action: none;
    }}
    canvas:active {{ cursor: grabbing; }}

    /* HUD Header Bar */
    .hud-header {{
      position: absolute;
      top: 18px;
      left: 20px;
      right: 20px;
      display: flex;
      justify-content: flex-end;
      align-items: center;
      pointer-events: none;
      z-index: 10;
    }}
    .hud-header * {{ pointer-events: auto; }}

    /* Bộ công cụ & Thanh tìm kiếm */
    .hud-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .search-box {{
      position: relative;
      width: 290px;
    }}
    .search-box input {{
      width: 100%;
      background: var(--input-bg);
      backdrop-filter: blur(12px);
      border: 1.5px solid var(--input-border);
      color: var(--input-text);
      font-size: 13px;
      font-weight: 500;
      padding: 9px 14px 9px 34px;
      border-radius: 10px;
      outline: none;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      transition: all 0.2s ease;
    }}
    .search-box input:focus {{
      border-color: #2563EB;
      box-shadow: 0 0 14px rgba(37, 99, 235, 0.35);
    }}
    .search-box input::placeholder {{
      color: var(--text-muted);
    }}
    .search-icon {{
      position: absolute;
      left: 11px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 14px;
      color: #2563EB;
    }}
    .hud-btn {{
      background: var(--btn-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--btn-border);
      color: var(--btn-text);
      font-size: 13px;
      font-weight: 600;
      padding: 9px 14px;
      border-radius: 10px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      transition: all 0.2s ease;
    }}
    .hud-btn:hover {{
      background: var(--btn-hover-bg);
      border-color: var(--accent);
      transform: translateY(-1px);
    }}
    .hud-btn.active {{
      background: var(--btn-active-bg);
      border-color: var(--btn-active-border);
      color: var(--btn-active-text);
      box-shadow: 0 2px 10px rgba(37, 99, 235, 0.18);
    }}

    /* Thanh điều hướng chân trang (Bottom HUD Bar) */
    .hud-bottom-bar {{
      position: absolute;
      bottom: 18px;
      left: 20px;
      right: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      pointer-events: none;
      z-index: 10;
    }}
    .hud-bottom-bar * {{ pointer-events: auto; }}

    .bottom-left-group {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .hud-stats-pill {{
      background: var(--stat-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--stat-border);
      padding: 6px 14px;
      border-radius: 9999px;
      display: flex;
      gap: 10px;
      font-size: 12px;
      color: var(--stat-text);
      box-shadow: var(--card-shadow);
    }}
    .stat-badge b {{
      color: var(--stat-num);
      font-weight: 700;
      margin-right: 3px;
    }}

    /* Viên thuốc Chú thích Phân loại Cụm (Legend Capsule) giống hình người dùng gửi */
    .legend-capsule {{
      background: var(--card-bg);
      backdrop-filter: blur(14px);
      border: 1px solid var(--card-border);
      border-radius: 9999px;
      padding: 5px 12px;
      display: flex;
      align-items: center;
      gap: 8px;
      box-shadow: var(--card-shadow);
      overflow-x: auto;
      max-width: calc(100vw - 480px);
    }}
    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text);
      cursor: pointer;
      padding: 4px 9px;
      border-radius: 9999px;
      transition: all 0.2s ease;
      white-space: nowrap;
      user-select: none;
    }}
    .legend-item .dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      flex-shrink: 0;
      display: inline-block;
    }}
    .legend-item:hover {{
      background: var(--btn-hover-bg);
      color: var(--text-blue);
      transform: translateY(-1px);
    }}
    .legend-item.active {{
      background: var(--btn-active-bg);
      border: 1px solid var(--btn-active-border);
      color: var(--btn-active-text);
      box-shadow: 0 1px 6px rgba(37, 99, 235, 0.18);
    }}

    /* Hướng dẫn thao tác góc phải giống hệt hình người dùng gửi */
    .hud-instructions {{
      font-size: 12px;
      font-weight: 500;
      color: var(--text-muted);
      letter-spacing: 0.2px;
      white-space: nowrap;
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 9999px;
      padding: 7px 16px;
      box-shadow: var(--card-shadow);
    }}

    /* Drawer xem chi tiết Văn bản PDF */
    .detail-drawer {{
      position: absolute;
      top: 20px;
      bottom: 20px;
      right: -430px;
      width: 410px;
      background: var(--drawer-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--drawer-border);
      border-radius: 16px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: var(--drawer-shadow);
      transition: right 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 25;
      overflow-y: auto;
    }}
    .detail-drawer.open {{ right: 20px; }}

    .drawer-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 10px;
    }}
    .drawer-badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      padding: 4px 10px;
      border-radius: 6px;
      background: var(--drawer-badge-bg);
      border: 1px solid var(--drawer-badge-border);
      color: var(--drawer-badge-text);
    }}
    .drawer-close {{
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 20px;
      cursor: pointer;
      line-height: 1;
    }}
    .drawer-close:hover {{ color: var(--text); }}

    .drawer-title {{
      font-size: 17px;
      font-weight: 700;
      line-height: 1.4;
      color: var(--drawer-title);
    }}
    .drawer-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      font-size: 11px;
      color: var(--text-muted);
    }}
    .meta-tag {{
      background: var(--drawer-meta-bg);
      padding: 5px 10px;
      border-radius: 6px;
      border: 1px solid var(--drawer-meta-border);
    }}
    .meta-tag b {{ color: var(--drawer-meta-val); }}

    .drawer-path {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--drawer-path-text);
      word-break: break-all;
      background: var(--drawer-path-bg);
      border: 1px solid var(--drawer-meta-border);
      padding: 6px 10px;
      border-radius: 6px;
    }}
    .drawer-desc {{
      font-size: 13px;
      line-height: 1.6;
      color: var(--drawer-desc-text);
      border-left: 3px solid var(--accent);
      padding-left: 12px;
    }}

    .drawer-actions {{
      margin-top: auto;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .action-btn {{
      width: 100%;
      padding: 10px 14px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.2s ease;
      border: none;
    }}
    .action-btn-primary {{
      background: linear-gradient(135deg, #2563EB, #1D4ED8);
      color: #FFF;
      box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35);
    }}
    .action-btn-primary:hover {{
      box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
      transform: translateY(-1px);
    }}
    .action-btn-secondary {{
      background: var(--drawer-meta-bg);
      color: var(--btn-text);
      border: 1px solid var(--drawer-meta-border);
    }}
    .action-btn-secondary:hover {{
      background: var(--btn-hover-bg);
    }}

    .action-hint {{
      font-size: 11px;
      line-height: 1.5;
      color: var(--text-muted);
      background: var(--drawer-meta-bg);
      border: 1px solid var(--drawer-meta-border);
      padding: 10px 12px;
      border-radius: 8px;
    }}
    .action-hint code {{
      color: var(--text-blue);
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }}
    .toast-popup {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      max-width: 440px;
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border: 1.5px solid var(--accent);
      border-radius: 12px;
      padding: 14px 18px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      box-shadow: 0 10px 35px rgba(0, 0, 0, 0.22);
      transform: translateY(120px);
      opacity: 0;
      pointer-events: none;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 999;
    }}
    .toast-popup.show {{
      transform: translateY(0);
      opacity: 1;
      pointer-events: auto;
    }}
    .toast-icon {{ font-size: 22px; flex-shrink: 0; line-height: 1; }}
    .toast-title {{ font-size: 13px; font-weight: 700; color: var(--text-blue); margin-bottom: 4px; }}
    .toast-desc {{ font-size: 12px; color: var(--text); line-height: 1.5; }}

    .instr-mobile {{ display: none; }}

    /* Responsive cho màn hình vừa (Máy tính bảng) */
    @media (max-width: 960px) {{
      .hud-header {{ top: 12px; left: 12px; right: 12px; }}
      .search-box {{ width: 200px; }}
      .hud-btn {{ padding: 7px 11px; font-size: 12px; }}
      .hud-bottom-bar {{ bottom: 12px; left: 12px; right: 12px; flex-direction: column; align-items: stretch; gap: 8px; }}
      .bottom-left-group {{ justify-content: space-between; }}
      .legend-capsule {{ max-width: 100%; }}
      .hud-instructions {{ align-self: center; font-size: 11px; }}
      .detail-drawer {{ width: min(400px, 92vw); }}
    }}

    /* Tối ưu hóa chuyên sâu cho Điện thoại di động (Smartphones <= 640px) */
    @media (max-width: 640px) {{
      .hud-header {{
        top: 8px;
        left: 8px;
        right: 8px;
        justify-content: flex-start;
      }}
      .hud-actions {{
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        padding-bottom: 3px;
        gap: 6px;
      }}
      .hud-actions::-webkit-scrollbar {{ display: none; }}
      .search-box {{
        min-width: 165px;
        width: 165px;
        flex-shrink: 0;
      }}
      .search-box input {{
        font-size: 12px;
        padding: 7px 10px 7px 28px;
      }}
      .search-icon {{ left: 8px; font-size: 12px; }}
      .hud-btn {{
        padding: 6px 10px;
        font-size: 11.5px;
        white-space: nowrap;
        flex-shrink: 0;
      }}
      .hud-bottom-bar {{
        bottom: 8px;
        left: 8px;
        right: 8px;
        flex-direction: column;
        align-items: stretch;
        gap: 6px;
      }}
      .bottom-left-group {{
        flex-direction: column;
        align-items: stretch;
        gap: 6px;
      }}
      .hud-stats-pill {{
        align-self: flex-start;
        padding: 4px 10px;
        font-size: 11px;
      }}
      .legend-capsule {{
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        white-space: nowrap;
        flex-wrap: nowrap;
        padding: 5px 10px;
        border-radius: 12px;
        gap: 12px;
      }}
      .legend-capsule::-webkit-scrollbar {{ display: none; }}
      .legend-item {{
        flex-shrink: 0;
        font-size: 11.5px;
      }}
      .instr-desktop {{ display: none; }}
      .instr-mobile {{
        display: inline;
        font-size: 10.5px;
        text-align: center;
        opacity: 0.85;
      }}
      .detail-drawer {{
        top: auto;
        bottom: 0;
        left: 0;
        right: 0;
        width: 100%;
        max-width: 100vw;
        max-height: 82vh;
        border-radius: 20px 20px 0 0;
        border-left: none;
        border-right: none;
        border-bottom: none;
        border-top: 1px solid var(--drawer-border);
        transform: translateY(105%);
        transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        padding: 20px 16px;
        box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.25);
      }}
      .detail-drawer.open {{
        right: 0;
        transform: translateY(0);
      }}
      .drawer-title {{ font-size: 15px; }}
      .action-btn {{
        padding: 12px 16px;
        font-size: 14px;
        border-radius: 10px;
      }}
    }}
  </style>
</head>
<body>

  <div id="stage">
    <!-- Header Controls -->
    <header class="hud-header">
      <div class="hud-actions">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" placeholder="Tìm số hiệu (225, 354, 399...), từ khóa..." autocomplete="off" />
        </div>
        <button class="hud-btn" id="btnToggleTheme" title="Chuyển đổi giao diện Nền Sáng / Nền Tối">
          <span>☀️</span> Giao Diện Sáng
        </button>
        <button class="hud-btn active" id="btnToggleLabels" title="Bật/Tắt hiển thị tên file trên toàn bộ các nút">
          <span>🏷️</span> Ẩn/Hiện tên file
        </button>
        <button class="hud-btn active" id="btnToggleRotate" title="Bật/Tắt tự động xoay">
          <span>🔄</span> Tự Xoay
        </button>
        <button class="hud-btn active" id="btnToggleLinks" title="Bật/Tắt liên kết nghiệp vụ chéo">
          <span>🕸️</span> Mạng Liên Kết
        </button>
        <button class="hud-btn" id="btnResetView" title="Đưa góc nhìn về chính diện">
          <span>🎯</span> Góc Nhìn Gốc
        </button>
        <button class="hud-btn" id="btnToggleFullscreen" title="Bật/Tắt xem toàn màn hình">
          <span>⛶</span> Toàn Màn Hình
        </button>
      </div>
    </header>

    <!-- Drawer chi tiết tệp PDF -->
    <aside class="detail-drawer" id="detailDrawer">
      <div class="drawer-header">
        <span class="drawer-badge" id="dBadge">VĂN BẢN PDF</span>
        <button class="drawer-close" id="dCloseBtn">✕</button>
      </div>
      <h2 class="drawer-title" id="dTitle">Tên văn bản PDF</h2>
      <div class="drawer-meta" id="dMeta">
        <span class="meta-tag">Số hiệu: <b id="dSoHieu">--</b></span>
        <span class="meta-tag">Dung lượng: <b id="dSize">--</b></span>
        <span class="meta-tag">Ngày: <b id="dDate">--</b></span>
      </div>
      <div class="drawer-path" id="dPath">FILE PDF/...</div>
      <p class="drawer-desc" id="dDesc">Trích yếu nội dung văn bản...</p>

      <div class="drawer-actions">
        <button class="action-btn action-btn-primary" id="dSmartOpenBtn" title="Mở trực tiếp toàn văn tệp PDF trên trình duyệt">
          <span>📖 Mở Toàn Văn Tệp PDF</span>
        </button>
        <div class="action-hint" id="dActionHint">
          <span>💡 <b>Hỗ trợ đa nền tảng:</b> Bấm nút trên hoặc nhấp đúp vào văn bản để xem trực tiếp file PDF mượt mà trên cả máy tính và điện thoại di động.</span>
        </div>
      </div>
    </aside>

    <!-- Thanh điều hướng chân trang (Legend & Hướng dẫn thao tác) -->
    <footer class="hud-bottom-bar">
      <div class="bottom-left-group">
        <div class="hud-stats-pill">
          <span class="stat-badge"><b>{graph_data['stats']['totalFiles']}</b> Tệp</span>
          <span class="stat-badge"><b>{graph_data['stats']['crossLinks']}</b> Liên Kết</span>
        </div>
        <div class="legend-capsule" id="legendCapsule">
          <div class="legend-item active" data-cluster="all" title="Xem toàn bộ các cụm chuyên đề">
            <span class="dot" style="background: var(--text-blue);"></span>Tất cả
          </div>
          <div class="legend-item" data-cluster="ktgs" title="Xem chuyên đề Kiểm tra, Giám sát & Kỷ luật Đảng">
            <span class="dot" style="background: #10B981;"></span>Kiểm Tra Giám Sát
          </div>
          <div class="legend-item" data-cluster="tochuc" title="Xem nghiệp vụ Tổ chức, Cán bộ & Đảng viên">
            <span class="dot" style="background: #8B5CF6;"></span>Tổ Chức Cán Bộ
          </div>
          <div class="legend-item" data-cluster="tw" title="Xem Chủ trương, Nghị quyết & Quy định TW">
            <span class="dot" style="background: #F59E0B;"></span>Quy Định TW
          </div>
          <div class="legend-item" data-cluster="vptw" title="Xem Thể thức văn bản 399 & Công tác Văn phòng">
            <span class="dot" style="background: #3B82F6;"></span>Thể Thức & VPTW
          </div>
          <div class="legend-item" data-cluster="nhanuoc" title="Xem Văn bản quy phạm pháp luật Nhà nước">
            <span class="dot" style="background: #06B6D4;"></span>Pháp Luật Nhà Nước
          </div>
          <div class="legend-item" data-cluster="tstn" title="Xem Kiểm soát tài sản & thu nhập (NĐ 164, QĐ 56)">
            <span class="dot" style="background: #EF4444;"></span>Kiểm Soát TSTN
          </div>
          <div class="legend-item" data-cluster="expired" title="Xem kho tài liệu lịch sử đã hết hiệu lực">
            <span class="dot" style="background: #64748B;"></span>Hết Hiệu Lực
          </div>
        </div>
      </div>

      <div class="hud-instructions">
        <span class="instr-desktop">Kéo để xoay · Lăn để phóng · Bấm đúp để về góc nhìn đầu</span>
        <span class="instr-mobile">Vuốt 1 ngón để xoay · Chụm 2 ngón để phóng · Chạm để xem tệp</span>
      </div>
    </footer>

    <canvas id="graphCanvas"></canvas>

    <!-- Toast thông báo thông minh -->
    <div id="toastNotification" class="toast-popup">
      <div class="toast-icon">🚀</div>
      <div class="toast-body">
        <div class="toast-title" id="toastTitle">Đã mở tab mới & Sao chép đường dẫn!</div>
        <div class="toast-desc" id="toastDesc">Đường dẫn tệp đã sẵn sàng trong Clipboard. Bấm <b>Ctrl + V</b> rồi Enter nếu cần dán vào thanh địa chỉ.</div>
      </div>
    </div>
  </div>

  <script>
    const graphData = {data_json};

    const canvas = document.getElementById('graphCanvas');
    const ctx = canvas.getContext('2d');
    const drawer = document.getElementById('detailDrawer');
    const dBadge = document.getElementById('dBadge');
    const dTitle = document.getElementById('dTitle');
    const dSoHieu = document.getElementById('dSoHieu');
    const dSize = document.getElementById('dSize');
    const dDate = document.getElementById('dDate');
    const dPath = document.getElementById('dPath');
    const dDesc = document.getElementById('dDesc');
    const dSmartOpenBtn = document.getElementById('dSmartOpenBtn');
    const dActionHint = document.getElementById('dActionHint');
    const toast = document.getElementById('toastNotification');
    const toastTitle = document.getElementById('toastTitle');
    const toastDesc = document.getElementById('toastDesc');
    let toastTimer = null;

    function showToast(title, desc, duration = 5000) {{
      if (toastTitle) toastTitle.textContent = title;
      if (toastDesc) toastDesc.innerHTML = desc;
      if (toast) {{
        toast.classList.add('show');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => {{
          toast.classList.remove('show');
        }}, duration);
      }}
    }}

    function smartOpenDoc(node) {{
      if (!node) return;
      if (node.type === 'hub' || node.type === 'cluster') return;

      const pathUri = node.fileUri || ('file:///' + (node.fullPath || ''));
      const relUri = encodeURI(node.relPath);

      // 1. Tự động sao chép đường dẫn file:/// vào Clipboard
      try {{
        if (navigator.clipboard && navigator.clipboard.writeText) {{
          navigator.clipboard.writeText(pathUri);
        }} else {{
          const ta = document.createElement('textarea');
          ta.value = pathUri;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
        }}
      }} catch (err) {{
        console.warn('Lỗi copy clipboard:', err);
      }}

      // 2. Mở file PDF trực tiếp (Hoạt động hoàn hảo cả trên GitHub Pages và máy tính cục bộ)
      const isOnline = location.protocol.startsWith('http');
      if (isOnline) {{
        // Khi chạy trên GitHub: mở file PDF lưu trữ trên GitHub Pages
        window.open(relUri, '_blank');
        showToast(
          '📄 Đang Mở Tệp PDF Trực Tuyến!',
          `Đang tải <b>${{node.fileName || node.label}}</b> trên trình đọc PDF của trình duyệt.`
        );
      }} else {{
        // Khi chạy cục bộ trên máy tính: mở trực tiếp file PDF từ ổ đĩa
        window.open(pathUri, '_blank');
        showToast(
          '📖 Đang Mở Tệp PDF Cục Bộ!',
          `Đã mở <b>${{node.fileName || node.label}}</b> từ ổ đĩa máy tính.`
        );
      }}

      clearSearchState();
    }}
    const dCloseBtn = document.getElementById('dCloseBtn');

    const searchInput = document.getElementById('searchInput');
    const btnToggleTheme = document.getElementById('btnToggleTheme');
    const btnToggleLabels = document.getElementById('btnToggleLabels');
    const btnToggleRotate = document.getElementById('btnToggleRotate');
    const btnToggleLinks = document.getElementById('btnToggleLinks');
    const btnResetView = document.getElementById('btnResetView');
    const btnToggleFullscreen = document.getElementById('btnToggleFullscreen');

    let width = 0, height = 0, dpr = 1;
    let rotX = -0.18, rotY = 0;
    let zoom = 1.0;
    let isDragging = false;
    let lastMouseX = 0, lastMouseY = 0;
    let autoRotate = true;
    let showLinks = true;
    let showAllLabels = true;
    let hoveredNode = null;
    let selectedNode = null;
    let searchQuery = '';
    let activeCluster = 'all';

    const nodeMap = {{}};
    graphData.nodes.forEach(n => {{ nodeMap[n.id] = n; }});

    // 0. KHỞI TẠO THEME (NỀN SÁNG - CHỮ XANH NAVY MẶC ĐỊNH)
    function applyTheme(theme) {{
      if (theme === 'dark') {{
        document.documentElement.setAttribute('data-theme', 'dark');
        btnToggleTheme.innerHTML = '<span>🌙</span> Nền Tối';
        btnToggleTheme.classList.add('active');
      }} else {{
        document.documentElement.removeAttribute('data-theme');
        btnToggleTheme.innerHTML = '<span>☀️</span> Nền Sáng';
        btnToggleTheme.classList.remove('active');
      }}
      localStorage.setItem('pdf_kg_theme', theme);
    }}

    const savedTheme = localStorage.getItem('pdf_kg_theme') || 'light';
    applyTheme(savedTheme);

    btnToggleTheme.onclick = () => {{
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      applyTheme(isDark ? 'light' : 'dark');
    }};

    // 0.1 KHỞI TẠO BỘ LỌC CỤM CHUYÊN ĐỀ (LEGEND CAPSULE)
    document.querySelectorAll('.legend-item').forEach(item => {{
      item.onclick = () => {{
        const ckey = item.getAttribute('data-cluster');
        if (activeCluster === ckey && ckey !== 'all') {{
          activeCluster = 'all';
        }} else {{
          activeCluster = ckey;
        }}

        document.querySelectorAll('.legend-item').forEach(el => {{
          el.classList.toggle('active', el.getAttribute('data-cluster') === activeCluster);
        }});

        if (activeCluster !== 'all') {{
          const targetClusterNode = graphData.nodes.find(n => n.id === 'cluster-' + activeCluster);
          if (targetClusterNode) {{
            rotY = -Math.atan2(targetClusterNode.x, targetClusterNode.z);
            rotX = -0.12;
            zoom = 1.15;
            showToast('🔍 Đang lọc chuyên đề:', targetClusterNode.label, 2500);
          }}
        }} else {{
          rotX = -0.18;
          rotY = 0;
          zoom = 1.0;
        }}
      }};
    }});

    // 1. TẠO BẦU TRỜI SAO (STARFIELD)
    const stars = Array.from({{ length: 110 }}, () => ({{
      x: Math.random(),
      y: Math.random(),
      r: Math.random() * 1.4 + 0.4,
      alpha: Math.random() * 0.6 + 0.2
    }}));

    // 2. PHÉP CHIẾU 3D PHỐI CẢNH (PERSPECTIVE PROJECTION)
    function projectNode(n, cosY, sinY, cosX, sinX) {{
      const x1 = n.x * cosY - n.z * sinY;
      const z1 = n.z * cosY + n.x * sinY;
      const y2 = n.y * cosX - z1 * sinX;
      const z2 = z1 * cosX + n.y * sinX;

      const fov = 620;
      const scale = (fov / Math.max(140, fov + z2)) * zoom;

      n.px = width * 0.5 + x1 * scale;
      n.py = height * 0.5 + y2 * scale;
      n.pz = z2;
      n.pr = Math.max(2.4, n.radius * scale);
      n.pscale = scale;
    }}

    function resize() {{
      width = canvas.parentElement.clientWidth;
      height = canvas.parentElement.clientHeight;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
    }}
    window.addEventListener('resize', resize);
    resize();

    // 3. VÒNG LẶP RENDER 60 FPS
    function renderFrame() {{
      if (autoRotate && !isDragging) {{
        rotY += 0.0009;
      }}

      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

      ctx.save();
      ctx.scale(dpr, dpr);

      // Nền Canvas: Nền sáng ngọc #F8FAFC dịu mắt, Dark mode xóa trong suốt
      if (isDark) {{
        ctx.clearRect(0, 0, width, height);
      }} else {{
        ctx.fillStyle = '#F8FAFC';
        ctx.fillRect(0, 0, width, height);
      }}

      // Vẽ hạt nền / sao nền
      stars.forEach(st => {{
        ctx.fillStyle = isDark
          ? `rgba(203, 213, 225, ${{st.alpha}})`
          : `rgba(100, 116, 139, ${{st.alpha * 0.35}})`;
        ctx.beginPath();
        ctx.arc(st.x * width, st.y * height, st.r, 0, Math.PI * 2);
        ctx.fill();
      }});

      const cosY = Math.cos(rotY), sinY = Math.sin(rotY);
      const cosX = Math.cos(rotX), sinX = Math.sin(rotX);

      // Chiếu tọa độ node
      const nodes = graphData.nodes;
      for (let i = 0; i < nodes.length; i++) {{
        projectNode(nodes[i], cosY, sinY, cosX, sinX);
      }}

      // Vẽ cạnh liên kết
      const edges = graphData.edges;
      for (let i = 0; i < edges.length; i++) {{
        const e = edges[i];
        if (e.type === 'relation' && !showLinks) continue;

        const s = nodeMap[e.source];
        const t = nodeMap[e.target];
        if (!s || !t) continue;

        const isHighlight = (hoveredNode && (hoveredNode.id === s.id || hoveredNode.id === t.id)) ||
                            (selectedNode && (selectedNode.id === s.id || selectedNode.id === t.id));

        const isSearchConnected = searchQuery && (
          (s.label.toLowerCase().includes(searchQuery)) ||
          (t.label.toLowerCase().includes(searchQuery))
        );

        const isClusterMatch = (activeCluster === 'all') ||
                               (s.cluster === activeCluster && t.cluster === activeCluster) ||
                               (s.type === 'cluster' && s.cluster === activeCluster) ||
                               (t.type === 'cluster' && t.cluster === activeCluster) ||
                               (s.type === 'hub' && (t.cluster === activeCluster || t.id === 'cluster-' + activeCluster));

        if ((searchQuery && !isSearchConnected && !isHighlight) || (!isClusterMatch && !isHighlight)) {{
          // Làm mờ tối đa các đường không liên quan khi đang tìm kiếm hoặc lọc cụm
          ctx.strokeStyle = isDark ? 'rgba(148, 163, 184, 0.02)' : 'rgba(148, 163, 184, 0.04)';
          ctx.lineWidth = 0.3;
        }} else if (isSearchConnected) {{
          // Đường nối đến kết quả tìm kiếm sáng rực màu hồng neon
          ctx.strokeStyle = '#FF007F';
          ctx.lineWidth = 2.4;
        }} else if (e.type === 'relation') {{
          // Liên kết nghiệp vụ chéo
          if (isHighlight) {{
            ctx.strokeStyle = '#EA580C';
            ctx.lineWidth = 2.6;
          }} else {{
            ctx.strokeStyle = isDark ? 'rgba(245, 158, 11, 0.30)' : 'rgba(217, 119, 6, 0.55)';
            ctx.lineWidth = isDark ? 1.2 : 1.6;
          }}
        }} else if (e.type === 'hub-link') {{
          ctx.strokeStyle = isDark
            ? (e.color ? e.color + '55' : 'rgba(255, 255, 255, 0.35)')
            : 'rgba(37, 99, 235, 0.45)';
          ctx.lineWidth = 2.0;
        }} else if (e.type === 'cluster-ring') {{
          ctx.strokeStyle = isDark ? 'rgba(51, 65, 85, 0.35)' : 'rgba(148, 163, 184, 0.45)';
          ctx.lineWidth = 1.0;
        }} else {{
          // cluster-item
          if (isHighlight) {{
            ctx.strokeStyle = isDark ? '#FFF' : '#1D4ED8';
            ctx.lineWidth = 1.8;
          }} else {{
            ctx.strokeStyle = isDark
              ? (s.color ? s.color + '22' : 'rgba(148, 163, 184, 0.08)')
              : (s.color ? s.color + '33' : 'rgba(100, 116, 139, 0.22)');
            ctx.lineWidth = 0.8;
          }}
        }}

        ctx.beginPath();
        ctx.moveTo(s.px, s.py);
        ctx.lineTo(t.px, t.py);
        ctx.stroke();
      }}

      // Sắp xếp thứ tự Z
      const sorted = nodes.slice().sort((a, b) => b.pz - a.pz);

      for (let i = 0; i < sorted.length; i++) {{
        const n = sorted[i];
        n.badgeBounds = null;
        const isHover = hoveredNode && hoveredNode.id === n.id;
        const isSelect = selectedNode && selectedNode.id === n.id;
        const isMatchSearch = searchQuery && n.label.toLowerCase().includes(searchQuery);
        const isClusterNodeMatch = (activeCluster === 'all') || (n.cluster === activeCluster) || (n.id === 'cluster-' + activeCluster) || (n.type === 'hub');
        const isDimmed = (searchQuery && !isMatchSearch && n.type !== 'hub' && n.type !== 'cluster') || (!isClusterNodeMatch);

        // Vầng sáng Aura
        if (isMatchSearch) {{
          const glowR = n.pr * 5.2;
          const glow = ctx.createRadialGradient(n.px, n.py, n.pr * 0.2, n.px, n.py, glowR);
          glow.addColorStop(0, '#FF007F');
          glow.addColorStop(0.35, 'rgba(255, 0, 127, 0.65)');
          glow.addColorStop(0.7, 'rgba(255, 0, 127, 0.18)');
          glow.addColorStop(1, 'transparent');
          ctx.fillStyle = glow;
          ctx.beginPath();
          ctx.arc(n.px, n.py, glowR, 0, Math.PI * 2);
          ctx.fill();

          ctx.strokeStyle = '#FF007F';
          ctx.lineWidth = 2.4;
          ctx.beginPath();
          ctx.arc(n.px, n.py, n.pr * 2.2, 0, Math.PI * 2);
          ctx.stroke();
        }} else if (!isDimmed && (n.type === 'hub' || n.type === 'cluster' || isHover || isSelect)) {{
          const glowR = n.pr * (isHover || isSelect ? 3.8 : 2.4);
          const glow = ctx.createRadialGradient(n.px, n.py, n.pr * 0.2, n.px, n.py, glowR);
          glow.addColorStop(0, isDark ? (n.color || '#F59E0B') : (n.color || '#2563EB'));
          glow.addColorStop(1, 'transparent');
          ctx.fillStyle = glow;
          ctx.beginPath();
          ctx.arc(n.px, n.py, glowR, 0, Math.PI * 2);
          ctx.fill();
        }}

        // Điểm tròn Node
        if (isMatchSearch) {{
          ctx.fillStyle = '#FFFFFF';
          ctx.beginPath();
          ctx.arc(n.px, n.py, n.pr * 1.6, 0, Math.PI * 2);
          ctx.fill();
          ctx.strokeStyle = '#FF007F';
          ctx.lineWidth = 2.8;
          ctx.stroke();
        }} else if (isDimmed) {{
          ctx.fillStyle = isDark ? 'rgba(100, 116, 139, 0.12)' : 'rgba(203, 213, 225, 0.35)';
          ctx.beginPath();
          ctx.arc(n.px, n.py, n.pr * 0.75, 0, Math.PI * 2);
          ctx.fill();
        }} else {{
          if (n.type === 'hub') {{
            ctx.fillStyle = isDark ? '#FFF' : '#1E3A8A';
          }} else if (isHover || isSelect) {{
            ctx.fillStyle = isDark ? '#FFF' : '#1D4ED8';
          }} else {{
            ctx.fillStyle = n.color;
          }}
          ctx.beginPath();
          ctx.arc(n.px, n.py, n.pr, 0, Math.PI * 2);
          ctx.fill();

          if (!isDark && n.type !== 'hub') {{
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
            ctx.lineWidth = 1.2;
            ctx.stroke();
          }}
        }}

        // Nhãn tên file có hộp thẻ Pill Badge nổi bật trên nền web (Nền trắng ngọc, chữ xanh Navy)
        const showLabel = isMatchSearch || (!searchQuery && (showAllLabels || n.type === 'hub' || n.type === 'cluster' || isHover || isSelect));
        if (showLabel) {{
          const isSpecial = n.type === 'hub' || n.type === 'cluster';
          const fontSize = Math.max(10, Math.min(15, Math.round((isMatchSearch ? 13 : (n.type === 'hub' ? 14 : (n.type === 'cluster' ? 12 : 11))) * n.pscale)));
          
          ctx.save();
          ctx.font = `${{(isHover || isSelect || isSpecial || isMatchSearch) ? '700 ' : '600 '}}${{fontSize}}px 'Plus Jakarta Sans', sans-serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';

          // Rút gọn khi ở xa
          let txt = n.label;
          if (n.type === 'doc' && !isHover && !isSelect && !isMatchSearch) {{
            if (n.pscale < 0.75 && txt.length > 25) {{
              txt = txt.slice(0, 23) + '..';
            }} else if (txt.length > 40) {{
              txt = txt.slice(0, 38) + '..';
            }}
          }}

          const textWidth = ctx.measureText(txt).width;
          const padX = 8, padY = 4.5;
          const badgeW = textWidth + padX * 2;
          const badgeH = fontSize + padY * 2;
          const badgeX = n.px - badgeW / 2;
          const badgeY = n.py + n.pr + (isMatchSearch ? 10 : 7);
          n.badgeBounds = {{ x: badgeX, y: badgeY, w: badgeW, h: badgeH }};

          // Vẽ thẻ nền (Pill Badge) bo góc
          ctx.beginPath();
          if (ctx.roundRect) {{
            ctx.roundRect(badgeX, badgeY, badgeW, badgeH, 6);
          }} else {{
            ctx.rect(badgeX, badgeY, badgeW, badgeH);
          }}

          if (isMatchSearch) {{
            ctx.fillStyle = '#FF007F';
            ctx.fill();
            ctx.fillStyle = '#FFFFFF';
          }} else if (isHover || isSelect) {{
            ctx.fillStyle = isDark ? '#2563EB' : '#1D4ED8';
            ctx.fill();
            ctx.fillStyle = '#FFFFFF';
          }} else if (n.type === 'hub') {{
            ctx.fillStyle = isDark ? '#1E293B' : '#1E3A8A';
            ctx.fill();
            ctx.fillStyle = '#FFFFFF';
          }} else if (n.type === 'cluster') {{
            ctx.fillStyle = isDark ? 'rgba(15, 23, 42, 0.94)' : 'rgba(255, 255, 255, 0.96)';
            ctx.fill();
            ctx.strokeStyle = n.color || '#2563EB';
            ctx.lineWidth = 1.5;
            ctx.stroke();
            ctx.fillStyle = isDark ? (n.color || '#F8FAFC') : (n.color || '#1E3A8A');
          }} else {{
            // File PDF: Nền trắng ngọc, viền xanh nhẹ, chữ xanh Navy nổi bật!
            ctx.fillStyle = isDark ? 'rgba(15, 23, 42, 0.90)' : 'rgba(255, 255, 255, 0.95)';
            ctx.fill();
            ctx.strokeStyle = isDark ? 'rgba(148, 163, 184, 0.25)' : 'rgba(37, 99, 235, 0.28)';
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.fillStyle = isDark ? '#E2E8F0' : '#1E3A8A';
          }}

          ctx.fillText(txt, n.px, badgeY + badgeH / 2);
          ctx.restore();
        }}
      }}

      ctx.restore();
      requestAnimationFrame(renderFrame);
    }}
    requestAnimationFrame(renderFrame);

    // 4. SỰ KIỆN CHUỘT
    canvas.addEventListener('mousedown', e => {{
      isDragging = true;
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
    }});

    window.addEventListener('mousemove', e => {{
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      if (isDragging) {{
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        rotY += dx * 0.0035;
        rotX += dy * 0.0035;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        return;
      }}

      // Hit testing: kiểm tra cả hình tròn nút và toàn bộ diện tích thẻ chữ (Pill Badge)
      hoveredNode = graphData.nodes.find(n => {{
        if (Math.hypot(mx - n.px, my - n.py) <= n.pr + 5) return true;
        if (n.badgeBounds) {{
          const b = n.badgeBounds;
          if (mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h) return true;
        }}
        return false;
      }}) || null;
      canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
    }});

    window.addEventListener('mouseup', () => {{ isDragging = false; }});

    canvas.addEventListener('wheel', e => {{
      e.preventDefault();
      zoom += e.deltaY * -0.0012;
      zoom = Math.min(Math.max(0.4, zoom), 2.5);
    }}, {{ passive: false }});

    canvas.addEventListener('click', () => {{
      if (hoveredNode) {{
        showNodeDetails(hoveredNode);
      }}
    }});

    // 4.1. SỰ KIỆN CẢM ỨNG CHO ĐIỆN THOẠI & MÁY TÍNH BẢNG (TOUCH GESTURES)
    let touchStartX = 0;
    let touchStartY = 0;
    let touchStartTime = 0;
    let initialPinchDist = null;
    let initialZoom = 1.0;

    canvas.addEventListener('touchstart', e => {{
      if (e.touches.length === 1) {{
        isDragging = true;
        lastMouseX = e.touches[0].clientX;
        lastMouseY = e.touches[0].clientY;
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        touchStartTime = Date.now();
      }} else if (e.touches.length === 2) {{
        isDragging = false;
        initialPinchDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        initialZoom = zoom;
      }}
    }}, {{ passive: false }});

    canvas.addEventListener('touchmove', e => {{
      e.preventDefault();
      if (e.touches.length === 1 && isDragging) {{
        const dx = e.touches[0].clientX - lastMouseX;
        const dy = e.touches[0].clientY - lastMouseY;
        rotY += dx * 0.0045;
        rotX += dy * 0.0045;
        lastMouseX = e.touches[0].clientX;
        lastMouseY = e.touches[0].clientY;
      }} else if (e.touches.length === 2 && initialPinchDist) {{
        const currentDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        const factor = currentDist / initialPinchDist;
        zoom = Math.min(Math.max(0.4, initialZoom * factor), 2.5);
      }}
    }}, {{ passive: false }});

    canvas.addEventListener('touchend', e => {{
      isDragging = false;
      initialPinchDist = null;

      // Xử lý chạm nhanh (Tap) vào nút văn bản
      if (e.changedTouches.length === 1) {{
        const touch = e.changedTouches[0];
        const elapsed = Date.now() - touchStartTime;
        const dist = Math.hypot(touch.clientX - touchStartX, touch.clientY - touchStartY);
        if (elapsed < 350 && dist < 15) {{
          const rect = canvas.getBoundingClientRect();
          const tx = touch.clientX - rect.left;
          const ty = touch.clientY - rect.top;

          const tappedNode = graphData.nodes.find(n => {{
            if (Math.hypot(tx - n.px, ty - n.py) <= n.pr + 12) return true;
            if (n.badgeBounds) {{
              const b = n.badgeBounds;
              if (tx >= b.x - 4 && tx <= b.x + b.w + 4 && ty >= b.y - 4 && ty <= b.y + b.h + 4) return true;
            }}
            return false;
          }});

          if (tappedNode) {{
            showNodeDetails(tappedNode);
          }} else {{
            if (drawer.classList.contains('open')) {{
              drawer.classList.remove('open');
              selectedNode = null;
            }}
          }}
        }}
      }}
    }});

    function showNodeDetails(node) {{
      selectedNode = node;
      dBadge.textContent = node.type === 'hub' ? 'KHO TỔNG' : (node.type === 'cluster' ? 'CỤM CHỦ ĐỀ' : 'VĂN BẢN PDF');
      dBadge.style.color = node.color;
      dTitle.textContent = node.label;
      dSoHieu.textContent = node.soHieu || '--';
      dSize.textContent = node.size || '--';
      dDate.textContent = node.mtime || '--';
      dPath.textContent = node.relPath || 'Gốc';
      dDesc.textContent = node.desc || '';

      if (node.type === 'doc' && node.relPath) {{
        dSmartOpenBtn.style.display = 'flex';
        dActionHint.style.display = 'block';
      }} else {{
        dSmartOpenBtn.style.display = 'none';
        dActionHint.style.display = 'none';
      }}

      drawer.classList.add('open');
    }}

    function clearSearchState() {{
      if (searchQuery) {{
        searchQuery = '';
        if (searchInput) searchInput.value = '';
      }}
    }}

    dCloseBtn.onclick = () => {{
      drawer.classList.remove('open');
      selectedNode = null;
    }};

    dSmartOpenBtn.onclick = () => {{
      smartOpenDoc(selectedNode);
    }};

    canvas.addEventListener('dblclick', () => {{
      if (hoveredNode && hoveredNode.type === 'doc') {{
        showNodeDetails(hoveredNode);
        smartOpenDoc(hoveredNode);
      }} else if (!hoveredNode) {{
        // Bấm đúp vào nền để về góc nhìn đầu (đúng theo hướng dẫn chân trang)
        rotX = -0.18;
        rotY = 0;
        zoom = 1.0;
        activeCluster = 'all';
        document.querySelectorAll('.legend-item').forEach(el => {{
          el.classList.toggle('active', el.getAttribute('data-cluster') === 'all');
        }});
        showToast('🎯 Góc nhìn gốc', 'Đã đặt lại góc nhìn ban đầu toàn bộ kho văn bản.', 2000);
      }}
    }});

    // 5. CÁC NÚT ĐIỀU KHIỂN HUD
    btnToggleLabels.onclick = () => {{
      showAllLabels = !showAllLabels;
      btnToggleLabels.classList.toggle('active', showAllLabels);
    }};

    btnToggleRotate.onclick = () => {{
      autoRotate = !autoRotate;
      btnToggleRotate.classList.toggle('active', autoRotate);
    }};

    btnToggleLinks.onclick = () => {{
      showLinks = !showLinks;
      btnToggleLinks.classList.toggle('active', showLinks);
    }};

    btnResetView.onclick = () => {{
      rotX = -0.18;
      rotY = 0;
      zoom = 1.0;
    }};

    btnToggleFullscreen.onclick = () => {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen().catch(err => {{
          console.warn('Lỗi toàn màn hình:', err);
        }});
      }} else {{
        if (document.exitFullscreen) {{
          document.exitFullscreen();
        }}
      }}
    }};

    document.addEventListener('fullscreenchange', () => {{
      const isFull = !!document.fullscreenElement;
      btnToggleFullscreen.classList.toggle('active', isFull);
      btnToggleFullscreen.innerHTML = isFull ? '<span>🗗</span> Thu Nhỏ' : '<span>⛶</span> Toàn Màn Hình';
      setTimeout(resize, 100);
    }});

    searchInput.addEventListener('input', e => {{
      searchQuery = e.target.value.trim().toLowerCase();
    }});

    // 6. PHÍM TẮT THÔNG MINH (KEYBOARD SHORTCUTS)
    window.addEventListener('keydown', e => {{
      if (document.activeElement === searchInput) {{
        if (e.key === 'Escape') {{
          searchInput.blur();
          clearSearchState();
        }}
        return;
      }}

      if (e.key === '/' || (e.ctrlKey && e.key.toLowerCase() === 'k')) {{
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }} else if (e.code === 'Space') {{
        e.preventDefault();
        btnToggleRotate.click();
      }} else if (e.key === 'Escape') {{
        drawer.classList.remove('open');
        selectedNode = null;
        clearSearchState();
      }} else if (e.key.toLowerCase() === 'l') {{
        btnToggleLabels.click();
      }} else if (e.key.toLowerCase() === 'm') {{
        btnToggleLinks.click();
      }} else if (e.key.toLowerCase() === 't') {{
        btnToggleTheme.click();
      }} else if (e.key.toLowerCase() === 'r') {{
        btnResetView.click();
      }} else if (e.key.toLowerCase() === 'f') {{
        btnToggleFullscreen.click();
      }}
    }});
  </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Đã xuất bản đồ tri thức thành công tại: {output_path}")

if __name__ == '__main__':
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(current_script_dir):
        pdf_dir = current_script_dir
    else:
        pdf_dir = r'E:\GOOGLEDRIVER3\14. Văn bản nghiệp vụ\FILE PDF'
    out_html = os.path.join(pdf_dir, 'Ban_Do_Tri_Thuc_Van_Ban_PDF.html')
    data = scan_pdf_folder(pdf_dir)
    generate_html(data, out_html)

    # Xuất bản file index.html sẵn sàng để đẩy lên GitHub Pages
    index_html = os.path.join(pdf_dir, 'index.html')
    with open(index_html, 'w', encoding='utf-8') as f:
        with open(out_html, 'r', encoding='utf-8') as src:
            f.write(src.read())
    print(f"Đã tạo tệp index.html để sẵn sàng xuất bản GitHub tại: {index_html}")
