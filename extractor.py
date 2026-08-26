import cv2
import pytesseract
import numpy as np
import json
import math
import argparse
from pytesseract import Output

def extract_graph(image_path, output_json, debug=False):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image at {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # 1. Text detection
    d = pytesseract.image_to_data(gray, output_type=Output.DICT, config='--psm 11')
    texts = []
    for i in range(len(d['text'])):
        if int(d['conf'][i]) > 40:
            text = d['text'][i].strip()
            if text:
                x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
                texts.append({
                    'text': text,
                    'box': (x, y, w, h),
                    'center': (x + w/2, y + h/2)
                })
                
    if debug:
        img_debug = img.copy()
        for t in texts:
            x, y, w, h = t['box']
            cv2.rectangle(img_debug, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img_debug, t['text'], (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imwrite("debug_texts.png", img_debug)

    # 2. Node detection
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    nodes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 10 < area < 500:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0: continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            if circularity > 0.5:  # Relaxed circularity for nodes
                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    nodes.append((cx, cy, cv2.boundingRect(cnt)))

    # If no dots detected, treat text as nodes
    if len(nodes) == 0:
        for t in texts:
            if t['text'].isalpha() and len(t['text']) <= 2:
                nodes.append((t['center'][0], t['center'][1], t['box']))

    node_labels = []
    used_texts = set()
    for i, (nx, ny, box) in enumerate(nodes):
        closest_text = None
        min_dist = float('inf')
        for j, t in enumerate(texts):
            if j in used_texts: continue
            dist = math.hypot(nx - t['center'][0], ny - t['center'][1])
            if dist < 60 and dist < min_dist:
                min_dist = dist
                closest_text = j
                
        label = f"node_{i}"
        if closest_text is not None:
            text_val = texts[closest_text]['text']
            text_val = ''.join(c for c in text_val if c.isalnum())
            if text_val:
                label = text_val
                used_texts.add(closest_text)
                
        node_labels.append({'id': label, 'x': nx, 'y': ny, 'box': box})

    if debug:
        img_debug_nodes = img.copy()
        for n in node_labels:
            cv2.circle(img_debug_nodes, (int(n['x']), int(n['y'])), 5, (0, 0, 255), -1)
            cv2.putText(img_debug_nodes, n['id'], (int(n['x'])+10, int(n['y'])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.imwrite("debug_nodes.png", img_debug_nodes)

    # 3. Edge detection
    lines_img = thresh.copy()
    for t in texts:
        x, y, w, h = t['box']
        cv2.rectangle(lines_img, (x, y), (x+w, y+h), 0, -1)
        
    lines_detected = cv2.HoughLinesP(lines_img, 1, np.pi/180, threshold=40, minLineLength=30, maxLineGap=50)
    
    edges = []
    if lines_detected is not None:
        for line in lines_detected:
            x1, y1, x2, y2 = line.flatten()[:4]
            if not node_labels: continue
            node_start = min(node_labels, key=lambda n: math.hypot(x1 - n['x'], y1 - n['y']))
            node_end = min(node_labels, key=lambda n: math.hypot(x2 - n['x'], y2 - n['y']))
            
            if node_start and node_end and node_start['id'] != node_end['id']:
                d1 = math.hypot(x1 - node_start['x'], y1 - node_start['y'])
                d2 = math.hypot(x2 - node_end['x'], y2 - node_end['y'])
                if d1 < 100 and d2 < 100:
                    edge = {'source': node_start['id'], 'target': node_end['id']}
                    
                    if not any((e['source'] == edge['source'] and e['target'] == edge['target']) or 
                               (e['source'] == edge['target'] and e['target'] == edge['source']) for e in edges):
                        edges.append(edge)

    if debug:
        img_debug_edges = img.copy()
        for e in edges:
            n1 = next(n for n in node_labels if n['id'] == e['source'])
            n2 = next(n for n in node_labels if n['id'] == e['target'])
            cv2.line(img_debug_edges, (int(n1['x']), int(n1['y'])), (int(n2['x']), int(n2['y'])), (255, 0, 0), 2)
            if 'weight' in e:
                mx, my = int((n1['x'] + n2['x'])/2), int((n1['y'] + n2['y'])/2)
                cv2.putText(img_debug_edges, e['weight'], (mx, my), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.imwrite("debug_edges.png", img_debug_edges)

    graph_data = {'nodes': [n['id'] for n in node_labels], 'edges': edges}
    with open(output_json, 'w') as f:
        json.dump(graph_data, f, indent=4)
    print(f"Graph extracted to {output_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("output")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    
    import os
    if os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    elif os.path.exists(r'C:\Users\USER\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\USER\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        
    extract_graph(args.image, args.output, args.debug)
