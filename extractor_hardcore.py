import cv2
import numpy as np
import json
import math
import argparse
import pytesseract
from pytesseract import Output
from skimage.morphology import skeletonize
from skimage.measure import label, regionprops
from scipy.spatial.distance import cdist

def angle_between(v1, v2):
    dot = np.dot(v1, v2)
    norm = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm == 0: return 0
    cos_theta = max(min(dot / norm, 1.0), -1.0)
    return math.degrees(math.acos(cos_theta))

def extract_hardcore(image_path, output_json, debug=True):
    img = cv2.imread(image_path)
    if img is None: raise ValueError("Image not found")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # 1. OCR for labels
    d = pytesseract.image_to_data(gray, output_type=Output.DICT, config='--psm 11')
    texts = []
    for i in range(len(d['text'])):
        if int(d['conf'][i]) > 30:
            text = d['text'][i].strip()
            text = ''.join(c for c in text if c.isalnum())
            if text:
                x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
                texts.append({'text': text, 'box': (x,y,w,h), 'cx': x+w/2, 'cy': y+h/2})
                
    # 2. Node Detection (Solid Circles)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    nodes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 10 < area < 1000:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter > 0:
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0 and (area / hull_area) > 0.8 and circularity > 0.6:
                    M = cv2.moments(cnt)
                    if M['m00'] != 0:
                        cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
                        nodes.append({'id': f"node_{len(nodes)}", 'x': cx, 'y': cy, 'r': math.sqrt(area/math.pi)})

    # Assign text to nodes
    for n in nodes:
        closest = None
        min_d = float('inf')
        for t in texts:
            d_dist = math.hypot(n['x'] - t['cx'], n['y'] - t['cy'])
            if d_dist < 40 and d_dist < min_d:
                min_d = d_dist
                closest = t['text']
        if closest: n['id'] = closest

    # 3. Clean up image for skeleton
    lines_only = thresh.copy()
    for n in nodes:
        cv2.circle(lines_only, (n['x'], n['y']), int(n['r'])+4, 0, -1)
    for t in texts:
        x,y,w,h = t['box']
        cv2.rectangle(lines_only, (x-2, y-2), (x+w+2, y+h+2), 0, -1)
        
    # Skeletonize
    skeleton = skeletonize(lines_only > 0).astype(np.uint8) * 255
    
    # 4. Junction Detection (Hit-or-Miss / neighbor count)
    kernel = np.array([[1, 1, 1], [1, 10, 1], [1, 1, 1]], dtype=np.uint8)
    filtered = cv2.filter2D(skeleton // 255, -1, kernel)
    junctions_mask = (filtered >= 13).astype(np.uint8) * 255 # 10 (center) + at least 3 neighbors
    junctions_mask = cv2.dilate(junctions_mask, np.ones((3,3), np.uint8), iterations=1)
    
    # 5. Extract Segments
    segments_mask = cv2.subtract(skeleton, junctions_mask)
    num_labels, labels_im, stats, centroids = cv2.connectedComponentsWithStats(segments_mask, connectivity=8)
    
    segments = []
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] < 5: continue
        pts = np.argwhere(labels_im == i)
        # Sort points to form a sequence. (Very naive: sort by x, or find endpoints. For robustness we fit PCA or just use endpoints)
        # Actually, simpler: find pixels with 1 neighbor within the component
        comp_mask = (labels_im == i).astype(np.uint8)
        comp_filtered = cv2.filter2D(comp_mask, -1, kernel)
        ends = np.argwhere((comp_filtered == 11) & (comp_mask == 1))
        
        if len(ends) >= 2:
            # Pick two endpoints furthest apart
            end1, end2 = ends[0], ends[-1]
            if len(ends) > 2:
                dists = cdist(ends, ends)
                idx = np.unravel_index(np.argmax(dists), dists.shape)
                end1, end2 = ends[idx[0]], ends[idx[1]]
                
            segments.append({
                'pts': pts,
                'end1': (end1[1], end1[0]), # x, y
                'end2': (end2[1], end2[0])
            })
            
    # 6. Junction Routing
    junc_labels, junc_im = cv2.connectedComponents(junctions_mask)
    merged_segments = list(segments)
    
    for j_id in range(1, junc_labels):
        j_pts = np.argwhere(junc_im == j_id)
        if len(j_pts) == 0: continue
        jx, jy = np.mean(j_pts[:, 1]), np.mean(j_pts[:, 0])
        
        # Find segment ends near this junction
        touching = []
        for s_idx, s in enumerate(merged_segments):
            if s is None: continue
            d1 = math.hypot(s['end1'][0] - jx, s['end1'][1] - jy)
            d2 = math.hypot(s['end2'][0] - jx, s['end2'][1] - jy)
            if d1 < 15: touching.append((s_idx, 'end1', s['end2']))
            elif d2 < 15: touching.append((s_idx, 'end2', s['end1']))
            
        if len(touching) >= 2:
            # Pair them up by tangent angle (simplification: vector from junction to other end)
            best_pair = None
            best_angle = 0
            for i in range(len(touching)):
                for j in range(i+1, len(touching)):
                    idx1, type1, other1 = touching[i]
                    idx2, type2, other2 = touching[j]
                    v1 = np.array([other1[0]-jx, other1[1]-jy])
                    v2 = np.array([other2[0]-jx, other2[1]-jy])
                    ang = angle_between(v1, v2)
                    if ang > 135 and ang > best_angle: # Smooth continuation
                        best_angle = ang
                        best_pair = (idx1, type1, idx2, type2)
            
            if best_pair:
                idx1, type1, idx2, type2 = best_pair
                s1, s2 = merged_segments[idx1], merged_segments[idx2]
                new_s = {
                    'pts': np.vstack((s1['pts'], s2['pts'])),
                    'end1': s1['end2'] if type1 == 'end1' else s1['end1'],
                    'end2': s2['end2'] if type2 == 'end1' else s2['end1']
                }
                merged_segments[idx1] = None
                merged_segments[idx2] = None
                merged_segments.append(new_s)

    final_segments = [s for s in merged_segments if s is not None]

    # 7. Map segments to graph nodes
    edges = []
    for s in final_segments:
        e1, e2 = s['end1'], s['end2']
        n1 = min(nodes, key=lambda n: math.hypot(n['x']-e1[0], n['y']-e1[1]), default=None)
        n2 = min(nodes, key=lambda n: math.hypot(n['x']-e2[0], n['y']-e2[1]), default=None)
        
        if n1 and n2 and n1['id'] != n2['id']:
            if math.hypot(n1['x']-e1[0], n1['y']-e1[1]) < 30 and math.hypot(n2['x']-e2[0], n2['y']-e2[1]) < 30:
                edge = {'source': n1['id'], 'target': n2['id']}
                if not any((e['source']==edge['source'] and e['target']==edge['target']) or 
                           (e['source']==edge['target'] and e['target']==edge['source']) for e in edges):
                    edges.append(edge)

    if debug:
        img_debug = img.copy()
        for s in final_segments:
            cv2.line(img_debug, s['end1'], s['end2'], (255, 0, 0), 1)
        for e in edges:
            n1 = next(n for n in nodes if n['id'] == e['source'])
            n2 = next(n for n in nodes if n['id'] == e['target'])
            cv2.line(img_debug, (n1['x'], n1['y']), (n2['x'], n2['y']), (0, 255, 0), 2)
        for n in nodes:
            cv2.circle(img_debug, (n['x'], n['y']), 5, (0, 0, 255), -1)
            cv2.putText(img_debug, n['id'], (n['x']+10, n['y']), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.imwrite("debug_hardcore.png", img_debug)

    graph_data = {'nodes': [n['id'] for n in nodes], 'edges': edges}
    with open(output_json, 'w') as f:
        json.dump(graph_data, f, indent=4)
    print(f"Graph extracted to {output_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("output")
    args = parser.parse_args()
    
    import os
    if os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    elif os.path.exists(r'C:\Users\USER\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\USER\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        
    extract_hardcore(args.image, args.output)
