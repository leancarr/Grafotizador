import cv2
import numpy as np
import math
import json
import argparse

def extract_graph_perfect_edges(image_path, output_json, debug=True):
    img = cv2.imread(image_path)
    if img is None: raise ValueError("Could not load image")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # 1. Detect Nodes (solid black dots)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    nodes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 10 < area < 1000:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0: continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            if hull_area > 0:
                solidity = area / hull_area
                if circularity > 0.6 and solidity > 0.8:  # Solid dots
                    M = cv2.moments(cnt)
                    if M['m00'] != 0:
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])
                        nodes.append({'id': f"node_{len(nodes)}", 'x': cx, 'y': cy})
                    
    # 2. Edge Detection by Pixel Sampling
    # For every pair of nodes, we check if there's a continuous black line connecting them.
    edges = []
    
    # Create a mask of just the lines (dilate slightly to be forgiving)
    kernel = np.ones((3,3), np.uint8)
    lines_mask = cv2.dilate(thresh, kernel, iterations=1)
    
    if debug:
        img_debug = img.copy()
        
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            n1 = nodes[i]
            n2 = nodes[j]
            
            # Create a blank mask for this specific line segment
            line_mask = np.zeros_like(thresh)
            cv2.line(line_mask, (n1['x'], n1['y']), (n2['x'], n2['y']), 255, thickness=2)
            
            # To avoid the node blobs themselves falsely increasing the score,
            # we ignore pixels too close to the node centers
            cv2.circle(line_mask, (n1['x'], n1['y']), 15, 0, -1)
            cv2.circle(line_mask, (n2['x'], n2['y']), 15, 0, -1)
            
            # Calculate how many pixels of this line segment actually fall on black pixels in the image
            total_line_pixels = cv2.countNonZero(line_mask)
            if total_line_pixels == 0: continue
            
            overlap = cv2.bitwise_and(lines_mask, line_mask)
            overlap_pixels = cv2.countNonZero(overlap)
            
            coverage = overlap_pixels / total_line_pixels
            
            # If more than 85% of the line segment is black, the edge exists!
            if coverage > 0.85:
                edges.append({'source': n1['id'], 'target': n2['id']})
                if debug:
                    cv2.line(img_debug, (n1['x'], n1['y']), (n2['x'], n2['y']), (0, 255, 0), 2)
                    
    if debug:
        for n in nodes:
            cv2.circle(img_debug, (n['x'], n['y']), 5, (0, 0, 255), -1)
            cv2.putText(img_debug, n['id'], (n['x']+10, n['y']), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.imwrite("debug_perfect.png", img_debug)
        print("Debug image saved as debug_perfect.png")
        
    graph_data = {'nodes': [n['id'] for n in nodes], 'edges': edges}
    with open(output_json, 'w') as f:
        json.dump(graph_data, f, indent=4)
    print(f"Graph extracted to {output_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("output")
    args = parser.parse_args()
    extract_graph_perfect_edges(args.image, args.output)
