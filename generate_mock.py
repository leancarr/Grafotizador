import cv2
import numpy as np

def create_mock_graph():
    # Create white image
    img = np.ones((500, 500, 3), dtype=np.uint8) * 255
    
    # Draw nodes for Graph (a)
    nodes = {'w': (100, 400), 'x': (200, 400), 'y': (300, 400), 'z': (400, 400), 't': (250, 100)}
    for label, (x, y) in nodes.items():
        cv2.circle(img, (x, y), 10, (0, 0, 0), -1)
        cv2.putText(img, label, (x - 20, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
    # Draw edges
    edges = [('w', 'x'), ('x', 'y'), ('y', 'z'), ('t', 'x'), ('t', 'y'), ('t', 'z')]
    for n1, n2 in edges:
        x1, y1 = nodes[n1]
        x2, y2 = nodes[n2]
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 2)
        
    cv2.imwrite('mock_graph.png', img)
    print("Mock graph created as mock_graph.png")

if __name__ == '__main__':
    create_mock_graph()
