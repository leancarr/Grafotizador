import cv2
import numpy as np

def create_mock_graph():
    # Create white image
    img = np.ones((500, 500, 3), dtype=np.uint8) * 255
    
    # Draw nodes
    nodes = {'a': (100, 100), 'b': (400, 100), 'u': (100, 400), 'v': (400, 400)}
    for label, (x, y) in nodes.items():
        cv2.circle(img, (x, y), 10, (0, 0, 0), -1)
        cv2.putText(img, label, (x - 20, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
    # Draw edges
    edges = [('a', 'b', '10'), ('a', 'u', '5'), ('b', 'v', '8')]
    for n1, n2, weight in edges:
        x1, y1 = nodes[n1]
        x2, y2 = nodes[n2]
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 2)
        # Draw weight
        mx, my = (x1 + x2)//2, (y1 + y2)//2
        cv2.putText(img, weight, (mx, my - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
    cv2.imwrite('mock_graph.png', img)
    print("Mock graph created as mock_graph.png")

if __name__ == '__main__':
    create_mock_graph()
